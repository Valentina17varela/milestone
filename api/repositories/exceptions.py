from typing import List, Union


class APIException(Exception):
    def __init__(self, http_status: int, message: Union[List[str], str], internal_code):
        self.http_status = http_status
        self.message = message
        self.internal_code = internal_code
