from mirapi.responses import Response


def page_not_found() -> Response:
    """
    Return a 404 Not Found response.
    :return: The 404 response.
    """
    return Response('Not Found', status_code=404)


def method_not_allowed() -> Response:
    """
    Return a 405 Method Not Allowed response.
    :return: The 405 response.
    """
    return Response('Method Not Allowed', status_code=405)
