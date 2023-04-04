import requests
import logging
from config import get_settings


def get_products(user_id):
    settings = get_settings()
    endpoint = f"{settings.PLANS_API_URL}/products/{user_id}/acquisitions"
    try:
        rv = requests.get(endpoint)
        rv.raise_for_status()
    except requests.exceptions.ConnectionError:
        logging.info({"message": "Plans service unavailable"})
        return None
    except requests.HTTPError as e:
        logging.info({"message": f"Plans service error: {e}"})
        return None
    return rv.json()


def product_by_id(product_id):
    settings = get_settings()
    endpoint = f"{settings.PLANS_API_URL}/products/{product_id}"
    try:
        rv = requests.get(endpoint)
        rv.raise_for_status()
    except requests.exceptions.ConnectionError:
        logging.info({"message": "Plans service unavailable"})
        return None
    except requests.HTTPError as e:
        logging.info({"message": f"Plans service error: {e}"})
        return None
    return rv.json()
