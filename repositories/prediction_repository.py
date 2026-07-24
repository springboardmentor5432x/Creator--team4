"""
repositories/prediction_repository.py — Prediction Data Access Layer

Handles CRUD operations against the predictions MongoDB collection.
Stores reach predictions and audience forecasts with TTL auto-expiration.
"""

from typing import Dict, List, Optional
from datetime import datetime
from mongo.mongodb import get_database
from models.mongo import PREDICTIONS
import pymongo


class PredictionRepository:
    """
    Data access layer for the predictions collection.

    Document schema:
        {
            creator_id: str,
            prediction_type: str,  # 'reach' | 'audience'
            predicted_value: dict,
            confidence: float,
            generated_at: datetime,
        }
    """

    async def save_prediction(
        self,
        creator_id: str,
        prediction_type: str,
        data: Dict,
    ) -> str:
        """
        Save a new prediction record.

        Args:
            creator_id: Creator ID.
            prediction_type: Type of prediction ('reach' or 'audience').
            data: Full prediction result data.

        Returns:
            Inserted document _id as string.
        """
        db = get_database()
        doc = {
            "creator_id": creator_id,
            "prediction_type": prediction_type,
            "predicted_value": data,
            "generated_at": datetime.utcnow(),
        }
        result = await db[PREDICTIONS].insert_one(doc)
        return str(result.inserted_id)

    async def get_predictions(
        self,
        creator_id: str,
        prediction_type: str,
        limit: int = 10,
    ) -> List[Dict]:
        """Fetch recent predictions for a creator, newest first."""
        db = get_database()
        cursor = (
            db[PREDICTIONS]
            .find({"creator_id": creator_id, "prediction_type": prediction_type})
            .sort("generated_at", pymongo.DESCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def get_latest_prediction(
        self,
        creator_id: str,
        prediction_type: str,
    ) -> Optional[Dict]:
        """Return the most recent prediction of the given type."""
        db = get_database()
        return await db[PREDICTIONS].find_one(
            {"creator_id": creator_id, "prediction_type": prediction_type},
            sort=[("generated_at", pymongo.DESCENDING)],
        )
