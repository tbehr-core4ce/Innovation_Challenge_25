#!/usr/bin/env python3
"""
Database management utility script for BETS.
Provides commands for database setup, migration, and seeding.
backend/scripts/db_manager.py
Usage:
    python scripts/db_manager.py init      # Initialize database
    python scripts/db_manager.py migrate   # Run migrations
    python scripts/db_manager.py seed      # Seed sample data
    python scripts/db_manager.py reset     # Reset database (CAUTION!)
    python scripts/db_manager.py check     # Check database connection
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import argparse
from datetime import datetime, timedelta
import random

from src.core.database import (
    engine, Base, SessionLocal, 
    init_db, drop_all_tables, check_db_connection
)
from src.core.logging import setup_logging, get_logger

from src.core.models import (
    H5N1Case, Alert, DataImport, User,
    AnimalCategory, CaseStatus, Severity, DataSource, AlertType
)

# Setup logging
setup_logging("INFO")
logger = get_logger(__name__)


def initialize_database():
    """Initialize database by creating all tables."""
    logger.info("Initializing database...")
    
    if not check_db_connection():
        logger.error("Cannot connect to database. Check your DATABASE_URL.")
        return False
    
    try:
        init_db()
        logger.info("Database initialized successfully!")
        return True
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        return False


def run_migrations():
    """Run Alembic migrations."""
    logger.info("Running database migrations...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=backend_path
        )
        
        if result.returncode == 0:
            logger.info("Migrations completed successfully!")
            print(result.stdout)
            return True
        else:
            logger.error("Migration failed", error=result.stderr)
            print(result.stderr)
            return False
            
    except Exception as e:
        logger.error("Failed to run migrations", error=str(e))
        return False


def create_sample_cases(db, count: int = 50):
    """Create sample H5N1 cases for testing."""
    logger.info(f"Creating {count} sample cases...")
    
    # Sample locations (longitude, latitude) - US locations
    locations = [
        (-122.4194, 37.7749, "San Francisco", "California", "San Francisco County"),
        (-118.2437, 34.0522, "Los Angeles", "California", "Los Angeles County"),
        (-87.6298, 41.8781, "Chicago", "Illinois", "Cook County"),
        (-95.3698, 29.7604, "Houston", "Texas", "Harris County"),
        (-75.1652, 39.9526, "Philadelphia", "Pennsylvania", "Philadelphia County"),
        (-112.0740, 33.4484, "Phoenix", "Arizona", "Maricopa County"),
        (-104.9903, 39.7392, "Denver", "Colorado", "Denver County"),
        (-122.3321, 47.6062, "Seattle", "Washington", "King County"),
        (-71.0589, 42.3601, "Boston", "Massachusetts", "Suffolk County"),
        (-80.1918, 25.7617, "Miami", "Florida", "Miami-Dade County"),
    ]
    
    animal_species = {
        AnimalCategory.POULTRY: ["Chicken", "Turkey", "Duck", "Goose"],
        AnimalCategory.DAIRY_CATTLE: ["Holstein Cow", "Jersey Cow", "Brown Swiss"],
        AnimalCategory.WILD_BIRD: ["Canada Goose", "Mallard Duck", "Snow Goose", "Crow"],
        AnimalCategory.WILD_MAMMAL: ["Raccoon", "Fox", "Skunk", "Bear"],
        AnimalCategory.DOMESTIC_MAMMAL: ["Cat", "Dog", "Pig"],
    }
    
    cases = []
    start_date = datetime.now() - timedelta(days=180)
    
    for i in range(count):
        lng, lat, city, state, county = random.choice(locations)
        category = random.choice(list(AnimalCategory))
        species = random.choice(animal_species.get(category, ["Unknown"]))
        
        case_date = start_date + timedelta(days=random.randint(0, 180))
        
        case = H5N1Case(
            external_id=f"SAMPLE-{i+1:04d}",
            case_date=case_date,
            report_date=case_date + timedelta(days=random.randint(1, 7)),
            status=random.choice(list(CaseStatus)),
            severity=random.choice(list(Severity)),
            animal_category=category,
            animal_species=species,
            animals_affected=random.randint(1, 500),
            animals_dead=random.randint(0, 300),
            country="United States",
            state_province=state,
            county=county,
            city=city,
            latitude=lat + random.uniform(-0.5, 0.5),
            longitude=lng + random.uniform(-0.5, 0.5),
            data_source=random.choice(list(DataSource)),
            description=f"Sample H5N1 case in {city}, {state}",
        )
        
        # Set PostGIS geometry from lat/lng
        # Format: ST_GeomFromText('POINT(longitude latitude)', 4326)
        from sqlalchemy import text
        case.location = text(f"ST_GeomFromText('POINT({case.longitude} {case.latitude})', 4326)")
        
        cases.append(case)
    
    try:
        db.bulk_save_objects(cases)
        db.commit()
        logger.info(f"Created {count} sample cases successfully!")
        return True
    except Exception as e:
        db.rollback()
        logger.error("Failed to create sample cases", error=str(e))
        return False


def create_sample_alerts(db, count: int = 10):
    """Create sample alerts."""
    logger.info(f"Creating {count} sample alerts...")
    
    # Get some random cases to associate with alerts
    cases = db.query(H5N1Case).limit(count).all()
    
    alerts = []
    for i, case in enumerate(cases):
        alert = Alert(
            alert_type=random.choice(list(AlertType)),
            title=f"Alert: {case.animal_category.value} outbreak in {case.city}",
            description=f"H5N1 detected in {case.animals_affected} {case.animal_species}",
            severity=case.severity,
            case_id=case.id,
            country=case.country,
            state_province=case.state_province,
            is_active=random.choice([True, True, True, False]),  # 75% active
        )
        alerts.append(alert)
    
    try:
        db.bulk_save_objects(alerts)
        db.commit()
        logger.info(f"Created {count} sample alerts successfully!")
        return True
    except Exception as e:
        db.rollback()
        logger.error("Failed to create sample alerts", error=str(e))
        return False


def create_admin_user(db):
    """Create a default admin user."""
    logger.info("Creating admin user...")
    
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Check if admin already exists
    existing = db.query(User).filter(User.email == "admin@bets.local").first()
    if existing:
        logger.info("Admin user already exists")
        return True
    
    admin = User(
        email="admin@bets.local",
        username="admin",
        hashed_password=pwd_context.hash("admin123"),  # Change this!
        full_name="BETS Administrator",
        organization="BETS",
        role="admin",
        is_active=True,
        is_superuser=True,
    )
    
    try:
        db.add(admin)
        db.commit()
        logger.info("Admin user created successfully!")
        logger.info("Email: admin@bets.local | Password: admin123 (CHANGE THIS!)")
        return True
    except Exception as e:
        db.rollback()
        logger.error("Failed to create admin user", error=str(e))
        return False


def seed_database():
    """Seed database with sample data."""
    logger.info("Seeding database with sample data...")
    
    db = SessionLocal()
    try:
        # Create sample cases
        create_sample_cases(db, count=100)
        
        # Create sample alerts
        create_sample_alerts(db, count=15)
        
        # Create admin user
        create_admin_user(db)
        
        logger.info("Database seeding completed successfully!")
        return True
        
    except Exception as e:
        logger.error("Failed to seed database", error=str(e))
        return False
    finally:
        db.close()


def reset_database():
    """Reset database by dropping and recreating all tables."""
    logger.warning("!!! RESETTING DATABASE - ALL DATA WILL BE LOST !!!")
    
    response = input("Are you sure? Type 'yes' to continue: ")
    if response.lower() != 'yes':
        logger.info("Reset cancelled")
        return False
    
    try:
        drop_all_tables()
        init_db()
        logger.info("Database reset successfully!")
        return True
    except Exception as e:
        logger.error("Failed to reset database", error=str(e))
        return False


def check_connection():
    """Check database connection and display info."""
    logger.info("Checking database connection...")
    
    if check_db_connection():
        db = SessionLocal()
        try:
            case_count = db.query(H5N1Case).count()
            alert_count = db.query(Alert).count()
            user_count = db.query(User).count()
            
            logger.info("Database connection successful!")
            logger.info(f"Cases: {case_count}")
            logger.info(f"Alerts: {alert_count}")
            logger.info(f"Users: {user_count}")
            return True
        except Exception as e:
            logger.error("Database connected but query failed", error=str(e))
            return False
        finally:
            db.close()
    else:
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="BETS Database Manager")
    parser.add_argument(
        "command",
        choices=["init", "migrate", "seed", "reset", "check"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    commands = {
        "init": initialize_database,
        "migrate": run_migrations,
        "seed": seed_database,
        "reset": reset_database,
        "check": check_connection,
    }
    
    success = commands[args.command]()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()