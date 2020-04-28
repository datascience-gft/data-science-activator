import pytest
from gcpip.fe.gap_pyspark import run_submit_job_to_dataproc_cluster
from gcpip.runner import run_load
from gcpip.config.config_reader import LoadConfig, FeatureEngineeringConfig
from gcpip.upload.gcp_upload import upload_file
from google.api_core.exceptions import Conflict
from google.cloud import dataproc_v1, storage, bigquery
from google.cloud.dataproc_v1.gapic.transports import job_controller_grpc_transport


def generate_fe_args(bucket, submission_config_blob, region, pyspark_file,
                     other_python_files, cluster_name):
    return {"bucket": bucket,
            "submission_config_blob": submission_config_blob,
            "region": region,
            "pyspark_file": pyspark_file,
            "other_python_files": other_python_files,
            "cluster_name": cluster_name}


def test_fe():
    fe_config_file_name = "test_fe/test_fe.yaml"
    load_config_file_name = "test_fe/test_fe_load.yaml"

    fe_config = FeatureEngineeringConfig(fe_config_file_name)
    load_config = LoadConfig(load_config_file_name)

    test_bucket_name = fe_config.staging_bucket

    # Create test bucket
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(test_bucket_name, location="europe-west2")

    # Upload test data, submission config, fe_config to GCS bucket
    upload_dic = {"test_fe/test_market_data.csv": "data/market_data.csv",
                  "test_fe/test_fe_submission.yaml": "submissions/submissions_config.yaml",
                  "test_fe/test_fe.yaml": "meta/fe.yaml"}
    for source_file in upload_dic:
        upload_file(storage_client, test_bucket_name, source_file, upload_dic[source_file])

    # Create test BigQuery dataset
    bq_client = bigquery.Client()
    dataset_id = "{}.{}".format(load_config.project_id, load_config.destination_dataset)
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "europe-west2"
    try:
        dataset = bq_client.create_dataset(dataset)
    except Conflict:
        pass

    # Load data into BQ  & check load was successful
    run_load(load_config)
    table_ids = [x.table_id for x in bq_client.list_tables(dataset)]
    assert fe_config.source_table in table_ids

    feature_engineering_args = generate_fe_args(bucket=test_bucket_name,
                                                submission_config_blob="submissions/submissions_config.yaml",
                                                region="europe-west2",
                                                pyspark_file="../src/gcpip/fe/feature_engineering_runner.py",
                                                other_python_files="../src/gcpip/fe/feature_engineering_functions.py",
                                                cluster_name="dataproc-cluster")

    job_transport = (
        job_controller_grpc_transport.JobControllerGrpcTransport(
            address='{}-dataproc.googleapis.com:443'.format(feature_engineering_args['region'])))
    dataproc_job_client = dataproc_v1.JobControllerClient(job_transport)

    # jar file for bq connector
    jar_file_uris_bq_connector = ["gs://spark-lib/bigquery/spark-bigquery-latest.jar"]

    run_submit_job_to_dataproc_cluster(region=feature_engineering_args['region'],
                                       cluster_name=feature_engineering_args['cluster_name'],
                                       pyspark_file_path=feature_engineering_args["pyspark_file"],
                                       other_python_file_path=feature_engineering_args["other_python_files"],
                                       jar_file_uris=jar_file_uris_bq_connector,
                                       config_obj=fe_config,
                                       dataproc_job_client=dataproc_job_client)

    # Check table in bigquery
    table_ids = [x.table_id for x in bq_client.list_tables(dataset)]
    assert fe_config.destination_table in table_ids

    # Tear down temporary resources
    bucket.delete(force=True)
    bq_client.delete_dataset(dataset, delete_contents=True)
