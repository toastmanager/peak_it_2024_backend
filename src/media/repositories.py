from typing import BinaryIO
import uuid
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager

from aiobotocore.session import get_session


class MediaRepository(ABC):
    @abstractmethod
    async def upload_object(
        self, object_key: str, file: bytes | BinaryIO, generate_prefix: bool = True
    ) -> str:
        """
        Uploads object to storage and returns object key

        :param generate_prefix: Generates prefix if set to True.
        """
        raise NotImplementedError
    
    async def replace_object(self, object_key: str, file: bytes | BinaryIO) -> str:
        """
        Replace object with [object_key] with given [file]
        """

        raise NotImplementedError

    @abstractmethod
    async def delete_objects(self, objects_keys: list[dict[str, str]]) -> None:
        """
        Deletes an object by its key

        :param objects_keys: dictionary with objects keys. Example: [{"Key": "object_name"}, {"Key": "script/py_script.py"}]
        """
        raise NotImplementedError

    @abstractmethod
    async def get_object(self, object_key: str) -> bytes:
        """
        Returns dictionary with file metadata and contents by object key
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[bytes]:
        """
        Returns dictionary list with files metadata
        """
        raise NotImplementedError


class S3Repository(MediaRepository):
    def __init__(
        self, access_key: str, secret_key: str, endpoint_url: str, bucket_name: str
    ) -> None:
        super().__init__()
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_object(
        self, object_key: str, file: BinaryIO, generate_prefix: bool = True
    ) -> str:
        object_key = object_key.replace(" ", "_")
        if generate_prefix:
            object_key = uuid.uuid4().hex + "_" + object_key
        try:
            async with self.get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name, Key=object_key, Body=file
                )  # type: ignore
                return object_key
        except Exception as e:
            raise e
        
    async def replace_object(self, object_key: str, file: BinaryIO) -> str:
        return await self.upload_object(object_key=object_key, file=file, generate_prefix=False)

    async def delete_objects(self, objects_keys: list[dict[str, str]]) -> None:
        try:
            async with self.get_client() as client:
                await client.delete_objects(
                    Bucket=self.bucket_name, Delete={"Objects": objects_keys}
                )  # type: ignore
        except Exception as e:
            raise e

    async def get_object(self, object_key: str) -> bytes:
        try:
            async with self.get_client() as client:
                file = await client.get_object(Bucket=self.bucket_name, Key=object_key)  # type: ignore
                async with file["Body"] as stream:
                    return await stream.read()
        except Exception as e:
            raise e

    async def get_all(self) -> list[bytes]:
        try:
            async with self.get_client() as client:
                return (await client.list_objects(Bucket=self.bucket_name))["Contents"]  # type: ignore
        except Exception as e:
            raise e
