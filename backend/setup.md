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