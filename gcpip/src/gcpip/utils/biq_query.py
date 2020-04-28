# TODO logging

import logging
from google.oauth2 import service_account
from google.cloud import bigquery
from gcpip.utils.storage import get_gcs_url

logger = logging.getLogger(__name__)


def get_bq_client(key_file):
    """
    Get authenticated BQ client object

    Args:
        key_file (str): Path to GCP authentication file

    Returns:
        google.cloud.bigquery.Client: BQ client object
    """

    logger.debug("Get Big Query Client")

    credentials = service_account.Credentials.from_service_account_file(
        key_file, scopes=["https://www.googleapis.com/auth/cloud-platform"])
    client = bigquery.Client(credentials=credentials,
                             project=credentials.project_id)

    return client


def get_datasets(bq_client, project_id):
    """
    Get BQ datasets for project id

    Args:
        bq_client (google.cloud.bigquery.Client): BQ client object
        project_id (str): GCP project ID

    Returns:
        list[google.cloud.bigquery.dataset.Dataset]: list of dataset objects
    """

    logger.debug(
        "Get list of datasets associated with project: {}"
        .format(project_id))

    return [x for x in bq_client.list_datasets(project_id)]


def get_dataset_ids(bq_client, project_id):
    """
    Get BQ dataset ids for project id

    Args:
        bq_client (google.cloud.bigquery.Client): BQ client object
        project_id (str): GCP project ID

    Returns:
        list[str]: list of dataset ids
    """

    logger.debug(
        "Get list of dataset IDs associated with project: {}"
        .format(project_id))

    return [x.dataset_id for x in bq_client.list_datasets(project_id)]


def get_dataset(bq_client, project_id, dataset_id):
    """
    Get BQ dataset

    Args:
        bq_client (google.cloud.bigquery.Client): BQ client object
        project_id (str): GCP project ID
        dataset_id (str): Dataset ID

    Returns:
        google.cloud.bigquery.dataset.Dataset: BQ dataset object
    """

    logger.debug("Get dataset: {}".format(dataset_id))

    dataset_ref = bq_client.dataset(dataset_id, project=project_id)
    return bq_client.get_dataset(dataset_ref)


def create_dataset(bq_client, project_id, dataset_id):
    """
    Create BQ dataset

    Args:
        bq_client (google.cloud.bigquery.Client): BQ client object
        project_id (str): GCP project ID
        dataset_id (str): Dataset ID

    Returns:
        google.cloud.bigquery.dataset.Dataset: BQ dataset object
    """

    logger.debug("Creating dataset: {} in project: {}".format(
        dataset_id, project_id))

    dataset = bq_client.dataset(dataset_id, project=project_id)
    return bq_client.create_dataset(dataset)


def delete_dataset(bq_client, project_id, dataset_id):
    """
    Delete BQ dataset

    Args:
        bq_client (google.cloud.bigquery.Client): BQ client object
        project_id (str): GCP project ID
        dataset_id (str): Dataset ID
    """

    logger.debug("Deleting dataset: {} in project: {}".format(
        dataset_id, project_id))

    dataset = bq_client.dataset(dataset_id, project=project_id)
    bq_client.delete_dataset(dataset)


def get_table_ids(bq_client, project_id, dataset_id):
    """
    Get list of table objects belonging to a dataset

    Args:
        bq_client (google.cloud.bigquery.Client): BQ client object
        project_id (str): GCP project ID
        dataset_id (str): Dataset ID

    Returns:
        list(str): List of BQ table ids
    """

    logger.debug(
        "Getting list of tables associated with dataset: {}"
        .format(dataset_id))

    dataset = get_dataset(bq_client, project_id, dataset_id)
    return [x.table_id for x in bq_client.list_tables(dataset)]


def create_table(bq_client, project_id, dataset_id, table_id, schema_config):
    """
    Create BQ table

    Args:
        bq_client (google.cloud.bigquery.Client): BQ client object
        project_id (str): GCP project ID
        dataset_id (str): Dataset ID

    Returns:
        google.cloud.bigquery.table.Table: BQ table object
    """

    logger.debug("Creating big query table: {} in dataset: {}".format(
        table_id, dataset_id))

    dataset = get_dataset(bq_client, project_id, dataset_id)
    table_ref = dataset.table(table_id)
    schema = parse_schema(schema_config)
    table = bigquery.Table(table_ref, schema=schema)
    return bq_client.create_table(table)


def get_table_reference(bq_client, project_id, dataset_id, table_id):
    """
    Get Biq Query table reference

    Args:
        bq_client (google.cloud.bigquery.Client): BQ client object
        project_id (str): GCP project ID
        dataset_id (str): Dataset ID
        table_id (str): Table ID

    Returns:
        google.cloud.bigquery.table.TableReference: BQ table reference
    """

    logger.debug("Getting table reference for table: {}, dataset: {}"
                 .format(table_id, dataset_id))
    dataset = get_dataset(bq_client, project_id, dataset_id)
    return dataset.table(table_id)


def get_table(bq_client, project_id, dataset_id, table_id):

    logger.debug("Getting table: {}, dataset: {}"
                 .format(table_id, dataset_id))
    dataset = get_dataset(bq_client, project_id, dataset_id)
    table_ref = dataset.table(table_id)

    return bq_client.get_table(table_ref)


def delete_table(bq_client, project_id, dataset_id, table_id):

    logger.debug("Deleting table: {} from dataset: {}"
                 .format(table_id, dataset_id))
    table_ref = get_table_reference(
        bq_client, project_id, dataset_id, table_id)
    bq_client.delete_table(table_ref)


def parse_schema(schema_config):
    """
    Parse schema config from load YAML and returns list of BQ schema objects

    Args:
        schema_config (dict): Schema config from load YAML

    Returns:
        list: List of BQ schema objects
    """

    logger.debug("Parsing schema config")

    schema = []

    for field in schema_config.keys():

        col = schema_config[field]
        schema_col = bigquery.SchemaField(
            col['name'], col['type'], mode=col['mode'])
        schema.append(schema_col)

    return schema


def gcs_csv_to_bq(bq_client, project_id, bucket_id,
                  csv_path, dataset_id, table_id, skip_leading_rows):
    """
    Load GCS CSV to BQ using BQ import job.
    Data must follow specifications set here:
        https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-csv#limitations

    Args:
        bq_client (google.cloud.bigquery.Client): BQ client object
        project_id (str): ID of project for load job.
        bucket_id (str): ID of bucket containing CSV to load.
        csv_path (str): Path to CSV to load.
        dataset_id (str): ID of Biq Query dataset to load data.
        table_id (str): ID of Big Query table to load data.

    Returns:
        google.cloud.bigquery.job.LoadJob: Import job object
    """

    logger.debug("Loading CSV file: {} from bucket: {} into table: {} in \
        dataset: {}".format(csv_path, bucket_id, table_id, dataset_id))

    # Get GS URL
    gcs_url = get_gcs_url(bucket_id, csv_path)

    # Get table reference
    table_reference = get_table_reference(
        bq_client, project_id, dataset_id, table_id)

    # Setup load job
    job_config = bigquery.LoadJobConfig()
    job_config.skip_leading_rows = skip_leading_rows
    job_config.source_format = 'CSV'
    job_config.write_disposition = 'WRITE_EMPTY'

    return bq_client.load_table_from_uri(gcs_url, table_reference,
                                         job_config=job_config)
