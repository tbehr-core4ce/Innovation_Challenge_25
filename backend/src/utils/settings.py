"""
Configuration management for BETS API
Loads from environment variables with sensible defaults
"""
import os
from typing import Any, Dict, Optional

# from dotenv import load_dotenv

# # Find the .env file (go up from src/utils/ to backend/)
# env_path = Path(__file__).parent.parent.parent / ".env"
# load_dotenv(dotenv_path=env_path)


class Settings:
    """
    Loads configuration from environment variables.
    Azure blob storage is optional (enabled via ENABLE_BLOB_STORAGE=true).
    """
    
    # Core required configuration
    REQUIRED_KEYS = [
        "DATABASE_URL",
    ]
    
    # Azure configuration (only required if blob storage enabled)
    AZURE_REQUIRED = [
        "AZURE_STORAGE_ACCOUNT",
        "AZURE_CONTAINER_NAME",
    ]
    
    # Azure auth - either connection string OR account key
    AZURE_AUTH_KEYS = [
        "AZURE_CONNECTION_STRING",
        "AZURE_ACCOUNT_KEY",
    ]
    
    # Base defaults
    BASE_DEFAULTS = {
        "ENVIRONMENT": "dev",
        "LOG_LEVEL": "INFO",
        "ENABLE_BLOB_STORAGE": "false",
        "DATABASE_URL": "postgresql+psycopg://bets_user:bets_password@localhost:5432/bets_db",
        
        # Azure defaults (used if blob storage enabled)
        "AZURE_CONTAINER_NAME": "bets-datasets",
        "ENDPOINT_SUFFIX": "core.usgovcloudapi.net",
        
        # BETS-specific defaults
        "DEFAULT_MAP_CENTER_LAT": "39.8283",  # US center
        "DEFAULT_MAP_CENTER_LON": "-98.5795",
        "DEFAULT_MAP_ZOOM": "4",
        "DATA_REFRESH_INTERVAL_MINUTES": "60",  # How often to check for new data
        "ALERT_THRESHOLD_CASES": "10",  # Cases before triggering alert
    }
    """  DEFAULT_MAP_CENTER_LAT/LON - For initial map view (set to US center)
    DEFAULT_MAP_ZOOM - Initial zoom level
    DATA_REFRESH_INTERVAL_MINUTES - How often to poll for new H5N1 data
    ALERT_THRESHOLD_CASES - Trigger threshold for outbreak alerts"""
    
    def __init__(self):
        # Copy environment variables
        self._env: Dict[str, str] = dict(os.environ)
        
        # Apply defaults
        for key, val in self.BASE_DEFAULTS.items():
            self._env.setdefault(key, val)
        
        # Determine environment
        self.environment = self._env.get("ENVIRONMENT", "dev").lower()
        self.enable_blob_storage = self._env.get("ENABLE_BLOB_STORAGE", "false").lower() == "true"
        
        print(f"[INFO] Environment: {self.environment}")
        print(f"[INFO] Blob storage: {'enabled' if self.enable_blob_storage else 'disabled'}")
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate that required configuration is present"""
        # Always check core required keys
        missing = [k for k in self.REQUIRED_KEYS if k not in self._env or not self._env.get(k)]
        if missing:
            raise ValueError(f"Missing required configuration: {missing}")
        
        # Only validate Azure if blob storage is enabled
        if self.enable_blob_storage:
            azure_missing = [k for k in self.AZURE_REQUIRED if k not in self._env or not self._env.get(k)]
            if azure_missing:
                raise ValueError(
                    f"Blob storage enabled but missing Azure configuration: {azure_missing}\n"
                    f"Set ENABLE_BLOB_STORAGE=false or provide Azure credentials."
                )
            
            # Check that at least one auth method is present
            has_auth = any(k in self._env and self._env.get(k) for k in self.AZURE_AUTH_KEYS)
            if not has_auth:
                raise ValueError(
                    f"Blob storage enabled but missing Azure authentication.\n"
                    f"Provide either: {', '.join(self.AZURE_AUTH_KEYS)}"
                )
    
    def __getattr__(self, name: str) -> str:
        """Get configuration value by attribute access"""
        if name.startswith('_'):
            raise AttributeError(f"Setting `{name}` not found")
        if name in self._env:
            return self._env[name]
        raise AttributeError(f"Setting `{name}` not found")
    
    def get(self, name: str, default: Optional[Any] = None) -> Optional[Any]:
        """Get configuration value with optional default"""
        return self._env.get(name, default)
    
    def has_connection_string(self) -> bool:
        """Check if connection string authentication is available"""
        return bool(self._env.get("AZURE_CONNECTION_STRING"))
    
    def has_account_key(self) -> bool:
        """Check if account key authentication is available"""
        return bool(self._env.get("AZURE_ACCOUNT_KEY"))
    
    def is_dev(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "dev"
    
    def is_staging(self) -> bool:
        """Check if running in staging environment"""
        return self.environment == "staging"
    
    def is_prod(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "prod"


# Global settings instance
settings = Settings()