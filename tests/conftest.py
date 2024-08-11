import os

import pytest
from minio import Minio

from tiny_s3 import Client


def get(var: str) -> str:
    """Get value from env or fail."""

    value = os.environ.get(var)
    assert value, f"Variable {var} is unset!"
    return value


@pytest.fixture(name="s3_endpoint", scope="session")
def fx_s3_endpoint() -> str:
    return get("S3_HOST")


@pytest.fixture(name="s3_url", scope="session")
def fx_s3_url(s3_endpoint: str) -> str:
    return f"http://{s3_endpoint}"


@pytest.fixture(name="bucket", scope="session")
def fx_bucket() -> str:
    return get("S3_BUCKET")


@pytest.fixture(name="minio")
def fx_minio(s3_endpoint: str) -> Minio:
    return Minio(
        endpoint=s3_endpoint,
        access_key=get("S3_ACCESS_KEY"),
        secret_key=get("S3_SECRET_KEY"),
        secure=False,
    )


@pytest.fixture(autouse=True)
def create_bucket(minio: Minio, bucket: str) -> None:
    if not minio.bucket_exists(bucket):
        minio.make_bucket(bucket)


@pytest.fixture(name="client")
def create_client(s3_url: str, bucket: str) -> Client:
    return Client(
        url=s3_url,
        access_key=get("S3_ACCESS_KEY"),
        secret_key=get("S3_SECRET_KEY"),
        bucket=bucket,
    )
