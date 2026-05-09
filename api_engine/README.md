# Plan Recommendation Engine API

A FastAPI-based REST API for managing venues, areas, and creating personalized plans.

## Features

- **Venue Management**: CRUD operations for venues with tagging and categorization
- **Area Management**: Manage geographical areas and their venues
- **Plan Creation**: Create and manage personalized plans with multiple venues
- **Search & Discovery**: Search venues by name, location, and categories
- **Recommendations**: Get venue recommendations based on location and preferences
- **RESTful Design**: Clean API design with proper HTTP methods and status codes

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run the API

```bash
# Development mode
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - Health check

### Venues
- `GET /venues` - List venues (with filtering)
- `GET /venues/{id}` - Get specific venue
- `POST /venues` - Create new venue
- `PUT /venues/{id}` - Update venue (not implemented yet)
- `DELETE /venues/{id}` - Delete venue (not implemented yet)

### Areas
- `GET /areas` - List areas
- `GET /areas/{id}` - Get specific area
- `POST /areas` - Create new area

### Plans
- `GET /plans` - List plans (with user filtering)
- `GET /plans/{id}` - Get specific plan
- `POST /plans` - Create new plan

### Search & Recommendations
- `GET /search/venues` - Search venues by name/description
- `GET /recommendations/venues` - Get venue recommendations

## Database Models

### Venue
- Basic information (name, location, rating, price level)
- Structured tags (category, vibe, special, price tags)
- Reviews and photos
- Area association

### Area
- Geographic areas with venues
- Location coordinates
- Active status

### Plan
- User-created plans
- Status tracking (draft, active, completed, cancelled)
- Budget and timing information
- Venue associations

## Request Examples

### Get All Venues
```bash
curl "http://localhost:8000/venues?limit=10&skip=0"
```

### Search Venues
```bash
curl "http://localhost:8000/search/venues?q=cafe&limit=5"
```

### Get Recommendations
```bash
curl "http://localhost:8000/recommendations/venues?latitude=28.6304&longitude=77.2177&radius=5&categories=restaurant,cafe"
```

### Create a Plan
```bash
curl -X POST "http://localhost:8000/plans" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "title": "Weekend Plan",
    "description": "A fun weekend plan",
    "venue_ids": [1, 2, 3]
  }'
```

## Configuration

Key environment variables:

- `DATABASE_URL`: Database connection string
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: false)
- `CORS_ORIGINS`: Allowed CORS origins (default: "*")

## Development

### Project Structure
```
api_engine/
├── main.py              # FastAPI application
├── models.py            # SQLModel definitions
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

### Adding New Endpoints

1. Define models in `models.py`
2. Add endpoint in `main.py`
3. Update documentation

### Database Migrations

The API uses SQLModel with automatic table creation. For production, consider using Alembic for migrations.

## Production Deployment

### Using Docker (recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup

- Use PostgreSQL or MySQL for production database
- Set up proper CORS origins
- Configure reverse proxy (nginx)
- Enable SSL/TLS

## License

[Your License Here]
