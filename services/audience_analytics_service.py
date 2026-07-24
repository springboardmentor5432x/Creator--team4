from typing import Dict, Optional
from repositories.audience_repository import AudienceRepository


class AudienceAnalyticsService:
    def __init__(self):
        self.repository = AudienceRepository()

    async def get_analytics(self, creator_id: str) -> Optional[Dict]:
        return await self.repository.get_audience_analytics(creator_id)

    async def get_demographics(self, creator_id: str) -> Optional[Dict]:
        return await self.repository.get_audience_demographics(creator_id)

    async def get_behavior(self, creator_id: str) -> Optional[Dict]:
        return await self.repository.get_audience_behavior(creator_id)

    async def save_analytics(self, data: Dict) -> str:
        return await self.repository.save_audience_analytics(data)

    async def save_demographics(self, data: Dict) -> str:
        return await self.repository.save_audience_demographics(data)

    async def save_behavior(self, data: Dict) -> str:
        return await self.repository.save_audience_behavior(data)