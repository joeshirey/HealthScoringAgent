"""
This script provides a convenient way to run the FastAPI application for
local development.
"""

import uvicorn


def main() -> None:
    """
    Starts the Uvicorn server with hot-reloading enabled.

    This is the recommended way to run the application during development, as
    it will automatically restart the server whenever code changes are detected.
    """
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8090,
        reload=True,
        timeout_graceful_shutdown=60,
    )


if __name__ == "__main__":
    main()
