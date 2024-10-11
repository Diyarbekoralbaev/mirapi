from typing import List
from starlette.exceptions import *

class RouteAlreadyExistsError(Exception):
    def __init__(self, path: str, method: List[str]):
        """
        Exception for when a route already exists.
        :param path: The path of the route.
        :param method: The method(s) of the route.
        """
        super().__init__(f"Route for {path} with method(s) {', '.join(method)} already exists")
