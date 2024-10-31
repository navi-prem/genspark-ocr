import os
import uuid

from azure.storage.blob import BlobServiceClient
from flask import jsonify


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def getResponse(message, status_code: int):
    return jsonify({"message": message}), status_code


"""
Uploads the contents of the file to azure blob storage
"""


@singleton
class BlobUploader:
    def __init__(self):
        self.conn_str = os.environ["CONNECTION_STRING"]
        self.kb_container_name = os.environ["KB_CONTAINER_NAME"]
        self.rag_container_name = os.environ["RAG_CONTAINER_NAME"]
        self.storage_account = os.environ["STORAGE_ACCOUNT"]
        if (
            self.conn_str == ""
            or self.kb_container_name == ""
            or self.rag_container_name == ""
            or self.storage_account == ""
        ):
            raise Exception("Connection String and Container Name cannot be empty!")
        self.blob_service = BlobServiceClient.from_connection_string(self.conn_str)
        self.kb_container_client = self.blob_service.get_container_client(
            self.kb_container_name
        )
        self.rag_container_client = self.blob_service.get_container_client(
            self.rag_container_name
        )

    """
    returns a unique uuid for the file which can be used to access the file
    format file_name+'$'+uuid

    file_path: local file path
    file_name: original name of the uploaded file
    key      : 'rag'|'kb'
    """

    def upload(self, file_path: str, file_name: str, key: str, **kwargs):
        tags = kwargs.get("tags")
        try:
            blob_name = file_name + "$" + str(uuid.uuid4())
            if key == "kb":
                blob_client = self.kb_container_client.get_blob_client(blob_name)
            elif key == "rag":
                blob_client = self.rag_container_client.get_blob_client(blob_name)
            else:
                raise Exception(f"Unsupported key format '{key}'.")

            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True, tags=tags)

            print(f"[INFO] File '{blob_name}' uploaded to Azure Blob Storage.")
            return blob_name
        except Exception as ex:
            print("[ERROR] Exception:", ex)

    """
    returns a list of all file names
    key= 'rag'|'kb'
    """

    def getAllFileNames(self, key: str):
        file_names = []
        if key == "kb":
            container_client = self.kb_container_client
        elif key == "rag":
            container_client = self.rag_container_client
        else:
            raise Exception(f"Unsupported key format '{key}'.")
        for file in container_client.list_blob_names():
            file_names.append(file)
        return file_names

    """
    returns the url of the bol
    blob_key    = key of the blob
    key         = 'rag'|'kb'
    """

    def getBlobUrl(self, blob_key: str, key: str):
        blob_key = blob_key.strip()
        if blob_key == "":
            raise Exception("Not valid blob_key!")
        if key == "rag":
            container_name = self.rag_container_name
        elif key == "kb":
            container_name = self.kb_container_name
        else:
            raise Exception("Not valid key")
        return f"https://{self.storage_account}.blob.core.windows.net/{container_name}/{blob_key}"
