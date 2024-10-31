from flask import jsonify
from azure.storage.blob import BlobServiceClient 
import os
import uuid

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

def getResponse(message,status_code:int):
    return jsonify({ "message": message}), status_code

"""
Uploads the contents of the file to azure blob storage
Requires the file name to be unique
"""
@singleton
class BlobUploader:
    def __init__(self):
        self.conn_str=os.environ["CONNECTION_STRING"]
        self.container_name=os.environ["CONTAINER_NAME"]
        if(self.conn_str=="" or self.container_name ==""):
            raise Exception("Connection String and Container Name cannot be empty!")
        self.blob_service= BlobServiceClient.from_connection_string(self.conn_str)
        self.container_client = self.blob_service.get_container_client(self.container_name)

    """
    returns a unique uuid for the file which can be used to access the file
    format file_name+'$'+uuid
    the above thing is done for uniqueness
    """
    def upload(self,file_path:str,file_name:str):
        try:
            blob_name = file_name+'$'+str(uuid.uuid4())
            blob_client = self.container_client.get_blob_client(blob_name)

            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
            print(f"[INFO] File '{blob_name}' uploaded to Azure Blob Storage.")
            return blob_name
        except Exception as ex:
            print("[ERROR] Exception:", ex)
    
    """
    returns a list of all file names
    """
    def getAllFileNames(self):
        file_names=[]
        for file in self.container_client.list_blob_names():
            file_names.append(file.split('$')[0])
        return file_names
