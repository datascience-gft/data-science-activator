import pytest
from gcpip.runner import run_load
from gcpip.utils.storage import (
    create_bucket, get_storage_client, delete_bucket)
from gcpip.config.config_reader import LoadConfig
from gcpip.upload.gcp_upload import upload_file
from gcpip.utils.biq_query import (
    get_bq_client, create_dataset, get_table_ids, get_table,
    delete_dataset, delete_table)
from google.api_core.exceptions import Conflict


def generate_load_args(config_name):

    return ['load',
            '-c', 'resources/config/' + config_name + '.yaml']


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


def test_load():

    config_file_name = "test_load"
    load_args = generate_load_args(config_file_name)
    load_config = LoadConfig(load_args[2])

    # Create test bucket
    storage_client = get_storage_client(load_config.key_file)
    bucket_id = create_bucket(storage_client, load_config.project_id,
                              "test-bucket")

    # Upload test data
    source_file = 'resources/upload_example1.csv'
    upload_file(storage_client, bucket_id, source_file, source_file)

    # Create test dataset

    bq_client = get_bq_client(load_config.key_file)
    try:
        create_dataset(bq_client, load_config.project_id,
                       load_config.destination_dataset)
    except Conflict:
        pass

    # Load data into BQ
    load_config.sources[0]['bucket_id'] = bucket_id
    run_load(load_config)

    # Check load was successful
    table_ids = get_table_ids(bq_client, load_config.project_id,
                              load_config.destination_dataset)

    assert load_config.destination_table in table_ids

    # Check table content
    table = get_table(
        bq_client,
        load_config.project_id,
        load_config.destination_dataset,
        load_config.destination_table)

    names = ["Ann", "James", "Dan", "Laura"]

    for i, row in enumerate(bq_client.list_rows(table)):
        assert row['name'] == names[i]

    # Tear down resource
    delete_bucket(storage_client, load_config.project_id,
                  bucket_id, force=True)
    delete_table(bq_client,
                 load_config.project_id,
                 load_config.destination_dataset,
                 load_config.destination_table)
    delete_dataset(bq_client,
                   load_config.project_id,
                   load_config.destination_dataset)
