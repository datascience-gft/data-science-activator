import os
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)


def get_pyspark_file(pyspark_file=None):
    """
    Get the pyspark file
    Args:
        pyspark_file (str): path of the pyspark file

    Returns:
        f (file object):
        os.path.basename(pyspark_file) (str) : name of the pyspark file
    """
    if pyspark_file:
        f = open(pyspark_file, "rb")
        return f, os.path.basename(pyspark_file)
    else:
        assert pyspark_file, "pyspark file is not found!"


def upload_file_to_staging_bucket(project, bucket_name, filename, file_obj):
    """
    Uploads the PySpark file in this directory to the configured input
    bucket.
    Args:
        project (str): project id
        bucket_name (str): name of the gcs bucket to which the file is uploaded
        filename (str): name of the file
        file_obj (file object): file object instance of the file

    Returns:

    """
    logger.info('Uploading file {} to bucket: {}.'.format(filename, bucket_name))
    client = storage.Client(project=project)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_file(file_obj)


def get_pyspark_job_details(cluster_name, main_python_file, jar_file_uris,
                            feature_engineering_args, other_python_file=None):
    """

    Args:
        other_python_file (list): HCFS file URIs of Python files to pass to the PySpark framework
        cluster_name (str): name of the dataproc cluster
        main_python_file (str): The HCFS URI of the main Python file to use as the driver. Must be a .py file
        jar_file_uris (list): HCFS URIs of jar files to add to the CLASSPATHs of the Python driver and tasks.
        feature_engineering_args (list): The arguments to pass to the driver.

    Returns:
        job_details (dic): details of the submitted job
    (https://cloud.google.com/dataproc/docs/reference/rpc/google.cloud.dataproc.v1#google.cloud.dataproc.v1.Job)

    """
    job_details = \
        dict(placement={
            'cluster_name': cluster_name
        },
            pyspark_job={
                'main_python_file_uri': main_python_file,
                "jar_file_uris": jar_file_uris,
                "args": feature_engineering_args,
                "python_file_uris": other_python_file
            })
    return job_details


def submit_pyspark_job(dataproc_job_client_obj,
                       project, region, job_details):
    """
    Submit the Pyspark job to the cluster (assumes `filename` was uploaded
    to `bucket_name.
    Args:
        job_details (dic): details of the submitted job
        dataproc_job_client_obj:
        project (str): project id
        region (str): region of the dataproc cluster

    Returns:
        job_id:

    """

    result = dataproc_job_client_obj.submit_job(
        project_id=project, region=region, job=job_details)
    job_id = result.reference.job_id
    logger.info('Submitted job ID {}.'.format(job_id))
    return job_id


