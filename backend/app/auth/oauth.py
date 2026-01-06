from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class OAuthUserInfo:
    """Normalized user info from OAuth providers."""
    provider: str
    provider_user_id: str
    email: Optional[str]
    username: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]


class OAuthProvider:
    """Base class for OAuth providers."""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        """Get the OAuth authorization URL."""
        raise NotImplementedError

    async def exchange_code(self, code: str, redirect_uri: str) -> Optional[str]:
        """Exchange authorization code for access token."""
        raise NotImplementedError

    async def get_user_info(self, access_token: str) -> Optional[OAuthUserInfo]:
        """Get user info from the provider."""
        raise NotImplementedError


class GitHubOAuth(OAuthProvider):
    """GitHub OAuth implementation."""

    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_URL = "https://api.github.com/user"
    EMAILS_URL = "https://api.github.com/user/emails"

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": "user:email",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query}"

    async def exchange_code(self, code: str, redirect_uri: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": redirect_uri,
                    },
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                data = response.json()
                return data.get("access_token")
            except Exception as e:
                logger.error(f"GitHub token exchange failed: {e}")
                return None

    async def get_user_info(self, access_token: str) -> Optional[OAuthUserInfo]:
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Authorization": f"Bearer {access_token}"}

                # Get user profile
                user_response = await client.get(self.USER_URL, headers=headers)
                user_response.raise_for_status()
                user_data = user_response.json()

                # Get primary email
                email = user_data.get("email")
                if not email:
                    emails_response = await client.get(self.EMAILS_URL, headers=headers)
                    emails_response.raise_for_status()
                    emails = emails_response.json()
                    primary = next((e for e in emails if e.get("primary")), None)
                    email = primary.get("email") if primary else None

                return OAuthUserInfo(
                    provider="github",
                    provider_user_id=str(user_data["id"]),
                    email=email,
                    username=user_data.get("login"),
                    display_name=user_data.get("name"),
                    avatar_url=user_data.get("avatar_url"),
                )
            except Exception as e:
                logger.error(f"GitHub user info fetch failed: {e}")
                return None


class GoogleOAuth(OAuthProvider):
    """Google OAuth implementation."""

    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "email profile",
            "state": state,
            "access_type": "offline",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query}"

    async def exchange_code(self, code: str, redirect_uri: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("access_token")
            except Exception as e:
                logger.error(f"Google token exchange failed: {e}")
                return None

    async def get_user_info(self, access_token: str) -> Optional[OAuthUserInfo]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.USER_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                data = response.json()

                return OAuthUserInfo(
                    provider="google",
                    provider_user_id=data["id"],
                    email=data.get("email"),
                    username=None,
                    display_name=data.get("name"),
                    avatar_url=data.get("picture"),
                )
            except Exception as e:
                logger.error(f"Google user info fetch failed: {e}")
                return None


class DiscordOAuth(OAuthProvider):
    """Discord OAuth implementation."""

    AUTH_URL = "https://discord.com/api/oauth2/authorize"
    TOKEN_URL = "https://discord.com/api/oauth2/token"
    USER_URL = "https://discord.com/api/users/@me"

    def get_authorization_url(self, redirect_uri: str, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "identify email",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query}"

    async def exchange_code(self, code: str, redirect_uri: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": redirect_uri,
                        "grant_type": "authorization_code",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                data = response.json()
                return data.get("access_token")
            except Exception as e:
                logger.error(f"Discord token exchange failed: {e}")
                return None

    async def get_user_info(self, access_token: str) -> Optional[OAuthUserInfo]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.USER_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                data = response.json()

                avatar_url = None
                if data.get("avatar"):
                    avatar_url = (
                        f"https://cdn.discordapp.com/avatars/{data['id']}/{data['avatar']}.png"
                    )

                return OAuthUserInfo(
                    provider="discord",
                    provider_user_id=data["id"],
                    email=data.get("email"),
                    username=data.get("username"),
                    display_name=data.get("global_name") or data.get("username"),
                    avatar_url=avatar_url,
                )
            except Exception as e:
                logger.error(f"Discord user info fetch failed: {e}")
                return None


def get_oauth_provider(provider: str) -> Optional[OAuthProvider]:
    """
    Factory function to get OAuth provider instance.

    Args:
        provider: Provider name ('github', 'google', 'discord')

    Returns:
        Configured OAuth provider or None if not configured
    """
    providers = {
        "github": (settings.OAUTH_GITHUB_CLIENT_ID, settings.OAUTH_GITHUB_CLIENT_SECRET, GitHubOAuth),
        "google": (settings.OAUTH_GOOGLE_CLIENT_ID, settings.OAUTH_GOOGLE_CLIENT_SECRET, GoogleOAuth),
        "discord": (settings.OAUTH_DISCORD_CLIENT_ID, settings.OAUTH_DISCORD_CLIENT_SECRET, DiscordOAuth),
    }

    if provider not in providers:
        logger.warning(f"Unknown OAuth provider: {provider}")
        return None

    client_id, client_secret, provider_class = providers[provider]

    if not client_id or not client_secret:
        logger.warning(f"OAuth provider {provider} not configured")
        return None

    return provider_class(client_id, client_secret)
