import os, uuid
#from posix import F_TEST
from base64 import b64decode
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

class Librarian:
    def __init__(self):
        self.__connect_str="DefaultEndpointsProtocol=https;AccountName=filesmanager070901;AccountKey=nmLzOCpdqPqKAAeZkkqLTURUMynvoANaFZ9w6zZaPLWFUeFvHBt+uSS9nnXtZMTpBB8Beg3680An7AVdNSX5Sg==;EndpointSuffix=core.windows.net"
        self.__id = ""
        self.__url = ""
        self.__container = ""
       
    def create_id(self, f_extension):
        self.set_id(str(uuid.uuid4())+'.'+f_extension)
        self.set_url("https://filesmanager070901.blob.core.windows.net/"+self.__container+"/" + self.get_id())

    def open_connection(self):
        self.__blob_service = BlobServiceClient.from_connection_string(self.__connect_str)

    def upload_file(self, b64):
        
        bits = b64decode(b64, validate=True)
        f = open(self.get_id(), 'wb')
        f.write(bits)
        f.close()

        # Create a blob client using the local file name as the name for the blob
        blob_client = self.__blob_service.get_blob_client(container=self.__container, blob=self.get_id())

        print("\nUploading to Azure Storage as blob:\n\t" + self.get_id())

        # Upload the created file
        with open(self.get_id(), "rb") as data:
            blob_client.upload_blob(data)

        print("Image uploaded at: " + self.get_url())

        os.remove(self.get_id())
    
    def delete_file(self, blob_id):
        blob_client = self.__blob_service.get_blob_client(container=self.__container, blob=blob_id)
        blob_client.delete_blob()


    def set_id(self, id):
        self.__id = id
    
    def set_container(self, container):
        self.__container = container
    
    def set_url(self, url):
        self.__url = url
    
    def get_id(self):
        return self.__id

    def get_url(self):
        return self.__url
