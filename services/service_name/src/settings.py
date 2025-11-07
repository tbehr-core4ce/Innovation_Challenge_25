"""
PROBS Unneeded ???
"""
import os
import json
from typing import Any, Dict, Optional


class Settings:
    """
    Loads configuration from environment variables or Azure Key Vault.
    Supports both connection string and account key authentication.
    Supports environment-specific configuration (dev, staging, prod).
    """
    
    # Required Azure configuration keys
    AZURE_REQUIRED = [
        "AZURE_STORAGE_ACCOUNT",   # replaced AZURE_ACCOUNT_NAME
        "AZURE_CONTAINER_NAME",
    ]
    
    # Optional - either connection string OR account key
    AZURE_AUTH_KEYS = [
        "AZURE_CONNECTION_STRING",
        "AZURE_ACCOUNT_KEY",
    ]
    
    # Base defaults (can be overridden by environment)
    BASE_DEFAULTS = {
        "UPLOAD_DIR": "/tmp/uploads",
        "OUTPUT_DIR": "/tmp/outputs",
        "ENDPOINT_SUFFIX": "core.usgovcloudapi.net",
        "AZURE_CONTAINER_NAME": "snappi"
    }
    
    # Environment-specific defaults
    ENV_DEFAULTS = {
        "dev": {
            "AZURE_ACCOUNT_NAME": "literacydev",
        },
        "staging": {
            "AZURE_ACCOUNT_NAME": "literacystaging",
        },
        "prod": {
            "AZURE_ACCOUNT_NAME": "literacyprod",
        }
    }
    
    # Secrets that can be loaded from Azure Key Vault
    SECRET_KEYS = [
        "AZURE_CONNECTION_STRING",
        "AZURE_ACCOUNT_KEY",
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
    ]
    
    def __init__(self):
        # Copy environment variables
        self._env: Dict[str, str] = dict(os.environ)

        # if "AZURE_ACCOUNT_NAME" in self._env and "AZURE_STORAGE_ACCOUNT" not in self._env:
        #     self._env["AZURE_STORAGE_ACCOUNT"] = self._env["AZURE_ACCOUNT_NAME"]
        
        # Determine environment (default to prod for safety)
        self.environment = self._env.get("ENVIRONMENT", "prod").lower() 
        print(f"[INFO] Loading settings for environment: {self.environment}")
        
        # Apply base defaults
        for key, val in self.BASE_DEFAULTS.items():
            self._env.setdefault(key, val)
        
        # Apply environment-specific defaults
        if self.environment in self.ENV_DEFAULTS:
            for key, val in self.ENV_DEFAULTS[self.environment].items():
                # Only set if not already in environment
                self._env.setdefault(key, val)
        else:
            # Unknown environment, use prod defaults
            print(f"[WARNING] Unknown environment '{self.environment}', using prod defaults")
            for key, val in self.ENV_DEFAULTS["prod"].items():
                self._env.setdefault(key, val)
        
        print(f"[INFO] Using Azure container: {self._env.get('AZURE_CONTAINER_NAME')}")
        
        # Try loading from Azure Key Vault if configured
        if "AZURE_KEY_VAULT_URL" in self._env:
            self._load_from_keyvault(self._env["AZURE_KEY_VAULT_URL"])
        
        # Validate required configuration
        self._validate_config()
    
    def _load_from_keyvault(self, vault_url: str) -> None:
        """Load secrets from Azure Key Vault"""
        try:
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=vault_url, credential=credential)
            
            for secret_name in self.SECRET_KEYS:
                try:
                    # Convert env var name to Key Vault format (replace _ with -)
                    kv_secret_name = secret_name.replace("_", "-")
                    secret = client.get_secret(kv_secret_name)
                    self._env[secret_name] = secret.value
                except Exception:
                    # Secret doesn't exist in Key Vault, skip
                    continue
        except Exception as e:
            print(f"Warning: Could not load from Key Vault: {e}")
    
    def _validate_config(self) -> None:
        """Validate that required configuration is present"""
        # Check required keys
        missing = [k for k in self.AZURE_REQUIRED if k not in self._env or not self._env.get(k)]
        if missing:
            raise ValueError(f"Missing required Azure configuration: {missing}")
        
        # Check that at least one auth method is present
        has_auth = any(k in self._env and self._env.get(k) for k in self.AZURE_AUTH_KEYS)
        if not has_auth:
            raise ValueError(
                f"Missing Azure authentication. Provide either: {', '.join(self.AZURE_AUTH_KEYS)}"
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