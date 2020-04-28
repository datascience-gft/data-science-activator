import sys
import logging
import argparse
from google.cloud import bigquery


def load(dataset_id, table, gcs_uri, client, autodetect=False):
    """
    This function loads data from GCS into Bq.
    Args:
        autodetect (boolean): True for autodetect the schema.
        dataset_id (str): bq dataset id that has the data.
        table (str): Name of the bq table.
        gcs_uri (str): GCS URI
        client (Bigquery.Client): bigquery.Client object.

    Returns: It reports back the log message about the loading.

    """
    dataset_ref = client.dataset(dataset_id)
    job_config = bigquery.LoadJobConfig()
    job_config.skip_leading_rows = 1
    job_config.source_format = bigquery.SourceFormat.CSV
    if autodetect:
        job_config.autodetect = True
    load_job = client.load_table_from_uri(
        gcs_uri, dataset_ref.table(table), job_config=job_config
    )
    id = load_job.job_id
    logging.info("Loading into {}.{} for job id {} has been started.".
                 format(dataset_id,table,id))

    load_job.result()
    logging.info("Loading into {}.{} for job id {} has been finished.".
                 format(dataset_id,table,id))

    destination_table = client.get_table(dataset_ref.table(table))
    logging.info("Number of loaded rows in {}.{} is from job id {} is {}.".
                 format(dataset_id,table,id,destination_table.num_rows))


def main(args):
    """
    """

    autodetect = False
    client_bq = bigquery.Client()
    dataset = 'market_dataset'
    bq_table = 'market'
    uri = 'gs://data-science-activator-landing-data-bucket-mssb-sandbox/prepared_data/market_data.csv'
    load(dataset_id=dataset, table=bq_table, gcs_uri=uri, client=client_bq,
         autodetect=autodetect)


def run():
    main(sys.argv[1:])


if __name__ == '__main__':
    run()
