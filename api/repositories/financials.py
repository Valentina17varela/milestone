import logging
import httpx
from config import get_settings


async def get_links_by_user_id(user_id: int):
    settings = get_settings()
    endpoint = f"{settings.FINANCIALS_API_URL}/financials/users/{user_id}/links/satws"
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            response = await client.get(endpoint)
            response.raise_for_status()
        except httpx.HTTPError as e:
            logging.info({"message": f"Financials service error: {e}"})
            return None
        except httpx.TimeoutException:
            logging.info({"message": "Financials service request timed out"})
            return None
        body = response.json()
        status = body.get("status")
        credentials = body.get("linked")
        result = [status, credentials]
        return result


async def get_regime_by_user_id(user_id: int):
    settings = get_settings()
    endpoint = f"{settings.FINANCIALS_API_URL}/financials/users/{user_id}/regime"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logging.info({"message": f"Financial service error: {e}"})
            return None
