from inspect import signature, getdoc
from typing import get_type_hints, Callable, Any, Dict, List

from pydantic import BaseModel
from mirapi.exceptions import HTTPException
from mirapi.requests import Request
from mirapi.responses import Response, JSONResponse, PlainTextResponse

from mirapi.errors import page_not_found
from mirapi.router import Router
from mirapi.types import OpenAPISpec, OpenAPIOperation, OpenAPIParameter


class MirAPI:
    def __init__(
            self,
            title: str = "MirAPI",
            version: str = "1.0.0",
            description: str = "",
            terms_of_service: str = "",
            contact: Dict[str, str] = None,
            license_info: Dict[str, str] = None,
            docs_url: str = "/docs",
            openapi_url: str = "/openapi.json",
            docs_enabled: bool = True
    ):
        self.router = Router()
        self.title = title
        self.version = version
        self.description = description
        self.terms_of_service = terms_of_service
        self.contact = contact or {}
        self.license_info = license_info or {}
        self.docs_url = docs_url
        self.openapi_url = openapi_url
        self.docs_enabled = docs_enabled

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
        """
        The ASGI application callable.
        :param scope: The ASGI scope.
        :param receive: The ASGI receive function.
        :param send: The ASGI send function.
        """
        if scope["type"] != "http":
            raise ValueError("Only HTTP requests are supported")

        request = Request(scope, receive)
        response = await self.handle_request(request)
        await response(scope, receive, send)

    async def handle_request(self, request: Request) -> Response:
        """
        Find the appropriate handler for the request and call it with the request object.
        :param request: The incoming request object.
        :return: The response object.
        """
        handler, kwargs = self.router.find_handler(request)
        if not handler:
            return page_not_found()

        sig = signature(handler)
        type_hints = get_type_hints(handler)

        for name, param in sig.parameters.items():
            if name != "request" and issubclass(type_hints.get(name, object), BaseModel):
                try:
                    json_data = await request.json()
                    kwargs[name] = type_hints[name](**json_data)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid request body: {str(e)}")
        response = await handler(request, **kwargs)
        if isinstance(response, (dict, list)):
            return JSONResponse(response)

        # Automatically convert str to PlainTextResponse
        if isinstance(response, str):
            return PlainTextResponse(response)

        return response

    def route(self, path: str, methods: List[str] = None) -> Callable:
        """
        Decorator that adds a new route to the router.
        :param path: The path of the route.
        :param methods: The HTTP methods that the route should respond to.
        :return: The decorator function.
        """
        if methods is None:
            methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'TRACE', 'CONNECT']

        def wrapper(func: Callable) -> Callable:
            self.router.add_route(path, func, methods)
            return func

        return wrapper

    def include_router(self, router: Router) -> None:
        """
        Include all routes from another router.
        :param router: The router object.
        """
        self.router.routes.extend(router.routes)

    def generate_openapi_spec(self) -> OpenAPISpec:
        paths: Dict[str, Dict[str, OpenAPIOperation]] = {}
        for route in self.router.routes:
            if route.path in [self.docs_url, self.openapi_url]:
                continue

            func = route.endpoint
            sig = signature(func)
            doc = getdoc(func) or ""
            type_hints = get_type_hints(func)

            path_item = paths.setdefault(route.path, {})
            for method in route.methods:
                method = method.lower()
                if method in ['head', 'options', 'trace', 'connect']:
                    continue

                parameters: List[OpenAPIParameter] = []
                request_body = None

                for name, param in sig.parameters.items():
                    if name != "request":
                        param_type = type_hints.get(name, str)
                        if issubclass(param_type, BaseModel):
                            request_body = {
                                "description": "Request body",
                                "content": {
                                    "application/json": {
                                        "schema": param_type.schema()
                                    }
                                }
                            }
                        else:
                            parameters.append({
                                "name": name,
                                "in": "path" if "{" + name + "}" in route.path else "query",
                                "required": True if "{" + name + "}" in route.path else False,
                                "schema": {"type": self._get_type_name(param_type)}
                            })

                operation: OpenAPIOperation = {
                    "summary": doc.split("\n")[0] if doc else "",
                    "description": doc,
                    "parameters": parameters,
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {"application/json": {}}
                        }
                    }
                }

                if request_body:
                    operation["requestBody"] = request_body

                path_item[method] = operation

        info = {
            "title": self.title,
            "version": self.version,
            "description": self.description,
        }
        if self.terms_of_service:
            info["termsOfService"] = self.terms_of_service
        if self.contact:
            info["contact"] = self.contact
        if self.license_info:
            info["license"] = self.license_info

        return {
            "openapi": "3.0.0",
            "info": info,
            "paths": paths
        }

    @staticmethod
    def _get_type_name(type_hint: Any) -> str:
        if hasattr(type_hint, '__origin__'):
            return type_hint.__origin__.__name__
        return type_hint.__name__

    def serve_swagger_ui(self) -> None:
        @self.get(self.docs_url)
        async def swagger_ui(request: Request) -> Response:
            if not self.docs_enabled:
                return page_not_found()
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>{self.title} - API Documentation</title>
                <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui.min.css" />
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        background-color: #f4f4f9;
                    }}
                    .swagger-ui .topbar {{
                        background-color: #4CAF50;
                    }}
                    .swagger-ui .info h1 {{
                        color: #4CAF50;
                    }}
                    .watermark {{
                        position: fixed;
                        bottom: 10px;
                        right: 10px;
                        font-family: Arial, sans-serif;
                        font-size: 18px;
                        color: #888;
                        opacity: 0.7;
                    }}
                </style>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/swagger-ui-bundle.min.js"></script>
            </head>
            <body>
                <div id="swagger-ui"></div>
                <div class="watermark">Created using MirAPI Framework</div>
                <script>
                    window.onload = function() {{
                        SwaggerUIBundle({{
                            url: "{self.openapi_url}",
                            dom_id: '#swagger-ui',
                            presets: [
                                SwaggerUIBundle.presets.apis,
                                SwaggerUIBundle.SwaggerUIStandalonePreset
                            ],
                            layout: "BaseLayout",
                            deepLinking: true,
                            showExtensions: true,
                            showCommonExtensions: true,
                            filter: true,
                            tryItOutEnabled: false,
                            supportedSubmitMethods: [],
                            onComplete: function() {{
                                // Hide the "Try it out" buttons
                                var tryItOutButtons = document.getElementsByClassName('try-out__btn');
                                for (var i = 0; i < tryItOutButtons.length; i++) {{
                                    tryItOutButtons[i].style.display = 'none';
                                }}
                            }}
                        }})
                    }}
                </script>
            </body>
            </html>
            """
            return Response(content=html_content, media_type="text/html")

        @self.get(self.openapi_url)
        async def openapi_spec(request: Request) -> JSONResponse:
            return JSONResponse(self.generate_openapi_spec())

    def get(self, path: str) -> Callable:
        """
        Decorator for adding a GET route.
        :param path: The path of the route.
        """
        return self.route(path, ['GET'])

    def post(self, path: str) -> Callable:
        """
        Decorator for adding a POST route.
        :param path: The path of the route.
        """
        return self.route(path, ['POST'])

    def put(self, path: str) -> Callable:
        """
        Decorator for adding a PUT route.
        :param path: The path of the route.
        """
        return self.route(path, ['PUT'])

    def patch(self, path: str) -> Callable:
        """
        Decorator for adding a PATCH route.
        :param path: The path of the route.
        """
        return self.route(path, ['PATCH'])

    def delete(self, path: str) -> Callable:
        """
        Decorator for adding a DELETE route.
        :param path: The path of the route.
        """
        return self.route(path, ['DELETE'])

    def head(self, path: str) -> Callable:
        """
        Decorator for adding a HEAD route.
        :param path: The path of the route.
        """
        return self.route(path, ['HEAD'])

    def options(self, path: str) -> Callable:
        """
        Decorator for adding an OPTIONS route.
        :param path: The path of the route.
        """
        return self.route(path, ['OPTIONS'])

    def trace(self, path: str) -> Callable:
        """
        Decorator for adding a TRACE route.
        :param path: The path of the route.
        """
        return self.route(path, ['TRACE'])

    def connect(self, path: str) -> Callable:
        """
        Decorator for adding a CONNECT route.
        :param path: The path of the route.
        """
        return self.route(path, ['CONNECT'])

class APIRouter:
    def __init__(self):
        self.router = Router()  # Internal router to manage routes

    def add_route(self, path: str, handler: Callable, methods: List[str]) -> None:
        """Add a new route to the router."""
        self.router.add_route(path, handler, methods)

    def get(self, path: str) -> Callable:
        """Decorator for adding a GET route."""
        return self._add_method_route(path, ['GET'])

    def post(self, path: str) -> Callable:
        """Decorator for adding a POST route."""
        return self._add_method_route(path, ['POST'])

    def put(self, path: str) -> Callable:
        """Decorator for adding a PUT route."""
        return self._add_method_route(path, ['PUT'])

    def patch(self, path: str) -> Callable:
        """Decorator for adding a PATCH route."""
        return self._add_method_route(path, ['PATCH'])

    def delete(self, path: str) -> Callable:
        """Decorator for adding a DELETE route."""
        return self._add_method_route(path, ['DELETE'])

    def head(self, path: str) -> Callable:
        """Decorator for adding a HEAD route."""
        return self._add_method_route(path, ['HEAD'])

    def options(self, path: str) -> Callable:
        """Decorator for adding an OPTIONS route."""
        return self._add_method_route(path, ['OPTIONS'])

    def trace(self, path: str) -> Callable:
        """Decorator for adding a TRACE route."""
        return self._add_method_route(path, ['TRACE'])

    def connect(self, path: str) -> Callable:
        """Decorator for adding a CONNECT route."""
        return self._add_method_route(path, ['CONNECT'])

    def _add_method_route(self, path: str, methods: List[str] = None) -> Callable:
        """Helper to add routes with specified methods."""
        def wrapper(func: Callable) -> Callable:
            self.add_route(path, func, methods)  # Add the route
            return func

        return wrapper

    @property
    def routes(self):
        """Expose routes for the MirAPI class."""
        return self.router.routes
