import httpx

from app.core.config import BACKEND_INTERNAL_API_KEY, SPRING_BACKEND_BASE_URL, SPRING_DETECTION_PATH
from app.schemas.detection import DetectionResult


class BackendClient:
    async def send_detection(
        self,
        result: DetectionResult,
        analysis_status: str | None = None,
    ) -> dict:
        if not BACKEND_INTERNAL_API_KEY:
            raise RuntimeError("BACKEND_INTERNAL_API_KEY is not set")
        
        url = f"{SPRING_BACKEND_BASE_URL}{SPRING_DETECTION_PATH}"
        headers = {
            "X-Internal-Api-Key": BACKEND_INTERNAL_API_KEY,
            "Content-Type": "application/json",
        }

        payload = result.model_dump(
            by_alias=True,
            mode="json",
        )
        if analysis_status is not None:
            payload["status"] = analysis_status

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers
            )

        response.raise_for_status()

        if not response.content:
            return {"status": "sent"}

        return response.json()

