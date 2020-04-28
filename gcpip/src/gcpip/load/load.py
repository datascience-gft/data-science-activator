import logging
from gcpip.utils.biq_query import create_table, gcs_csv_to_bq

logger = logging.getLogger(__name__)


def load_gcs_csv_to_bq(bq_client, bucket_id, csv_path,
                       project_id, dataset_id,
                       table_id, schema_config, skip_leading_rows):
    """
    Load CSV from GCS to Big Query.
    Data must follow format limitations defined here,
        https://cloud.google.com/bigquery/docs/loading-data-cloud-storage-csv#limitations

    Args:
        key_file (str): GCP service account JSON credentials.
        bucket_id (str): ID of bucket containing CSV to load.
        csv_path (str): Path to CSV to load.
        project_id (str): ID of project for load job.
        dataset_id (str): ID of Biq Query dataset to load data.
        table_id (str): ID of Big Query table to load data.
        schema_config (dict): Dictionary containing schema config information.
        kms_key (dict, optional): Dictionary containing KMS information.
            Defaults to None.

    Returns:
        google.cloud.bigquery.job.LoadJob: Import job object
    """

    logger.info("Creating table: {} in dataset: {} and loading CSV: {} \
                from bucket: {}"
                .format(table_id, dataset_id, csv_path, bucket_id))

    # Create table
    create_table(bq_client, project_id, dataset_id,
                 table_id, schema_config)

    # Load data
    import_job = gcs_csv_to_bq(bq_client, project_id,
                               bucket_id, csv_path, dataset_id,
                               table_id, skip_leading_rows)

    return import_job
