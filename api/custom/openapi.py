from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(server: FastAPI, settings):
    if server.openapi_schema:
        return server.openapi_schema
    openapi_schema = get_openapi(
        title=settings.project_name,
        version="0.1.0",
        description=settings.project_description,
        routes=server.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": (
            "https://lh3.googleusercontent.com/CkFCxXDWB4V_VlZxLln8hrx7d-9JKzgt2sSlXFlfI8xbjH"
            "MZ12L5oskEs6nn3TU1PWAFJZgZa7C4fU0ZzU8Wjh1RTmqS0Dbyfk00KY2cISm5qrjvoPFwhBL8DBsyaS"
            "Fy6SdfFeSH-cRcpfEGRnch2mE06-ZP-u4fbAZExRMstaloYV8chv8QtmfDtTIJtsZybdkDwJf29BYiIG"
            "ynLjydHP5H8lMgB2CXhCMabUZCGODFgOyDYeo-lWdLthncf2ujl61XY93jYdcb_fmOcnvpi3c8oEt6gc"
            "XxUgXKJN0W-DZEQcOpul6Mz_au7qtmUS6yfYJtiJAp7wmCCAsDCljXj35s37nFc8mHdpDKj6fyX2cdRJ"
            "BgA0iOMD0O9cdeQ8iscTIham_HdcjzugNUiZTtb0wb5KGTbxgT6k70CoPentklxnz4dPwW9M47Oih8Fo"
            "tUiAejML1aiGXMgVJRbzIH7-jHW-9w8VfuT-_Tx617rW0AGV3KErAje8rHV1Arap3c0jK6cY-wEI9Tuo"
            "fT8WSNWHp9huZvdFdRbjfESQIIXzT9EbjG3_PObmVlX_hYRwmxWjAfsRkyPgJhp3BiiPtItHsxLTCuJd"
            "e61mhcCNq57aC1z5W7IuhrYZMItNeDsbtd0CHK_cCmm5gsXCA1bQU32t_b223KPkUvjvtqxzd67rCW_6"
            "L8yh1n3xvjRd2YDbBji5Y3vA=w2880-h1392-ft"
        )
    }
    server.openapi_schema = openapi_schema
    return server.openapi_schema
