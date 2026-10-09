"""Entry point: `python -m robot_ops` starts the web app on 127.0.0.1:8000 by default."""

from __future__ import annotations

import uvicorn

from .config import Settings
from .main import create_app


def main() -> None:
    settings = Settings.from_env()
    if settings.host not in ("127.0.0.1", "localhost", "::1"):
        print(
            "WARNING: the application has no authentication; "
            f"binding to {settings.host} exposes it to the network."
        )
    uvicorn.run(create_app(), host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
