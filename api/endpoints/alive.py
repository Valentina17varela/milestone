from fastapi import FastAPI


def set_up_alive(server: FastAPI):
    @server.get("/alive", status_code=200)
    async def is_alive():
        return True
