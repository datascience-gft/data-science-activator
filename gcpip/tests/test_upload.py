import pytest
import numpy as np
from gcpip.runner import main
from gcpip.config.config_reader import UploadConfig
from gcpip.utils.storage import get_storage_client


def generate_upload_args(config_name, action, bucket, source, destination,
                         key_id=None, key_ring_id=None, location_id=None):

    return ['upload',
            '-a', action,
            '-c', 'resources/config/' + config_name + '.yaml',
            '-b', bucket,
            '-s', source,
            '-d', destination,
            '-k', key_id,
            '-r', key_ring_id,
            '-l', location_id]


def generate_decrypt_args(config_name, bucket, source,
                          key_id, key_ring_id, location_id):

    return ['decrypt',
            '-c', 'resources/config/' + config_name + '.yaml',
            '-b', bucket,
            '-s', source,
            '-k', key_id,
            '-r', key_ring_id,
            '-l', location_id]


@pytest.fixture
def upload_details():

    random_number = np.random.randint(1000, 9999)

    return {
        "config_name": "upload_config_file_example",
        "bucket": "test-bucket-data-gen-" + str(random_number),
        "source": "resources/upload_example1.csv",
        "destination": "test/upload_example1.csv",
        "key_id": 'test_key',
        "key_ring_id": 'test_key_ring',
        "location_id": 'europe-west2',
    }


@pytest.fixture
def create_test_bucket(upload_details):

    bucket = upload_details['bucket']
    config_file = 'resources/config/' + upload_details['config_name'] + '.yaml'
    upload_config = UploadConfig(config_file)
    storage_client = get_storage_client(key_file=upload_config.get_key_file())
    storage_client.create_bucket(bucket, project=upload_config.project_name)


def remove_test_bucket(upload_details):

    bucket = upload_details['bucket']
    config_file = 'resources/config/' + upload_details['config_name'] + '.yaml'
    upload_config = UploadConfig(config_file)
    storage_client = get_storage_client(key_file=upload_config.get_key_file())
    bucket = storage_client.get_bucket(bucket)
    bucket.delete(force=True)


def test_upload_encrypt_decrypt(upload_details, create_test_bucket):
    """

    Test for uploading encrypted files and then decrypting
    NOTE: Should not run decryption on a machine external to GCP on real data

    """

    bucket_name = upload_details['bucket']

    # Upload encrypted files
    args = generate_upload_args(
        config_name=upload_details['config_name'],
        action='encrypted',
        bucket=bucket_name,
        source=upload_details['source'],
        destination=upload_details['destination'],
        key_id=upload_details['key_id'],
        key_ring_id=upload_details['key_ring_id'],
        location_id=upload_details['location_id'])
    main(args)

    upload_config = UploadConfig(
        'resources/config/' + upload_details['config_name'] + '.yaml')
    storage_client = get_storage_client(key_file=upload_config.get_key_file())
    bucket = storage_client.get_bucket(bucket_name)
    blobs = [x.name for x in bucket.list_blobs()]

    # Check encrypted file and key uploaded
    assert upload_details['destination'] + ".encrypted" in blobs
    assert upload_details['destination'] + ".dek" in blobs

    # Decrypt files
    args = generate_decrypt_args(
        config_name=upload_details['config_name'],
        bucket=bucket_name,
        source=upload_details['destination'] + ".encrypted",
        key_id=upload_details['key_id'],
        key_ring_id=upload_details['key_ring_id'],
        location_id=upload_details['location_id'])
    main(args)

    # Check file decrypted and key removed
    bucket = storage_client.get_bucket(bucket_name)
    blobs = [x.name for x in bucket.list_blobs()]
    assert upload_details['destination'] in blobs
    assert upload_details['destination'] + ".encrypted" not in blobs
    assert upload_details['destination'] + ".dek" not in blobs

    # Remove test bucket
    remove_test_bucket(upload_details)
