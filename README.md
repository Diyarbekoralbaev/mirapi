# MirAPI

[![PyPI version](https://img.shields.io/pypi/v/mirapi.svg)](https://pypi.org/project/mirapi/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mirapi.svg)](https://pypi.org/project/mirapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![PyPI Downloads](https://img.shields.io/pypi/dm/mirapi)
<p align="center">
  <a href="https://tirikchilik.uz/araltech">
    <img src="https://camo.githubusercontent.com/ed28339e5a5786534715b1c0c885271437761fc91af84d5dc5bbc2c71e307a02/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f546972696b6368696c696b2d6666646430303f7374796c653d666f722d7468652d6261646765" alt="Donate with Tirikchilik">
  </a>
</p>
MirAPI is a lightweight, fast, and easy-to-use ASGI-based Python web framework for building APIs. It's designed to be simple yet powerful, allowing developers to quickly create robust asynchronous web applications and RESTful APIs with automatic OpenAPI (Swagger) documentation.

## Features

- ASGI-based for high performance and scalability
- Easy-to-use routing system
- Automatic OpenAPI (Swagger) documentation generation
- Built-in support for JSON responses
- Type hinting and Pydantic model integration
- Lightweight and fast asynchronous application
- Customizable error handling
- Support for all standard HTTP methods
- **New**: class-based handlers for route management
- **New**: Added `APIRouter` for modular route management and composition.
- **New**: Introduced `include_router` method for integrating external routers seamlessly.

## Installation

You can install MirAPI using pip:

```bash
pip install mirapi
```

## Quick Start

Here's a simple example to get you started with MirAPI:

```python
from mirapi import MirAPI
from pydantic import BaseModel

app = MirAPI(title="My API", version="1.0.0")

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.post("/items")
async def create_item(item: Item):
    return {"item": item, "message": "Item created successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

This example creates a simple asynchronous API with two endpoints: a GET route at the root path and a POST route for creating items.

## Advanced Usage

### Route Parameters

MirAPI supports path parameters in your routes:

```python
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id}
```

### Request Body Validation

Use Pydantic models to validate request bodies:

```python
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    age: int

@app.post("/users")
async def create_user(user: User):
    return {"user": user, "message": "User created successfully"}
```

### Error Handling

MirAPI provides built-in error handling, but you can also customize error responses:

```python
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

@app.route("/custom_error")
async def custom_error(request):
    raise HTTPException(status_code=400, detail="Custom error message")

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
```

## Documentation

MirAPI automatically generates OpenAPI (Swagger) documentation for your API. You can access the interactive API documentation by navigating to `/docs` in your browser when running your application.

## Dependencies

MirAPI depends on the following packages:

- starlette (0.39.2)
- parse (1.20.2)
- uvicorn (0.31.1)
- pydantic (2.9.2)

These dependencies will be automatically installed when you install MirAPI.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support
If you like this project, please consider supporting it by making a donation:
<p align="center">
  <a href="https://tirikchilik.uz/araltech">
    <img src="https://camo.githubusercontent.com/ed28339e5a5786534715b1c0c885271437761fc91af84d5dc5bbc2c71e307a02/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f546972696b6368696c696b2d6666646430303f7374796c653d666f722d7468652d6261646765" alt="Donate with Tirikchilik">
  </a>
</p>

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Diyarbekoralbaev/mirapi/LICENSE) file for details.

## Acknowledgments

- Inspired by modern ASGI-based Python web frameworks
- Built with love for the Python community

For more detailed information and advanced usage, please refer to the [documentation](https://mirapi.readthedocs.io).
