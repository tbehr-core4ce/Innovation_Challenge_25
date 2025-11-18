# BETS Database Makefile
# Convenient shortcuts for common operations

.PHONY: help db-up db-down db-reset db-check db-seed db-migrate db-logs install clean

help:  ## Show this help message
	@echo "BETS Database Management Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# Docker Commands
db-up:  ## Start PostgreSQL database
	docker compose up -d postgres
	@echo "Waiting for database to be ready..."
	@sleep 5
	@echo "✓ Database is running on localhost:5432"

db-down:  ## Stop PostgreSQL database
	docker compose down

db-reset:  ## Reset database (WARNING: deletes all data!)
	docker compose down -v
	docker compose up -d postgres
	@sleep 5
	@echo "✓ Database reset complete"

db-logs:  ## View database logs
	docker compose logs -f postgres

# Python/Alembic Commands
install:  ## Install Python dependencies CHANGE TO POETRY
	cd backend && pip install -r requirements.txt 

db-check:  ## Check database connection and show statistics
	cd backend && python scripts/db_manager.py check

db-init:  ## Initialize database tables
	cd backend && python scripts/db_manager.py init

db-seed:  ## Seed database with sample data
	cd backend && python scripts/db_manager.py seed

db-migrate:  ## Run database migrations
	cd backend && alembic upgrade head

db-migrate-create:  ## Create a new migration
	cd backend && alembic revision --autogenerate -m "$(msg)"

# Example: make db-migrate-create msg="Add new field"

db-migrate-history:  ## Show migration history
	cd backend && alembic history

db-migrate-current:  ## Show current migration version
	cd backend && alembic current

# Combined Commands
setup:  ## Complete setup (start DB, install deps, migrate, seed)
	@echo "🚀 Starting BETS database setup..."
	@$(MAKE) db-up
	@$(MAKE) install
	@sleep 2
	@echo "Creating initial migration..."
	cd backend && alembic revision --autogenerate -m "Initial schema" || true
	@$(MAKE) db-migrate
	@$(MAKE) db-seed
	@echo "✓ Setup complete!"
	@$(MAKE) db-check

quickstart: setup  ## Alias for setup

# Development Commands
dev:  ## Start development server
	cd backend && uvicorn app.main:app --reload --port 8000

pgadmin:  ## Start pgAdmin
	docker-compose up -d pgadmin
	@echo "✓ pgAdmin running at http://localhost:5050"
	@echo "  Login: admin@bets.local / admin"

# Cleanup
clean:  ## Clean up Python cache files
	find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find backend -type f -name "*.pyc" -delete 2>/dev/null || true
	find backend -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned up cache files"

clean-all: clean db-down  ## Clean everything and stop database
	@echo "✓ Complete cleanup done"

# Testing
test:  ## Run tests
	cd backend && pytest

test-cov:  ## Run tests with coverage
	cd backend && pytest --cov=app --cov-report=html

# Backup/Restore
db-backup:  ## Backup database to file
	docker-compose exec -T postgres pg_dump -U bets_user bets_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✓ Backup created: backup_$(shell date +%Y%m%d_%H%M%S).sql"

db-restore:  ## Restore database from backup (use: make db-restore file=backup.sql)
	@if [ -z "$(file)" ]; then echo "Usage: make db-restore file=backup.sql"; exit 1; fi
	cat $(file) | docker-compose exec -T postgres psql -U bets_user bets_db
	@echo "✓ Database restored from $(file)"

# Status
status:  ## Show database and application status
	@echo "=== Docker Status ==="
	@docker-compose ps
	@echo ""
	@echo "=== Database Status ==="
	@$(MAKE) db-check