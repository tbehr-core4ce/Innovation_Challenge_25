# 1. Start PostgreSQL with PostGIS
cd backend
docker-compose up -d

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Initialize Alembic (for migrations)
alembic init alembic

# 4. Create your first migration
alembic revision --autogenerate -m "Initial schema"

# 5. Run migrations
alembic upgrade head

# 6. Process CSVs
python scripts/process_all_csvs.py

# 7. Start FastAPI
uvicorn src.api.main:app --reload


could be useful when dealing with freaking python

# Clear all pycache
find backend -type d -name "__pycache__" -exec rm -rf {} +
find backend -name "*.pyc" -delete


Are you using SQLAlchemy ORM/parameterized queries (✓ good) or string concatenation (✗ SQL injection risk)?
Connection pooling configured with max limits?
Database credentials in environment variables, not hardcoded?
Are you using Alembic migrations (you mentioned this) vs raw SQL?