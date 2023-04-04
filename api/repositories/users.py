import requests
import logging
from config import get_settings


def get_link_form(user_id):
    settings = get_settings()
    endpoint = f"{settings.USERS_API_URL}/users/{user_id}/validate-rfc"
    try:
        rv = requests.get(endpoint)
        rv.raise_for_status()
    except requests.exceptions.ConnectionError:
        logging.info({"message": "Users service unavailable"})
        return None
    except requests.HTTPError as e:
        logging.info({"message": f"Users service error: {e}"})
        return None
    return rv.json()


def user_form_submission(user_id, form_id):
    settings = get_settings()
    endpoint = f"{settings.USERS_API_URL}/users/{user_id}/form-submission/{form_id}"
    try:
        rv = requests.get(endpoint)
        rv.raise_for_status()
    except requests.exceptions.ConnectionError:
        logging.info({"message": "Users service unavailable"})
        return None
    except requests.HTTPError as e:
        logging.info({"message": f"Users service error: {e}"})
        return None
    return rv.json()
