import os

import uvicorn


def main() -> None:
    host = os.environ.get("ARGUS_BACKEND_HOST")
    port_text = os.environ.get("ARGUS_BACKEND_PORT")
    if not host or not port_text:
        raise SystemExit("Defina ARGUS_BACKEND_HOST e ARGUS_BACKEND_PORT para iniciar o backend.")

    uvicorn.run("app.main:app", host=host, port=int(port_text), workers=1)


if __name__ == "__main__":
    main()
