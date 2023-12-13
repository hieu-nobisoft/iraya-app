from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os

def get_client():
    account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    shared_access_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")
    credential = shared_access_key

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient(account_url, credential=credential)

    return blob_service_client
