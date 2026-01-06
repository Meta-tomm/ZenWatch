"""OAuth provider configurations and utilities"""
from typing import Optional
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx

from app.config import settings


@dataclass
class OAuthProvider:
    """OAuth provider configuration"""
    name: str
    authorize_url: str
    token_url: str
    userinfo_url: str
    client_id: Optional[str]
    client_secret: Optional[str]
    scopes: list[str]


# OAuth provider configurations
OAUTH_PROVIDERS = {
    "github": OAuthProvider(
        name="github",
        authorize_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        userinfo_url="https://api.github.com/user",
        client_id=getattr(settings, "GITHUB_CLIENT_ID", None),
        client_secret=getattr(settings, "GITHUB_CLIENT_SECRET", None),
        scopes=["read:user", "user:email"],
    ),
    "google": OAuthProvider(
        name="google",
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo",
        client_id=getattr(settings, "GOOGLE_CLIENT_ID", None),
        client_secret=getattr(settings, "GOOGLE_CLIENT_SECRET", None),
        scopes=["openid", "email", "profile"],
    ),
    "discord": OAuthProvider(
        name="discord",
        authorize_url="https://discord.com/api/oauth2/authorize",
        token_url="https://discord.com/api/oauth2/token",
        userinfo_url="https://discord.com/api/users/@me",
        client_id=getattr(settings, "DISCORD_CLIENT_ID", None),
        client_secret=getattr(settings, "DISCORD_CLIENT_SECRET", None),
        scopes=["identify", "email"],
    ),
}


def get_oauth_provider(provider_name: str) -> Optional[OAuthProvider]:
    """Get OAuth provider configuration by name"""
    return OAUTH_PROVIDERS.get(provider_name.lower())


def build_authorize_url(provider: OAuthProvider, redirect_uri: str, state: str) -> str:
    """
    Build OAuth authorization URL for a provider

    Args:
        provider: OAuth provider configuration
        redirect_uri: Callback URL after authorization
        state: CSRF protection state token

    Returns:
        Full authorization URL
    """
    params = {
        "client_id": provider.client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(provider.scopes),
        "state": state,
        "response_type": "code",
    }

    # Google requires additional params
    if provider.name == "google":
        params["access_type"] = "offline"
        params["prompt"] = "consent"

    return f"{provider.authorize_url}?{urlencode(params)}"


async def exchange_code_for_token(
    provider: OAuthProvider,
    code: str,
    redirect_uri: str
) -> Optional[dict]:
    """
    Exchange authorization code for access token

    Args:
        provider: OAuth provider configuration
        code: Authorization code from callback
        redirect_uri: Same redirect URI used in authorization

    Returns:
        Token response dict or None if failed
    """
    async with httpx.AsyncClient() as client:
        data = {
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        headers = {"Accept": "application/json"}

        try:
            response = await client.post(
                provider.token_url,
                data=data,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return None


async def get_oauth_user_info(
    provider: OAuthProvider,
    access_token: str
) -> Optional[dict]:
    """
    Get user info from OAuth provider

    Args:
        provider: OAuth provider configuration
        access_token: OAuth access token

    Returns:
        User info dict or None if failed
    """
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}

        # GitHub uses different header format
        if provider.name == "github":
            headers["Authorization"] = f"token {access_token}"

        try:
            response = await client.get(
                provider.userinfo_url,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            user_data = response.json()

            # Normalize user data across providers
            return normalize_oauth_user_data(provider.name, user_data)
        except httpx.HTTPError:
            return None


async def get_github_email(access_token: str) -> Optional[str]:
    """
    Get primary email from GitHub (requires separate API call)

    Args:
        access_token: GitHub OAuth access token

    Returns:
        Primary email address or None
    """
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"token {access_token}"}

        try:
            response = await client.get(
                "https://api.github.com/user/emails",
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            emails = response.json()

            # Find primary verified email
            for email_data in emails:
                if email_data.get("primary") and email_data.get("verified"):
                    return email_data.get("email")

            # Fallback to first verified email
            for email_data in emails:
                if email_data.get("verified"):
                    return email_data.get("email")

            return None
        except httpx.HTTPError:
            return None


def normalize_oauth_user_data(provider_name: str, raw_data: dict) -> dict:
    """
    Normalize OAuth user data to consistent format

    Args:
        provider_name: OAuth provider name
        raw_data: Raw user data from provider

    Returns:
        Normalized user data dict with keys: id, email, name, avatar_url
    """
    if provider_name == "github":
        return {
            "provider_id": str(raw_data.get("id")),
            "email": raw_data.get("email"),  # May be None, need separate call
            "name": raw_data.get("name") or raw_data.get("login"),
            "username": raw_data.get("login"),
            "avatar_url": raw_data.get("avatar_url"),
        }
    elif provider_name == "google":
        return {
            "provider_id": raw_data.get("id"),
            "email": raw_data.get("email"),
            "name": raw_data.get("name"),
            "username": None,  # Google does not provide username
            "avatar_url": raw_data.get("picture"),
        }
    elif provider_name == "discord":
        avatar_hash = raw_data.get("avatar")
        user_id = raw_data.get("id")
        avatar_url = None
        if avatar_hash and user_id:
            avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"

        return {
            "provider_id": raw_data.get("id"),
            "email": raw_data.get("email"),
            "name": raw_data.get("global_name") or raw_data.get("username"),
            "username": raw_data.get("username"),
            "avatar_url": avatar_url,
        }
    else:
        return raw_data
