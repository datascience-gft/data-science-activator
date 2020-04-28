import logging
from google.cloud import kms_v1
from google.cloud.kms_v1 import enums
from google.oauth2 import service_account
from google.cloud import storage

logger = logging.getLogger(__name__)


def get_kms_client(key_file):
    """
    Get authenticated KMS client object

    Args:
        key_file (str): Path to GCP authentication file

    Returns:
        google.cloud.kms_v1.KeyManagementServiceClient: KMS client object
    """

    logger.debug("Creating KMS client")

    credentials = service_account.Credentials.from_service_account_file(
        key_file, scopes=["https://www.googleapis.com/auth/cloud-platform"])
    client = kms_v1.KeyManagementServiceClient(credentials=credentials)

    return client


def get_kms_key_ring_path(kms_client, project_id, location_id, key_ring_id):
    """
    Get path for key ring
    Path is generated without checking if ring exists

    Args:
        kms_client (kms_v1.KeyManagementServiceClient): KMS client object
        project_id (str): Name of GCP project
        location_id (str): KMS key location
        key_ring_id (str): KMS key ring ID

    Returns:
        str: key ring resource name
    """

    logger.debug("Getting KMS key ring resource name")

    return kms_client.key_ring_path(
        project_id, location_id, key_ring_id)


def get_kms_key_path(kms_client, project_id, location_id, key_ring_id, key_id):
    """
    Get KMS key resource name

    Args:
        kms_client (kms_v1.KeyManagementServiceClient): KMS client object
        project_id (str): Name of GCP project
        location_id (str): KMS key location
        key_ring_id (str): KMS key ring ID
        key_id (str): KMS key ID

    Returns:
        str: KMS key resource name
    """

    logger.debug("Getting KMS key resource name")

    return kms_client.crypto_key_path(
        project_id, location_id, key_ring_id, key_id)


def create_kms_key_ring(kms_client, project_id, location_id,
                        key_ring_id):
    """
    Create KMS key ring

    Args:
        kms_client (kms_v1.KeyManagementServiceClient): KMS client object
        project_id (str): Name of GCP project
        location_id (str): KMS key location
        key_ring_id (str): KMS key ring ID

    Returns:
        str: key ring resource name
    """

    logger.debug("Creating KMS key ring: {}".format(key_ring_id))

    parent = kms_client.location_path(project_id, location_id)

    keyring_name = kms_client.key_ring_path(
        project_id, location_id, key_ring_id)
    keyring = {'name': keyring_name}

    response = kms_client.create_key_ring(parent, key_ring_id, keyring)

    return response.name


def create_kms_key(kms_client, project_id, location_id, key_ring_id, key_id):
    """
    Create KMS Key

    Args:
        kms_client (kms_v1.KeyManagementServiceClient): KMS client object
        project_id (str): Name of GCP project
        location_id (str): KMS key location
        key_ring_id (str): KMS key ring ID
        key_id (str): KMS key ID

    Returns:
        str: key ring resource name
    """

    logger.debug("Creating KMS key: {}".format(key_id))

    key_ring = kms_client.key_ring_path(project_id, location_id, key_ring_id)

    purpose = enums.CryptoKey.CryptoKeyPurpose.ENCRYPT_DECRYPT
    key_params = {'purpose': purpose}
    response = kms_client.create_crypto_key(
        key_ring, key_id, key_params, skip_initial_version_creation=False)

    return response.name


def get_kms_key_rings(kms_client, project, location_id):
    """Get KMS key rings for a given project and location

    Args:
        kms_client (kms_v1.KeyManagementServiceClient): KMS client object
        project_id (str): Name of GCP project
        location_id (str): KMS key location

    Returns:
        list[str]: List of key ring ids
    """

    logger.debug("Listing KMS key rings for project: {} in location: {}"
                 .format(project, location_id))

    parent = kms_client.location_path(project, location_id)
    return [x.name.split("/")[-1] for x in kms_client.list_key_rings(parent)]


def get_kms_keys(kms_client, project, location_id, key_ring_id):
    """Get KMS keys for a given key ring

    Args:
        kms_client (kms_v1.KeyManagementServiceClient): KMS client object
        project_id (str): Name of GCP project
        location_id (str): KMS key location
        key_ring_id (str): KMS key ring ID

    Returns:
        list[str]: List of key ids
    """

    logger.debug("Listing KMS keys for ring: {} project: {} in location: {}"
                 .format(key_ring_id, project, location_id))

    parent = kms_client.key_ring_path(project, location_id, key_ring_id)
    return [x.name.split("/")[-1] for x in kms_client.list_crypto_keys(parent)]


def get_blob_kek_details(storage_client, bucket_name, blob_path):

    bucket = storage_client.get_bucket(bucket_name)
    blob = storage.Blob(blob_path, bucket)

    return blob.kms_key_name
