import logging
import os
from pathlib import Path
from gcpip.upload.encryption import (
    generate_key, encrypt_file, encrypt_dek, decrypt_dek, decrypt_file)
from gcpip.utils.encryption import (
    create_kms_key, create_kms_key_ring, get_kms_key_rings, get_kms_keys)
from gcpip.utils.storage import (
    download_gcs_file, load_gcs_object, delete_blob)

logger = logging.getLogger(__name__)


def upload_file(storage_client, bucket_name, source_file_name,
                destination_name):
    """
    This method upload a given file into google bucket storage.

    Args:
        storage_client(storage.Client): client object
        bucket_name (str): Google Cloud Bucket Name
        source_file_name (str): Input file to upload.
        destination_name (str): Destination directory and file name.
    """

    bucket = storage_client.get_bucket(bucket_name)

    uploader = bucket.blob(destination_name)
    uploader.upload_from_filename(source_file_name)

    logger.info('File {} uploaded to {}.'.format(
        source_file_name, destination_name))


def encrypt_upload_file(
        storage_client, kms_client, bucket_name, source_file_name,
        destination_name, project_id, location_id, key_ring_id, key_id):
    """
    Encrypts a file and uploads the file and wrapped data encryption key (DEK)
        to google cloud storage.
    File is encrypted with the DEK and DEK is encrypted with GCP KMS key.
    Both encrypted data and DEK will be uploaded to bucket with DEK named
        after file w/ .dek extension
    More detail on envelope encryption here:
        https://cloud.google.com/kms/docs/envelope-encryptions

    Args:
        storage_client (storage.Client): GCS client object
        kms_client (kms_v1.KeyManagementServiceClient): GCP KMS client object
        bucket_name (str): Name of bucket to upload files into
        source_file_name (str): Name of local file to upload
        destination_name (str): Name for uploaded file within bucket
        project_id (str): Name of GCP project
        location_id (str): KMS key location
        key_ring_id (str): KMS key ring ID
        key_id (str): KMS key ID
    """

    logger.info(
        "Uploading encrypted data: {} and DEK to GCS bucket: {}"
        .format(source_file_name, bucket_name))

    # Create DEK
    dek = generate_key()

    # Encrypt target file
    encrypt_file(source_file_name, dek)

    # Check key ring exists and create if not
    key_rings = get_kms_key_rings(
        kms_client, project=project_id, location_id=location_id)
    if key_ring_id not in key_rings:
        create_kms_key_ring(kms_client, project_id, location_id,
                            key_ring_id)

    # Check key exists and create if not
    keys = get_kms_keys(kms_client, project=project_id,
                        location_id=location_id, key_ring_id=key_ring_id)
    if key_id not in keys:
        create_kms_key(kms_client, project_id, location_id,
                       key_ring_id, key_id)

    # Encrypt DEK
    dek_encrypted = encrypt_dek(kms_client, dek, project_id, location_id,
                                key_ring_id, key_id)

    # Upload encrypted file to GCS bucket
    logger.debug("Uploading encrypted file to bucket")
    bucket = storage_client.get_bucket(bucket_name)
    uploader = bucket.blob(destination_name + ".encrypted")
    uploader.upload_from_filename(source_file_name + ".encrypted")

    # Upload encrypted DEK and KEK path to GCS bucket
    logger.debug("Uploading encrypted DEK to bucket")

    # kms_key_path = get_kms_key_path(
    #     kms_client, project_id, location_id, key_ring_id, key_id)

    # dek_kek = dek_encrypted + b" " + bytes(kms_key_path, 'utf-8')
    # dek_kek = dek_encrypted + bytes(kms_key_path, 'utf-8')

    dek_blob = bucket.blob(destination_name + ".dek")
    dek_blob.upload_from_string(dek_encrypted)
    # kek_blob = bucket.blob(destination_name + ".kek")
    # kek_blob.upload_from_string(kms_key_path)

    # Remove encrypted file
    logger.debug("Removing encrypted file: {}".format(source_file_name))
    os.remove(source_file_name + ".encrypted")


def decrypt_blob(
        storage_client, kms_client, bucket_name, blob_path,
        project_id, location_id, key_ring_id, key_id, temp_data='temp_dir'):
    """
    Decrypts an encrypted blob and saves decrypted data to GCS
    File must have been uploaded to GCS w/ wrapped DEK key
    More detail on envelope encryption here:
        https://cloud.google.com/kms/docs/envelope-encryptions

    Args:
        storage_client (storage.Client): GCS client object
        kms_client (kms_v1.KeyManagementServiceClient): GCP KMS client object
        bucket_name (str): Name of bucket to upload files into
        blob_path (str): Path to blob within bucket
        project_id (str): Name of GCP project
        location_id (str): KMS key location
        key_ring_id (str): KMS key ring ID
        key_id (str): KMS key ID
    """

    logger.info(
        "Decrypting data: {} in bucket: {}"
        .format(blob_path, bucket_name))

    # Create temp directory if not exists
    temp_data_path = Path(temp_data)
    if not temp_data_path.exists():
        os.makedirs(temp_data_path)

    # Download file to local disk
    file_name = blob_path.split("/")[-1]
    destination_path = temp_data_path / file_name
    download_gcs_file(storage_client, bucket_name, blob_path, destination_path)

    # Load encrypted DEK + KEK path
    dek_blob_path = ".".join(blob_path.split(".")[:-1]) + ".dek"
    dek = load_gcs_object(storage_client,
                          bucket_name, dek_blob_path)
    # kek_blob_path = ".".join(blob_path.split(".")[:-1]) + ".kek"
    # kek_path = load_gcs_object(storage_client,
    #                            bucket_name, kek_blob_path).decode('utf-8')

    # Decrypt DEK
    dek = decrypt_dek(kms_client, dek, project_id,
                      location_id, key_ring_id, key_id)

    # Decrypt file
    decrypted_file_path = decrypt_file(str(destination_path), dek)

    # Copy file to GCS
    destination_blob_path = blob_path.replace(".encrypted", "")
    upload_file(storage_client, bucket_name,
                decrypted_file_path, destination_blob_path)

    # Remove local temp files
    os.remove(destination_path)
    os.remove(decrypted_file_path)

    # Remove encrypted blobs
    delete_blob(storage_client, bucket_name, blob_path)
    delete_blob(storage_client, bucket_name, dek_blob_path)
