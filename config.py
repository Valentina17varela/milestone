import os
import random
import string
from functools import lru_cache
from typing import Union

from pydantic import BaseSettings, PostgresDsn


class BaseConfig(BaseSettings):
    PRODUCTION: bool = os.getenv("PRODUCTION", False)
    project_name: str = "Heru API for milestone management"
    project_description: str = "Set of endpoints for milestone management"
    api_v1_route: str = "/api/v1"
    openapi_route: str = "/api/v1/openapi.json"

    MILESTONE_SERVICE = os.getenv("MILESTONE_SERVICE", "milestone")
    PLANS_SERVICE = os.getenv("PLANS_SERVICE", "plans")
    FINANCIALS_SERVICE = os.getenv("FINANCIALS_SERVICE", "financials")
    FISCAL_SERVICE = os.getenv("FISCAL_SERVICE", "fiscal")
    USERS_SERVICE = os.getenv("USERS_SERVICE", "users")

    MILESTONE_API_URL = f"http://{MILESTONE_SERVICE}/api/v1"
    PLANS_API_URL = f"http://{PLANS_SERVICE}/api/v1"
    FINANCIALS_API_URL = f"http://{FINANCIALS_SERVICE}/api/v1"
    FISCAL_API_URL = f"http://{FISCAL_SERVICE}/api/v1"
    USERS_API_URL = f"http://{USERS_SERVICE}/api/v1"


class DevelopmentConfig(BaseConfig):
    DB_URI: PostgresDsn = os.getenv(
        "MILESTONE_DB_URI", "postgresql://" "postgres:@postgresql/milestone_service"
    )

    SECRET_KEY: str = "dev"
    DEBUG: bool = True
    TESTING: bool = False


class TestingConfig(BaseConfig):
    DB_URI: str = "sqlite:///./test.db"

    SECRET_KEY: str = "testing"
    DEBUG: bool = True
    TESTING: bool = True


class ProductionConfig(BaseConfig):
    def random_string(stringLength=10):
        """Generate a random string of fixed length"""
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for i in range(stringLength))

    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT", 5432)
    DB_DATABASE: str = os.getenv("DB_DATABASE")

    DB_URI: PostgresDsn = os.getenv(
        "MILESTONE_DB_URI",
        f"postgresql://{DB_USER}:{DB_PASSWORD}" f"@{DB_HOST}:{DB_PORT}/{DB_DATABASE}",
    )

    SECRET_KEY: str = random_string()
    DEBUG: bool = False
    TESTING: bool = False


ConfigClass = Union[TestingConfig, DevelopmentConfig, ProductionConfig]


@lru_cache()
def get_settings() -> ConfigClass:
    prod = os.getenv("API_PRODUCTION", None)

    if prod:
        return ProductionConfig()
    else:
        return DevelopmentConfig()