def get_feature_engineering_args(config_obj):
    """
    This function gets the command line arguments to pass to pyspark job submitted to Dataproc

    Args:
        config_obj: feature engineering configuration object

    Returns:
        ls_cli_args (list): list of cli arguments to pass to pyspark job which are used for different feature
        engineering tasks

    """
    # required arguments
    input_table = "{}.{}".format(config_obj.source_dataset, config_obj.source_table)
    output_table = "{}.{}".format(config_obj.destination_dataset, config_obj.destination_table)
    temporary_gcs_bucket = config_obj.staging_bucket
    moving_average_args = ["--ma", "False"]  # means does not execute
    mid_price_args = ["--mp", "False"]  # means does not execute
    spread_args = ["--spread", "False"]  # means does not execute

    for feature in config_obj.engineered_features:
        engineered_feature = config_obj.engineered_features[feature]
        if "parameters" in engineered_feature.keys():
            parameters = engineered_feature["parameters"]
        else:
            parameters = None
        if engineered_feature["name"] == "moving_average":  # moving average arguments (optional)
            moving_average_target_columns = engineered_feature["target_columns"]
            moving_average_time_intervals = [str(interval) for interval in parameters["time_intervals"]]
            moving_average_group_column = parameters["group_column"]
            moving_average_sort_column = parameters["sort_column"]
            moving_average_args = ["--ma", "True"] \
                                  + ["--ma_target_columns"] + moving_average_target_columns \
                                  + ["--ma_time_intervals"] + moving_average_time_intervals \
                                  + ["--ma_group_column"] + moving_average_group_column \
                                  + ['--ma_sort_column'] + moving_average_sort_column
        elif engineered_feature["name"] == "mid_price":  # mid price arguments (optional)
            mid_price_col1 = engineered_feature["target_columns"][0]
            mid_price_col2 = engineered_feature["target_columns"][1]
            mid_price_args = ["--mp", "True"] \
                             + ["--mp_col1"] + [mid_price_col1] + ["--mp_col2"] + [mid_price_col2]
        elif engineered_feature["name"] == "spread":  # spread arguments (optional)
            spread_col1 = engineered_feature["target_columns"][0]
            spread_col2 = engineered_feature["target_columns"][1]
            spread_args = ["--spread", "True"] \
                          + ["--spread_col1"] + [spread_col1] + ["--spread_col2"] + [spread_col2]

    feature_engineering_args = \
        ["--input_table"] + [input_table] \
        + ["--output_table"] + [output_table] \
        + ["--temporary_gcs_bucket"] + [temporary_gcs_bucket] \
        + moving_average_args \
        + mid_price_args \
        + spread_args

    return feature_engineering_args

def wait_for_job(dataproc, project, region, job_id):
    """Wait for job to complete or error out."""
    logger.info('Waiting for job to finish...')
    while True:
        job = dataproc.get_job(project, region, job_id)
        # Handle exceptions
        if job.status.State.Name(job.status.state) == 'ERROR':
            raise Exception(job.status.details)
        elif job.status.State.Name(job.status.state) == 'DONE':
            print('Job finished.')
            return job


def run_submit_job_to_dataproc_cluster(region="europe-west2",
                                       cluster_name=None,
                                       pyspark_file_path=None,
                                       other_python_file_path=None,
                                       jar_file_uris=None,
                                       config_obj=None,
                                       dataproc_job_client=None):
    """

    Args:
        other_python_file_path (str): local file path of other python file (i.e., feature_engineering_functions.py)
        region (str): Cloud Dataproc region to use
        cluster_name (str): The Dataproc cluster to submit the job to.
        pyspark_file_path (str): local file path of the pyspark file
        jar_file_uris (list):Comma separated list of jar files to be provided to the executor and driver classpaths.
        config_obj : feature engineering config object
        dataproc_job_client: dataproc job client

    """

    project_id = config_obj.project_id
    feature_engineering_args = get_feature_engineering_args(config_obj)
    gcs_staging_bucket = config_obj.staging_bucket

    spark_file, spark_filename = get_pyspark_file(pyspark_file_path)
    other_python_file, other_python_filename = get_pyspark_file(other_python_file_path)

    for file, filename in [(spark_file, spark_filename), (other_python_file, other_python_filename)]:
        upload_file_to_staging_bucket(project=project_id,
                                      bucket_name=gcs_staging_bucket,
                                      filename=filename,
                                      file_obj=file)

    main_python_uri = 'gs://{}/{}'.format(gcs_staging_bucket, spark_filename)
    other_python_file_uri = ['gs://{}/{}'.format(gcs_staging_bucket, other_python_filename)]

    job_details = get_pyspark_job_details(cluster_name, main_python_uri, jar_file_uris,
                                          feature_engineering_args, other_python_file_uri)

    job_id = submit_pyspark_job(dataproc_job_client_obj=dataproc_job_client,
                                project=project_id,
                                region=region,
                                job_details=job_details)
    wait_for_job(dataproc_job_client, project_id, region, job_id)

    logger.info(
        "Job:{job_id} has been successfully submitted to cluster: {cluster_name} and feature engineering tasks have "
        "been performed as configured!")
