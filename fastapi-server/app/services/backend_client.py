import httpx

from app.core.config import SPRING_BACKEND_BASE_URL, SPRING_DETECTION_PATH
from app.schemas.detection import DetectionResult


class BackendClient:
    async def send_detection(self, result: DetectionResult) -> dict:
        url = f"{SPRING_BACKEND_BASE_URL}{SPRING_DETECTION_PATH}"

        payload = result.model_dump(
            by_alias=True,
            mode="json",
        )

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json=payload,
            )

        response.raise_for_status()

        if not response.content:
            return {"status": "sent"}

        return response.json()

