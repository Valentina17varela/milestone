import re
from enum import Enum

from fastapi import FastAPI


class ParameterTypes(str, Enum):
    path = "path"
    query = "query"


def routes_for_gateway(server: FastAPI):
    @server.get("/api/v1/routes")
    def get_routes():
        endpoints = {}
        for url, data in server.openapi_schema["paths"].items():
            url_endpoint = "/".join(url.split("/")[3:])
            endpoint = re.sub("/{.*?}", "", url_endpoint).replace("/", "_")
            info = {"methods": list(data.keys()), "url": url, "arguments": []}

            for key, value in data.items():
                if "parameters" in value:
                    parameters = value["parameters"]
                    # only add path arguments, do not add query arguments
                    arguments = list(
                        {
                            param["name"]
                            for param in parameters
                            if param["in"] == ParameterTypes.path
                        }
                    )
                    info["arguments"] = arguments
                else:
                    continue
            endpoints[endpoint] = info

        return endpoints
