# Plan Recommendation Engine

A Django backend that turns a few preferences ("cozy", "romantic", "cafe → bar", "moderate") into a multi-stop outing plan: a sequence of real venues in a neighbourhood, chosen and ordered to fit the mood.

It serves the [Plan mobile app](https://github.com/yasshhanil/plan-recommendation-engine-frontend) (Expo / React Native). It also provides shareable plan landing pages, social share images, and the tooling that collects and tags venues from Google Places.

---

## Features

- **Template-based planning**: user tags are scored against 7 curated outing templates. The best match drives per-stage tag weights, with a confidence level (`high` / `medium` / `low`) based on the score margin.
- **Intent-based planning**: a deterministic mode. The chosen categories are ordered naturally (cafe → activity → restaurant → bar → dessert) and given one per stage.
- **Weighted venue scoring**: venues are scored against weighted tags. Special-tag filtering, energy transitions between stages, and occasional switches to a neighbouring area keep plans varied.
- **Shareable plans**: each saved plan gets a public `/plan/<uuid>/` landing page. Playwright renders a share-card image, which is stored in Google Cloud Storage.
- **Auth**: Google and Apple sign-in, plus email/password with bearer tokens.
- **Venue data pipeline**: management commands fetch venues from Google Places, tag them with rules or Gemini, and cache photos in GCS.
- **Admin & test console**: Django admin for content, plus a `/test/` page for trying plan generation in the browser.

## Tech stack

| Layer | Tools |
|---|---|
| Framework | Django 5 (plain `JsonResponse` views, no DRF) |
| Database | PostgreSQL in production, SQLite locally (via `DATABASE_URL`) |
| Storage | Google Cloud Storage (`django-storages`) |
| External APIs | Google Places API (New), Google Gemini |
| Rendering | Playwright (Chromium) for share images |
| Serving | Gunicorn + WhiteNoise, deployed on Railway (Docker) |

## How a plan is generated

```
tags ──► select_best_template()  ──► score vs. 7 template profiles
                │
                ▼
        get_confidence_level(top score, margin)
                │
     ┌──────────┴───────────┐
   high / medium            low
     │                       │
 template stage weights   assign_weights(tags)
     │                       │
     ▼                       ▼
 generate_plan_from_template / generate_plan
                │
                ▼
   score_venues() per stage → ranked venues in the chosen area
```

**Templates:** `date_night`, `fun_date`, `social_energy`, `easy_living`, `exploration_mode`, `social_cafe_crawl`, `retail_therapy`. Their profiles live in [recommendations/templates.py](recommendations/templates.py). Per-stage weights for 2-stage and 3-stage plans, plus the headline and description copy, live in [recommendations/template_constants.py](recommendations/template_constants.py).

### Tag vocabulary

| Group | Values |
|---|---|
| `category_tags` | cafe, restaurant, dessert, bar, activity, arcade, cinema, park, shopping |
| `vibe_tags` | cozy, fancy, aesthetic, casual, lively, quiet, romantic, trendy, family_friendly |
| `special_tags` | date_spot, group_friendly, quick_stop, late_night, outdoor, indoor |
| `price_tags` | affordable, moderate, upscale |

## Project structure

```
backend/
├── plan_engine/            # Django project (settings, root URLs, WSGI/ASGI)
├── recommendations/        # The main app
│   ├── views.py            # Plan, venue, area, city, share endpoints
│   ├── auth_views.py       # Google / Apple / email auth
│   ├── functions.py        # Scoring, plan generation, share images
│   ├── templates.py        # Template profiles & selection
│   ├── template_constants.py
│   ├── models.py           # Country, City, Area, Venue, Plan, AppUser, ...
│   ├── management/commands # Data pipeline & testing commands
│   └── templates/          # Home, plan landing page, share card, test console
├── Dockerfile
├── Procfile / railway.toml
└── requirements.txt
```

## Getting started

### Prerequisites

- Python 3.11
- A Google Places API key, needed to fetch venues
- A GCS bucket and service-account credentials, needed for images and share cards

### Setup

```bash
git clone https://github.com/yasshhanil/plan-recommendation-engine.git
cd plan-recommendation-engine

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium       # only needed for share-image generation

cp .env.example .env              # then fill in the values below
python manage.py migrate
python manage.py createsuperuser  # optional, for /admin
python manage.py runserver
```

The server runs at `http://127.0.0.1:8000`.

### Environment variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | e.g. `sqlite:///db.sqlite3` locally, or a Postgres URL |
| `DJANGO_SECRET_KEY` | ✅ | Django secret key |
| `API_SECRET_KEY` | ✅ | Shared secret; clients must send it as `X-Api-Key` |
| `DEBUG` | | `True` to enable debug mode (default `False`) |
| `GOOGLE_PLACES_API_KEY` | | For fetching venues and photos |
| `GS_BUCKET_NAME` | | GCS bucket for venue images and share cards |
| `GCS_CREDENTIALS` | | Service-account JSON, as a single-line string |
| `GOOGLE_WEB_CLIENT_ID` / `GOOGLE_WEB_CLIENT_SECRET` | | Google sign-in |
| `GOOGLE_IOS_CLIENT_ID` | | Google sign-in on iOS |
| `GEMINI_API_KEY` | | For `tag_venues_ai` |

## API

All `/api/` endpoints except auth require the `X-Api-Key` header. Endpoints that act on a user also take `Authorization: Bearer <token>`.

### Plans & venues

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/template/` | Template-based plan |
| `POST` | `/api/intent/` | Intent-based (deterministic) plan |
| `GET` | `/api/` | Basic weighted-tag recommendation |
| `POST` | `/api/save-plan/` | Save a plan (creates a share link and image) |
| `GET` | `/api/get-plans/` | List saved plans |
| `POST` | `/api/get-venues/` | Fetch venues by ID |
| `GET` | `/api/get-cities/` | List active cities |
| `GET` | `/api/get-areas/` | List areas in a city |
| `GET` | `/api/preview-card/` | Preview a share card |
| `POST` | `/api/join-waitlist/` | Join the city waitlist |

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/google/` | Sign in with Google |
| `POST` | `/api/auth/apple/` | Sign in with Apple |
| `POST` | `/api/auth/register/` | Email/password registration |
| `POST` | `/api/auth/login/` | Email/password login |
| `GET` | `/api/auth/me/` | Current user |
| `POST` | `/api/auth/set-city/` | Set the user's city |
| `POST` | `/api/auth/delete-account/` | Delete the account |

### Web pages

| Path | Description |
|---|---|
| `/` | Home / landing page |
| `/plan/<uuid>/` | Public page for a shared plan |
| `/test/` | Plan generation test console |
| `/admin/` | Django admin |

### Example request

```bash
curl -X POST http://127.0.0.1:8000/api/template/ \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $API_SECRET_KEY" \
  -d '{
    "tags": {
      "category_tags": ["cafe", "bar"],
      "vibe_tags": ["cozy", "romantic"],
      "special_tags": ["date_spot"],
      "price_tags": ["moderate"]
    },
    "city_id": 1,
    "stages": 2
  }'
```

The response includes `template_id`, `confidence_level`, `all_scores`, and `venue_data`, the ordered list of venues for the plan.

## Data pipeline

The commands below build and maintain the venue database:

```bash
python manage.py add_areas --city london     # seed cities/areas and fetch venues
python manage.py fetch_venues                # fetch venues from Google Places
python manage.py tag_venues                  # rule-based tagging
python manage.py tag_venues_ai               # Gemini-generated summaries & tags
python manage.py refresh_photo_references    # refresh Places photo refs
python manage.py upload_venue_images         # cache venue images in GCS
python manage.py fix_venue_price_tags --dry-run
python manage.py delete_rejected_venues
python manage.py analyze_venues              # data quality report
```

These commands are for testing template selection:

```bash
python manage.py test_template_selection
python manage.py test_template_plan
```

## Running tests

```bash
python manage.py test recommendations
```

## Deployment

The project ships with a `Dockerfile`. It installs dependencies and Playwright Chromium, runs migrations on start, and serves the app with Gunicorn. It is set up for [Railway](https://railway.app) through `railway.toml`. Set the environment variables above in your host's dashboard, and pass the GCS service account as `GCS_CREDENTIALS` rather than as a file.

```bash
docker build -t plan-engine .
docker run -p 8000:8000 --env-file .env plan-engine
```

## Related

- **Mobile app:** [plan-recommendation-engine-frontend](https://github.com/yasshhanil/plan-recommendation-engine-frontend). Built with Expo, React Native, Tamagui, React Query and Zustand.
