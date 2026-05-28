# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Start dev server (http://127.0.0.1:8000)
python manage.py runserver

# Django admin (create superuser first)
python manage.py createsuperuser

# Run tests
python manage.py test recommendations

# Management commands
python manage.py fetch_venues        # Fetch venues from Google Places API
python manage.py upload_venue_images # Upload venue images to GCS
```

## Architecture

This is a **Django 5 REST API** — no DRF, views return `JsonResponse` directly. The sole active Django app is `recommendations/`; `api_engine/` (FastAPI) and `data_population/` are parallel utilities not wired into Django.

### Request flow

`POST /api/template/` is the primary endpoint. It:
1. Calls `select_best_template(input_tags)` in [recommendations/templates.py](recommendations/templates.py) to score 6 predefined templates against user tags
2. Gets a confidence level (`high` / `medium` / `low`) based on score margin
3. Calls `generate_plan_from_template(template_weights, input_tags, area_id)` in [recommendations/functions.py](recommendations/functions.py) which scores every `Venue` in the DB by dot-product against weighted tags and returns the top-N
4. Returns template scores, confidence, and ranked venue list

### Tag system

Tags are stored as JSON on `Venue` (and submitted by clients). Four tag groups defined in [recommendations/constants.py](recommendations/constants.py):

| Group | Examples |
|---|---|
| `category_tags` | cafe, restaurant, bar, activity, shopping |
| `vibe_tags` | cozy, fancy, aesthetic, casual, romantic |
| `special_tags` | date_spot, outdoor, late_night, group_friendly |
| `price_tags` | affordable, moderate, upscale |

`assign_weights(input_tags)` in [recommendations/functions.py](recommendations/functions.py) distributes weight across all tags: selected tags get ~0.3–0.4 each; remaining weight spreads over unselected tags.

### Image pipeline

Venue images are fetched from the Google Places Photos API and cached in GCS bucket `plan-venue-images`. `bulk_upload_venue_images()` deduplicates by `place_id` before uploading. `MEDIA_URL` points to `https://storage.googleapis.com/plan-venue-images/venue_images/`. Requires `gcs-key.json` (service account) at the project root.

### Shareable plan images

`generate_share_image()` in [recommendations/functions.py](recommendations/functions.py) spins up a Playwright browser, renders [recommendations/templates/plan_landing.html](recommendations/templates/plan_landing.html) with venue data, and screenshots it to produce the share image stored in GCS.

### Settings highlights

- **Database**: SQLite (`db.sqlite3`) — no external DB
- **CORS**: All origins allowed (configured for `localhost:3000`)
- **Google Places API key**: loaded from `.env` as `GOOGLE_PLACES_API_KEY`
- **GCS credentials**: `gcs-key.json` at project root (not in `.env`)

## Environment

Copy `.env.example` → `.env` and fill in:

```
GOOGLE_PLACES_API_KEY=...
```

`gcs-key.json` must also be present for any image-related operations.
