import logging

import httpx 

from .auth import OsuAuth

logger = logging.getLogger(__name__)

class OsuClient:
    BASE_URL = "https://osu.ppy.sh/api/v2"

    def __init__(self, auth: OsuAuth):
        self.auth = auth
        self.http = httpx.AsyncClient(timeout=20)

    async def get(self, endpoint: str, params: dict | None = None) -> dict:
        token = await self.auth.get_token(self.http)

        response = await self.http.get(
            f"{self.BASE_URL}{endpoint}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            },
            params=params
        )
    
        response.raise_for_status()

        return response.json()

    async def get_beatmap(self, beatmapset_id: int) -> dict:
        return await self.get(f"/beatmapsets/{beatmapset_id}")

    async def get_beatmapsets_by_status(self, status: str) -> list[dict]:
        logger.info("Запрос сетов osu! со статусом: %s", status)
        data = await self.get(
            "/beatmapsets/search",
            params={
                "s": status,
                "sort": "updated_desc",
                "limit": 15,
            },
        )

        beatmapsets = data.get("beatmapsets", [])[:15]

        logger.info(
            "Статус %s: получено %s сетов",
            status,
            len(beatmapsets)
        )

        return beatmapsets


    async def get_ranked_and_qualified_beatmapsets(self) -> list[dict]:

        ranked = await self.get_beatmapsets_by_status("ranked")
        qualified = await self.get_beatmapsets_by_status("qualified")
        loved = await self.get_beatmapsets_by_status("loved")

        beatmapsets = {
            beatmapset["id"]: beatmapset
            for beatmapset in ranked + qualified + loved
        }

        result = []

        for beatmapset in beatmapsets.values():
            standart_maps = [
                beatmap
                for beatmap in beatmapset.get("beatmaps", [])
                if beatmap.get("mode") == "osu"
                or beatmap.get("mode_int") == 0
            ]

            if standart_maps:
                beatmapset["beatmaps"] = standart_maps
                result.append(beatmapset)

        for beatmapset in result:
            print(
                beatmapset["id"],
                beatmapset.get("title"),
                beatmapset.get("status"),
            )

        return result


    async def close(self) -> None:
        await self.http.aclose()