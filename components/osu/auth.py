import time

import httpx


class OsuAuth:
    TOKEN_URL = "https://osu.ppy.sh/oauth/token"

    def __init__(self, client_id: str, client_secret:str):
        self.client_id = client_id
        self.client_secret = client_secret

        self._token: str | None = None
        self._expires_at = 0.0

    async def get_token(self, client: httpx.AsyncClient) -> str:
        if self._token and time.monotonic() < self._expires_at:
            return self._token

        response = await client.post(
            self.TOKEN_URL,
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
                "scope": "public"
            },
        )
        data = response.json()

        self._token = data["access_token"]
        self._expires_at = (
            time.monotonic() + data["expires_in"] - 60
        )

        return self._token
