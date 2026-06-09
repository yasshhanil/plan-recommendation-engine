import base64
import json
import logging

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import AppUser, AuthToken
from .decorators import require_api_key

logger = logging.getLogger(__name__)


def _user_response(user, token):
    return JsonResponse({
        'token': str(token.token),
        'user': {'id': user.id, 'email': user.email, 'name': user.name, 'city': user.city},
    })


def _authenticate(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token_value = auth_header[len('Bearer '):].strip()
    try:
        return AuthToken.objects.select_related('user').get(token=token_value).user
    except Exception:
        return None


def _get_or_create_user(platform, platform_id, email, name):
    user, created = AppUser.objects.get_or_create(
        platform=platform,
        platform_id=platform_id,
        defaults={'email': email, 'name': name},
    )
    if created:
        logger.info(f'[auth] New user created: {email} via {platform}')
    else:
        logger.info(f'[auth] Existing user signed in: {email} via {platform}')
        if not user.name and name:
            user.name = name
            user.save(update_fields=['name'])
    return user


@csrf_exempt
@require_api_key
def google_auth(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    code = (body.get('code') or '').strip()
    redirect_uri = (body.get('redirect_uri') or '').strip()
    code_verifier = (body.get('code_verifier') or '').strip()
    if not code or not redirect_uri:
        return JsonResponse({'error': 'code and redirect_uri required'}, status=400)

    logger.info(f'[google_auth] Exchanging code for tokens, redirect_uri={redirect_uri}')

    token_data = {
        'code': code,
        'client_id': settings.GOOGLE_IOS_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }
    if code_verifier:
        token_data['code_verifier'] = code_verifier

    try:
        token_resp = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_data,
            timeout=10,
        )
    except requests.RequestException as e:
        logger.error(f'[google_auth] Token exchange request failed: {e}')
        return JsonResponse({'error': 'Could not reach Google'}, status=502)

    if token_resp.status_code != 200:
        logger.error(f'[google_auth] Token exchange failed {token_resp.status_code}: {token_resp.text}')
        return JsonResponse({'error': 'Failed to exchange code'}, status=401)

    access_token = token_resp.json().get('access_token')
    if not access_token:
        logger.error('[google_auth] No access_token in Google token response')
        return JsonResponse({'error': 'No access token in Google response'}, status=401)

    logger.info('[google_auth] Token exchange successful, fetching user info')

    try:
        userinfo_resp = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )
    except requests.RequestException as e:
        logger.error(f'[google_auth] Userinfo request failed: {e}')
        return JsonResponse({'error': 'Could not reach Google'}, status=502)

    if userinfo_resp.status_code != 200:
        logger.error(f'[google_auth] Userinfo fetch failed {userinfo_resp.status_code}: {userinfo_resp.text}')
        return JsonResponse({'error': 'Failed to fetch user info'}, status=401)

    data = userinfo_resp.json()
    platform_id = data.get('sub')
    if not platform_id:
        logger.error('[google_auth] No sub in userinfo response')
        return JsonResponse({'error': 'Could not retrieve Google user info'}, status=401)

    email = data.get('email', '')
    name = data.get('name') or data.get('given_name', '')

    user = _get_or_create_user('google', platform_id, email, name)
    token = AuthToken.objects.create(user=user)
    logger.info(f'[google_auth] Auth successful for {email}')
    return _user_response(user, token)


@csrf_exempt
@require_api_key
def me(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user = _authenticate(request)
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    return JsonResponse({'user': {'id': user.id, 'email': user.email, 'name': user.name, 'city': user.city}})


@csrf_exempt
@require_api_key
def set_city(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user = _authenticate(request)
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    city = (body.get('city') or '').strip()
    user.city = city or None
    user.save(update_fields=['city'])
    logger.info(f'[set_city] {user.email} set city to {user.city!r}')
    return JsonResponse({'success': True, 'city': user.city})


def _decode_apple_payload(identity_token):
    try:
        parts = identity_token.split('.')
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        payload_b64 += '=' * (-len(payload_b64) % 4)
        return json.loads(base64.urlsafe_b64decode(payload_b64))
    except Exception as e:
        logger.error(f'[apple_auth] JWT decode failed: {e}')
        return None


@csrf_exempt
@require_api_key
def apple_auth(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    identity_token = (body.get('identity_token') or '').strip()
    if not identity_token:
        return JsonResponse({'error': 'identity_token required'}, status=400)

    logger.info('[apple_auth] Decoding identity_token')

    payload = _decode_apple_payload(identity_token)
    if not payload:
        return JsonResponse({'error': 'Malformed identity_token'}, status=400)

    if payload.get('iss') != 'https://appleid.apple.com':
        logger.error(f'[apple_auth] Invalid issuer: {payload.get("iss")}')
        return JsonResponse({'error': 'Invalid token issuer'}, status=401)

    platform_id = payload.get('sub')
    if not platform_id:
        logger.error('[apple_auth] No sub in token payload')
        return JsonResponse({'error': 'Could not retrieve Apple user info'}, status=401)

    email = payload.get('email', '')

    full_name = body.get('full_name') or {}
    given = (full_name.get('givenName') or '') if isinstance(full_name, dict) else ''
    family = (full_name.get('familyName') or '') if isinstance(full_name, dict) else ''
    name = f'{given} {family}'.strip() or email.split('@')[0]

    user = _get_or_create_user('apple', platform_id, email, name)
    token = AuthToken.objects.create(user=user)
    logger.info(f'[apple_auth] Auth successful for {email}')
    return _user_response(user, token)
