import uvicorn

from app.config import settings
from app.main import app


def main() -> None:
    uvicorn.run(app, host=settings.backend_host, port=settings.backend_port)


if __name__ == "__main__":
    main()
