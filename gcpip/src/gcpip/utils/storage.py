import logging
import datetime as dt
import numpy as np
from google.cloud import storage
from google.oauth2 import service_account
from google.api_core.exceptions import Conflict


logger = logging.getLogger(__name__)


def get_storage_client(key_file):
    """
    This method create google storage client connection.
    Args:
        key_file (JSON): Google Cloud Key (Credential) file

    Returns (storage.Client): client object.

    """

    credentials = service_account.Credentials.from_service_account_file(
        key_file, scopes=["https://www.googleapis.com/auth/cloud-platform"])
    client = storage.Client(
        project=credentials.project_id, credentials=credentials)

    return client


def create_bucket(storage_client, project_name, bucket_name, location=None,
                  find_unique_name=True):
    """
    Creates GCS bucket

    Args:
        storage_client (storage.Client): GCP storage client object
        project_name (str): Project ID
        bucket_name (str): Bucket name
        location (str, optional): Location of bucket. Defaults to None.
        find_unique_name (bool, optional):
            If bucket name conflict will attempt to find unique name.
            Defaults to True.

    Returns:
        str: Bucket resource name
    """

    logger.debug("Creating bucket: {}".format(bucket_name))

    try:
        response = storage_client.create_bucket(
            bucket_name, project=project_name)
    except Conflict:
        bucket_name = (
            bucket_name + project_name + str(dt.datetime.now().date())
            + str(np.random.randint(1000, 9999)))
        response = storage_client.create_bucket(
            bucket_name, project=project_name)

    return response.name


def delete_bucket(storage_client, project_name, bucket_name, force=False):
    """
    Removes bucket

    Args:
        storage_client (storage.Client): GCP storage client object
        project_name (str): Project ID
        bucket_name (str): Bucket name
        force (bool, optional): Force remove all files from bucket.
            Defaults to False.
    """

    logger.debug("Deleting bucket: {}".format(bucket_name))

    bucket = storage_client.get_bucket(bucket_name)
    bucket.delete(force=force)


def download_gcs_file(storage_client, bucket_name, blob_path,
                      destination_path):
    """
    Downloads GCS blob as local file

    Args:
        storage_client (storage.Client): GCP storage client object
        bucket_name (str): Bucket name
        blob_path (str): Path to blob within bucket
        destination_file_name (str): Local path to download file
    """

    logger.debug("Downloading blob: {} to: {}".format(
        blob_path, destination_path))

    bucket = storage_client.get_bucket(bucket_name)
    blob = storage.Blob(blob_path, bucket)

    with open(destination_path, "wb") as file_obj:
        storage_client.download_blob_to_file(blob, file_obj)


def load_gcs_object(storage_client, bucket_name, blob_path):
    """
    Loads blob object as bytes

    Args:
        storage_client (storage.Client): GCP storage client object
        bucket_name (str): Bucket name
        blob_path (str): Path to blob within bucket

    Returns:
        bytes: blob object contents
    """

    logger.debug("Loading GCS object: {}".format(
        blob_path))

    bucket = storage_client.get_bucket(bucket_name)
    blob = storage.Blob(blob_path, bucket)

    return blob.download_as_string()


def delete_blob(storage_client, bucket_name, blob_path):
    """
    Deletes blob object from a given bucket

    Args:
        storage_client (storage.Client): GCP storage client object
        bucket_name (str): Bucket name
        blob_path (str): Path to blob within bucket
    """

    logger.debug("Deleting blob: {} from bucket: {}".format(
        bucket_name, blob_path))

    bucket = storage_client.get_bucket(bucket_name)
    blob = storage.Blob(blob_path, bucket)
    blob.delete()


def get_gcs_url(source_bucket, source_path):

    return "gs://" + source_bucket + "/" + source_path
