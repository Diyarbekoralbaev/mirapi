from typing import Tuple, Dict, Callable, Optional, List
from parse import parse
from starlette.routing import Route

from mirapi.exceptions import RouteAlreadyExistsError
from mirapi.requests import Request


class Router:
    def __init__(self):
        self.routes: List[Route] = []

    def add_route(self, path: str, handler: Callable, methods: List[str]) -> None:
        """
        Add a new route to the router.
        :param path: The path of the route.
        :param handler: The handler class or function.
        :param methods: The HTTP methods.
        """
        for route in self.routes:
            if route.path == path and any(method in route.methods for method in methods):
                raise RouteAlreadyExistsError(path, methods)

        self.routes.append(Route(path, handler, methods=methods))

    def find_handler(self, request: Request) -> Tuple[Optional[Callable], Dict[str, str]]:
        """
        Find the handler for the request.
        :param request: The incoming request object.
        :return: A tuple containing the handler and the named path parameters.
        """
        for route in self.routes:
            match = parse(route.path, request.url.path)
            if match and request.method in route.methods:
                handler = route.endpoint
                if isinstance(handler, type):
                    handler_instance = handler()
                    method_handler = getattr(handler_instance, request.method.lower(), None)
                    if method_handler:
                        return method_handler, match.named
                else:
                    return handler, match.named

        return None, {}
