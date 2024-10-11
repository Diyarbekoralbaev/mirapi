from typing import Dict, Any, TypedDict


class OpenAPIParameter(TypedDict):
    name: str
    location: str
    required: bool
    schema: Dict[str, Any]


class OpenAPIOperation(TypedDict, total=False):
    summary: str
    description: str
    parameters: list[OpenAPIParameter]
    requestBody: Dict[str, Any]
    responses: Dict[str, Dict[str, Any]]


class OpenAPISpec(TypedDict):
    openapi: str
    info: Dict[str, str]
    paths: Dict[str, Dict[str, OpenAPIOperation]]
