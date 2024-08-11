import base64
import hmac
import logging
from datetime import datetime, timezone
from hashlib import sha1
from typing import Any, Iterator, Optional
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import requests

_LOGGER = "tiny-s3"
_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S +0000"

log = logging.getLogger(_LOGGER)

Params = dict[str, str]
Headers = dict[str, str]
Item = dict[str, Optional[str]]


class Client:
    def __init__(self, url: str, access_key: str, secret_key: str, bucket: str) -> None:
        self.base_url = url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket

    def request(
        self,
        key: str = "",
        data: Any = None,
        method: str = "GET",
        params: Optional[Params] = None,
    ) -> requests.Response:
        full_key = f"{self.bucket}/{key}"
        headers = self.create_aws_headers(full_key, method)
        # headers["Content-type"] = "application/json"

        return requests.request(
            method,
            f"{self.base_url}/{full_key}",
            headers=headers,
            data=data,
            stream=True,
            timeout=10,
            params=params,
        )

    def create_aws_headers(self, full_key: str, method: str) -> Headers:
        """
        create aws headers with authorization logic documented at
        https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html#signing-request-intro
        :param key: String path of where the file will be accessed
        :param method: String method of the type of request
        :return: dict of headers
        """
        # Current time needs to be within 10 minutes of the S3 Server
        date = datetime.now(timezone.utc).strftime(_DATE_FORMAT)
        string_to_sign = f"{method}\n\n\n{date}\n/{full_key}".encode("UTF-8")

        log.debug(string_to_sign)
        signature = (
            base64.encodebytes(
                hmac.new(self.secret_key.encode("UTF-8"), string_to_sign, sha1).digest()
            )
            .strip()
            .decode()
        )
        signature = f"AWS {self.access_key}:{signature}"
        log.debug(signature)

        # Date is needed as part of the authorization
        return {
            "Authorization": signature,
            "Date": date,
        }

    def list_objects(self) -> Iterator[Item]:
        respose = self.request()

        root = ElementTree.fromstring(respose.text)
        for item in (child for child in root if child.tag.endswith("}Contents")):
            yield _to_dict(item)


def _key(text: str, sep="}") -> str:
    if sep in text:
        return text.split(sep, 1)[1]
    return text


def _to_dict(item: Element) -> Item:
    return {_key(attr.tag): attr.text for attr in item}
