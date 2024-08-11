from io import BytesIO

from minio import Minio

from tiny_s3 import Client


def test_list_objects(client: Client, minio: Minio, bucket: str):

    victim = "foo.txt"

    minio.put_object(
        bucket_name=bucket,
        object_name=victim,
        data=BytesIO(b""),
        length=0,
    )

    objs = [f["Key"] for f in client.list_objects()]

    assert victim in objs
