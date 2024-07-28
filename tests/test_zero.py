from tiny_s3 import Client


def test_list_objects(client: Client):
    objs = list(client.list_objects())

    print(objs)

    assert "foo.txt" in objs
