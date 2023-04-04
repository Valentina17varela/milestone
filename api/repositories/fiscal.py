import requests
import logging
import httpx
from config import get_settings


async def validate_submitted_anual_declaration(user_id, year):
    settings = get_settings()
    endpoint = (
        f"{settings.FISCAL_API_URL}/fiscal/annual_declaration/{user_id}/period/{year}"
    )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError:
        logging.info({"message": "Fiscal service unavailable"})
        return None
    except httpx.HTTPError as e:
        logging.info({"message": f"Fiscal service error: {e}"})
        return None


async def user_declaration(user_id):
    settings = get_settings()
    endpoint = f"{settings.FISCAL_API_URL}/fiscal/users/{user_id}/declarations/status"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logging.info({"message": f"Fiscal service error: {e}"})
            return None


async def validate_acuse_retool(user_id):
    settings = get_settings()
    endpoint = f"{settings.FISCAL_API_URL}/fiscal/users/{user_id}/declarations/declaration-documents"
    try:
        async with httpx.AsyncClient() as client:
            rv = await client.get(endpoint)
            rv.raise_for_status()
    except httpx.RequestError:
        logging.info({"message": "Fiscal service unavailable"})
        return None
    except httpx.HTTPError as e:
        logging.info({"message": f"Fiscal service error: {e}"})
        return None
    return rv.json()
