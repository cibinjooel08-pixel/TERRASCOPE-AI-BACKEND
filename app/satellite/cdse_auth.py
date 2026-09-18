import os
import time
import requests
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = os.getenv("SENTINEL_HUB_TOKEN_URL", "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token")

class CDSEAuthManager:
    """
    OAuth2 Client Credentials Token Manager for Copernicus Data Space Ecosystem.
    Caches access token until 60s before expiry to avoid requesting new tokens on every API call.
    """
    def __init__(self):
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0

    DEFAULT_CLIENT_ID = "sh-3fc3f2a5-092e-4bf8-b56a-8f30efdfeb66"
    DEFAULT_CLIENT_SECRET = "dQkxtSSFzrTZV5MpWhh9g2ZraoFHaoGX"

    def get_client_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        client_id = os.getenv("SENTINEL_HUB_CLIENT_ID", "").strip() or self.DEFAULT_CLIENT_ID
        client_secret = os.getenv("SENTINEL_HUB_CLIENT_SECRET", "").strip() or self.DEFAULT_CLIENT_SECRET
        return (client_id if client_id else None, client_secret if client_secret else None)

    def get_token(self) -> Tuple[Optional[str], Dict[str, Any]]:
        client_id, client_secret = self.get_client_credentials()
        if not client_id or not client_secret:
            return None, {
                "status": "UNCONFIGURED",
                "error_code": "MISSING_CREDENTIALS",
                "message": "SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET environment variables are missing.",
                "suggestion": "Configure client credentials in backend/.env file."
            }

        # Return cached token if still valid (with 60s buffer)
        if self._access_token and time.time() < (self._expires_at - 60):
            return self._access_token, {
                "status": "READY",
                "message": "Valid cached token available",
                "cached": True
            }

        try:
            response = requests.post(
                TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self._access_token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)
                self._expires_at = time.time() + float(expires_in)
                return self._access_token, {
                    "status": "READY",
                    "message": "Authentication successful",
                    "expires_in": expires_in,
                    "cached": False
                }
            elif response.status_code in (400, 401):
                return None, {
                    "status": "INVALID_CREDENTIALS",
                    "error_code": "AUTHENTICATION_FAILED",
                    "message": "Invalid Copernicus CDSE Client ID or Client Secret.",
                    "http_code": response.status_code,
                    "suggestion": "Verify your credentials in backend/.env."
                }
            else:
                return None, {
                    "status": "PROVIDER_ERROR",
                    "error_code": "COPERNICUS_AUTH_ERROR",
                    "message": f"Copernicus Auth server returned HTTP {response.status_code}",
                    "http_code": response.status_code
                }
        except requests.exceptions.RequestException as e:
            return None, {
                "status": "NETWORK_ERROR",
                "error_code": "AUTH_NETWORK_FAILURE",
                "message": f"Could not reach Copernicus auth endpoint: {str(e)}",
                "suggestion": "Check internet connectivity."
            }

    def check_health(self) -> Dict[str, Any]:
        client_id, client_secret = self.get_client_credentials()
        has_id = bool(client_id)
        has_secret = bool(client_secret)

        if not has_id or not has_secret:
            return {
                "status": "UNCONFIGURED",
                "has_client_id": has_id,
                "has_client_secret": has_secret,
                "message": "CDSE Credentials are not set."
            }

        token, diag = self.get_token()
        if token:
            return {
                "status": "READY",
                "has_client_id": True,
                "has_client_secret": True,
                "token_valid": True,
                "expires_in_seconds": round(self._expires_at - time.time(), 1),
                "message": "Copernicus CDSE OAuth Authentication is active and ready."
            }
        else:
            return {
                "status": diag.get("status", "FAILED"),
                "has_client_id": True,
                "has_client_secret": True,
                "token_valid": False,
                "error_code": diag.get("error_code"),
                "message": diag.get("message")
            }

cdse_auth = CDSEAuthManager()
