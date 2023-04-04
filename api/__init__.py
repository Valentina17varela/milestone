from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from api.custom.openapi import custom_openapi
from api.db.base import Base
from api.db.session import engine
from api.endpoints import router
from api.endpoints.alive import set_up_alive
from api.routes import routes_for_gateway
from api.repositories.exceptions import APIException
from config import get_settings


def get_app() -> FastAPI:

    # inspired from https://github.com/tiangolo/fastapi/issues/508#issuecomment-532368194
    settings = get_settings()  # see example above

    server = FastAPI(
        title=settings.project_name,
        openapi_url=settings.openapi_route,
        debug=settings.DEBUG,
    )

    @server.get("/", include_in_schema=False)
    def redirect_to_docs() -> RedirectResponse:
        return RedirectResponse("/docs")

    server.include_router(router, prefix="/api/v1/milestones")

    server.openapi_schema = custom_openapi(server, settings)
    routes_for_gateway(server)
    set_up_alive(server)

    @server.exception_handler(APIException)
    async def client_exception_handler(request: Request, exc: APIException):
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "http_status": exc.http_status,
                "message": exc.message,
                "internal_code": exc.internal_code,
            },
        )

    return server
