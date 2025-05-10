import os
import time
import docker.errors
import uvicorn
import docker
from .config import Config


def start() -> None:
    """
    Starts the dev Uvicorn server to run the FastAPI application.

    The server is configured to run on localhost (127.0.0.1) at port 8000
    with the reload option enabled for development purposes.
    """
    os.environ.setdefault("stage", "dev")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)


def start_prod() -> None:
    """
    Starts the prod Uvicorn server to run the FastAPI application.
    """
    os.environ.setdefault("stage", "prod")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000)


def start_db():
    """
    Spins up a PostgreSQL database locally using Docker.
    """
    client = docker.from_env()

    # Configuration for the PostgreSQL container
    container_name = "coachai-postgres-db"
    image = "postgres:latest"
    environment = {
        "POSTGRES_USER": Config.POSTGRES_USER,
        "POSTGRES_PASSWORD": Config.POSTGRES_PASSWORD,
        "POSTGRES_DB": Config.POSTGRES_DB,
    }
    ports = {f"{Config.POSTGRES_PORT}/tcp": int(Config.POSTGRES_PORT)}

    # Check if the container is already running
    try:
        container = client.containers.get(container_name)
        print(f"Container '{container_name}' is already running.")
        return
    except docker.errors.NotFound:
        pass

    # Check if the PostgreSQL image is already available
    try:
        client.images.get(image)
    except docker.errors.ImageNotFound:
        # Pull the PostgreSQL image if not already available
        print(f"Pulling Docker image '{image}'...")
        client.images.pull(image)

    # Run the PostgreSQL container
    print(f"Starting '{container_name}'...")
    container = client.containers.run(
        image,
        name=container_name,
        environment=environment,
        ports=ports,
        detach=True,
    )

    # Wait for the database to be ready
    expected_time: int = 30
    for _ in range(expected_time):  # Retry for up to expected_time seconds
        try:
            container.reload()
            if container.status == "running":
                print(f"PostgreSQL is running in container '{container_name}'.")
                break
        except docker.errors.APIError as e:
            print(f"Error checking container status: {e}")
        time.sleep(1)
    else:
        raise TimeoutError(
            f"PostgreSQL did not start within the expected time ({expected_time})."
        )
