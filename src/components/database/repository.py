from sqlalchemy import func, select

from .connection import SessionFactory

from .models import BeatmapSet

class BeatmapRepository:
    async def count(self) -> int:
        async with SessionFactory() as session:
            result = await session.scalar(
                select(func.count()).select_from(BeatmapSet)
            )
            return result or 0

    async def add_if_new(self, data: dict, notification_status: str = "pending") -> bool:
        async with SessionFactory() as session:
            existing = await session.get(
                BeatmapSet,
                data["id"]
            )

            if existing is not None:
                return False

            session.add(
                BeatmapSet(
                    id=data["id"],
                    title=data.get("title"),
                    artist=data.get("artist"),
                    creator=data.get("creator"),
                    status=data.get("status"),
                    notification_status=notification_status,
                )
            )

            await session.commit()
            return True

    async def get_pending(self) -> list[BeatmapSet]:
        async with SessionFactory() as session:
            result = await session.scalars(
                select(BeatmapSet).where(
                    BeatmapSet.notification_status == "pending"
                )
            )
            return list(result.all())

    async def mark_sent(self, beatmapset_id: int) -> None:
        async with SessionFactory() as session:
            beatmapset = await session.get(
                BeatmapSet,
                beatmapset_id
            )

            if beatmapset is not None:
                beatmapset.notification_status = "sent"
                await session.commit()