import os

from google.cloud import bigquery, storage, dataproc_v1
from gcpip.bq_view_generator import create_bq_views
from gcpip.config.config_reader import (
    UploadConfig, BigQueryViewConfig, LoadConfig, FeatureEngineeringConfig, SubmissionConfig)
from gcpip.utils.encryption import get_kms_client
from gcpip.utils.storage import get_storage_client
from gcpip.utils.biq_query import get_bq_client
from gcpip.fe.gap_pyspark import run_submit_job_to_dataproc_cluster
from gcpip.upload.gcp_upload import (
    upload_file, encrypt_upload_file, decrypt_blob)
from gcpip.load.load import load_gcs_csv_to_bq
import argparse
import logging
import sys
from google.cloud.dataproc_v1.gapic.transports import job_controller_grpc_transport

logger = logging.getLogger(__name__)


def get_args(args):
    """
    Parse command line arguments

    Returns: args object

    """

    # Create parser and subparser objects
    parser = argparse.ArgumentParser(
        description='This script creates a data pipeline within GCP')
    subparsers = parser.add_subparsers(help='types of action')

    # DLP subparser
    parser_dlp = subparsers.add_parser("dlp")
    parser_dlp.set_defaults(which='dlp')
    parser_dlp.add_argument(
        '-d', '--data_file', type=str,
        help='Please provide the config file that is required by to build '
             'features.',
        required=True),
    parser_dlp.add_argument(
        '-a', '--action', type=str,
        help='Please provide the config file that is required by to build '
             'features.',
        choices=['mask', 'inspect'],
        required=True),
    parser_dlp.add_argument(
        '-c', '--config_file', type=str,
        help='Please provide the config file that is required by to build '
             'features.',
        required=True)

    # Decrypt subparser
    parser_decrypt = subparsers.add_parser("decrypt")
    parser_decrypt.set_defaults(which='decrypt')
    parser_decrypt.add_argument(
        '-s', '--source', type=str,
        help='Please provide the blob to be decrypted '
             'features.',
        required=True),
    parser_decrypt.add_argument(
        '-c', '--config_file', type=str,
        help='Please provide the config file that is required by to build '
             'features.',
        required=True),
    parser_decrypt.add_argument(
        '-b', '--bucket', type=str,
        help='Please provide the bucket containing the encrypted blob '
             'features.',
        required=True)
    parser_decrypt.add_argument(
        '-k', '--key', type=str,
        help='Please provide the key id for KEK'
             'features.',
        required=False)
    parser_decrypt.add_argument(
        '-r', '--keyring', type=str,
        help='Please provide the key ring id for KEK'
             'features.',
        required=False)
    parser_decrypt.add_argument(
        '-l', '--location', type=str,
        help='Please provide the location of the KEK'
             'features.',
        required=False
    )

    # Upload subparser
    parser_upload = subparsers.add_parser("upload")
    parser_upload.set_defaults(which='upload')
    parser_upload.add_argument(
        '-a', '--action', type=str,
        help='Please provide the upload type (plain or encrypted)'
             'features.',
        choices=['plain', 'encrypted'],
        required=True),
    parser_upload.add_argument(
        '-d', '--destination', type=str,
        help='Please provide the blob destination'
             'features.',
        required=True),
    parser_upload.add_argument(
        '-s', '--source', type=str,
        help='Please provide the local source file'
             'features.',
        required=True),
    parser_upload.add_argument(
        '-c', '--config_file', type=str,
        help='Please provide the config file that is required by to build'
             'features.',
        required=True),
    parser_upload.add_argument(
        '-b', '--bucket', type=str,
        help='Please provide the bucket for GCS upload'
             'features.',
        required=True)
    parser_upload.add_argument(
        '-k', '--key', type=str,
        help='Please provide the key id for the KEK'
             'features.',
        required=False)
    parser_upload.add_argument(
        '-r', '--keyring', type=str,
        help='Please provide the key ring id for the KEK'
             'features.',
        required=False)
    parser_upload.add_argument(
        '-l', '--location', type=str,
        help='Please provide the location id for the KEK'
             'features.',
        required=False)

    # bigquery view parser
    parser_bq_view = subparsers.add_parser("bq_view")
    parser_bq_view.set_defaults(which='bq_view')
    parser_bq_view.add_argument(
        '-b', '--bucket', type=str,
        help='Please provide the bucket_name storing the submission configuration and metadata files.',
        required=True)
    parser_bq_view.add_argument(
        '-s', '--submission_config_blob', type=str,
        help='Please provide the submission configuration file. e.g. submissions/submission_config.yaml',
        required=True)

    # feature engineering parser
    parser_feature_engineering = subparsers.add_parser("fe")
    parser_feature_engineering.set_defaults(which='fe')
    parser_feature_engineering.add_argument(
        '-b', '--bucket', type=str,
        help='Please provide the bucket_name storing the submission configuration and metadata files.',
        required=True)
    parser_feature_engineering.add_argument(
        '-s', '--submission_config_blob', type=str,
        help='Please provide the submission configuration file. e.g. submissions/submission_config.yaml',
        required=True)
    parser_feature_engineering.add_argument(
        '-r', '--region', type=str,
        help='Please provide the region. e.g., "europe-west2"',
        default="europe-west2",
        required=True)
    parser_feature_engineering.add_argument(
        '-p', '--pyspark_file', type=str,
        help='Please provide the pyspark filepath. e.g., "fe/feature_engineering_runner.py"',
        required=True)
    parser_feature_engineering.add_argument(
        '-o', '--other_python_files', type=str,
        help='Please provide the complementary python filepath. e.g., "fe/feature_engineering_functions.py"',
        required=True)
    parser_feature_engineering.add_argument(
        '-u', '--cluster_name', type=str,
        help='Please provide the fe config file. e.g., "dataproc-cluster"'
             'features.',
        required=True)

    # Load big query parser
    parser_load = subparsers.add_parser("load")
    parser_load.set_defaults(which='load')
    parser_load.add_argument(
        '-b', '--bucket', type=str,
        help='Please provide the bucket_name storing the submission configuration and metadata files.',
        required=True)
    parser_load.add_argument(
        '-s', '--submission_config_blob', type=str,
        help='Please provide the submission configuration file. e.g. submissions/submission_config.yaml',
        required=True)

    # Global parser arguments
    parser.add_argument(
        '-v',
        '--verbose',
        dest='loglevel',
        help='set loglevel to INFO',
        action='store_const',
        const=logging.INFO
    )

    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest='loglevel',
        help='set loglevel to DEBUG',
        action='store_const',
        const=logging.DEBUG
    )

    args = parser.parse_args(args)
    return args


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = '[%(asctime)s] %(levelname)s:%(name)s:  %(message)s'
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt='%Y-%m-%d %H:%M:%S')


def run_upload(source, destination, bucket_name, config, encrypt=False,
               location_id=None, key_ring_id=None, key_id=None):
    """
    It runs upload task. Currently it upload the file to GCS.
    Uploaded file can be encrpyted or left as plain text before upload.
    Args:
        data_file (str): Path to the input file.
        destination (str): Google Cloud Destination directory/name
        bucket_name (str): Google Cloud Bucket name.
        config (UploadConfig): config object.

    Returns: Upload the file and return the upload confirmation message.

    """
    storage_client = get_storage_client(key_file=config.get_key_file())

    if encrypt is False:
        upload_file(storage_client=storage_client, bucket_name=bucket_name,
                    source_file_name=source,
                    destination_name=destination)

    if encrypt is True:
        kms_client = get_kms_client(key_file=config.get_key_file())
        encrypt_upload_file(storage_client, kms_client, bucket_name, source,
                            destination, config.project_name, location_id,
                            key_ring_id, key_id)


def run_decryption(blob_path, bucket_name, config, location_id,
                   key_ring_id, key_id):
    """
    Run decryption on uploaded blob.
    File will be downloaded to worker disk, decrypted and then uploaded to GCS
        storage

    Args:
        blob_path (str): Path to encrypted blob within bucket
        bucket_name (str): Name of bucket containing encrypted blob
        config (gcpip.config.config_reader.UploadConfig): Upload config object
        location_id (str): Location id of KEK
        key_ring_id (str): Key ring id of KEK
        key_id (str): Key id of KEK
    """

    storage_client = get_storage_client(key_file=config.get_key_file())
    kms_client = get_kms_client(key_file=config.get_key_file())

    decrypt_blob(
        storage_client, kms_client, bucket_name, blob_path,
        config.project_name, location_id, key_ring_id, key_id)


def run_load(load_config):
    # Get big query client
    bq_client = get_bq_client(load_config.key_file)

    # Run load job
    source0 = load_config.sources[0]
    load_gcs_csv_to_bq(bq_client,
                       bucket_id=source0['bucket_id'],
                       csv_path=source0['file_path'],
                       project_id=load_config.project_id,
                       dataset_id=load_config.destination_dataset,
                       table_id=load_config.destination_table,
                       schema_config=load_config.destination_schema,
                       skip_leading_rows=source0['skip_leading_rows'])


def check_submission_config_file_exists(client, bucket_name, source_blob_name):
    """
    This function checks if the specified submission configure file exists in the specified bucket.
    Args:
        client: cloud storage client object
        bucket_name (str): name of the bucket containing the view configuration file
        source_blob_name (str): name of the blob, which corresponds to the unique path of the object in the bucket.

    Returns:
        submission_config_exists (boolean): True, if the specified view_blob exists; otherwise, False

    """
    bucket = client.get_bucket(bucket_name)
    blobs = [x.name for x in bucket.list_blobs()]
    submission_config_exists = (source_blob_name in blobs)
    return submission_config_exists


def check_config_file_exists(client, bucket_name, config_blob_name):
    """
    This function checks if the specified BigQuery view configure file exists in the specified bucket.
    Args:
        client: cloud storage client object
        bucket_name (str): name of the bucket containing the view configuration file
        config_blob_name (str): name of the blob, which corresponds to the unique path of the object in the bucket.

    Returns:
        config_exists (boolean): True, if the specified config_blob exists; otherwise, False

    """
    bucket = client.get_bucket(bucket_name)
    blobs = [x.name for x in bucket.list_blobs()]
    config_exists = (config_blob_name in blobs)
    return config_exists


def get_submission_config_obj(client, bucket_name, source_blob_name):
    """
    This function get the submission configurations from submission config files in GCS
    The submission config file should be located in the submission folder in the data-landing-bucket
    Args:
        client: cloud storage client object
        bucket_name (str): name of the bucket
        source_blob_name (str): name of the blob, which corresponds to the unique path of the object in the bucket.
    Returns:
        submission_config_obj: submission configuration object
    """
    temp_local_file = "sub_config.yaml"  # temporary local file for storing the submission yaml file

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(temp_local_file)
    submission_config_obj = SubmissionConfig(temp_local_file)

    # remove the temp local file
    try:
        os.remove(temp_local_file)
        print("% s removed successfully" % temp_local_file)
    except OSError as error:
        print(error)
        print("File path can not be removed")

    return submission_config_obj


def get_config_obj_from_submission(action, client, bucket_name, source_blob_name):
    """
    This function create BigQuery view object from the source_table in the source_dataset
    Args:
        action (str): can be "view", "load", or "feature_engineering"
        client: cloud storage client object
        bucket_name (str): name of the bucket containing the submission config file
        source_blob_name(str): name of the blob, which corresponds to the unique path of the object in the bucket.
    Returns:
        config_obj:

    """
    submission_config_obj = get_submission_config_obj(client, bucket_name, source_blob_name)
    submission_list = list(submission_config_obj.get_submissions().keys())
    for submission in submission_list:
        if submission_config_obj.get_submissions()[submission]["action"] == action:
            meta_file_path = submission_config_obj.get_submissions()[submission]["metadata_file"]
            meta_file_name = os.path.basename(meta_file_path)

    source_blob_name = 'meta/' + meta_file_name
    temp_local_file = "{}.yaml".format(action)  # temporary local file for storing bq view yaml file
    bucket = client.bucket(bucket_name)

    config_blob_exists = check_config_file_exists(client=client,
                                                  bucket_name=bucket_name,
                                                  config_blob_name=source_blob_name)
    if config_blob_exists:
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(temp_local_file)
        if action == "load":
            config_obj = LoadConfig(temp_local_file)
        elif action == "view":
            config_obj = BigQueryViewConfig(temp_local_file)
        elif action == "feature_engineering":
            config_obj = FeatureEngineeringConfig(temp_local_file)

        # remove the temp local file
        try:
            os.remove(temp_local_file)
            print("% s removed successfully" % temp_local_file)
        except OSError as error:
            print(error)
            print("File path can not be removed")
        return config_obj
    else:
        assert config_blob_exists, "configuration yaml file does not exist in the GCS bucket, please upload!"


def main(args):
    """

    Args:
        args:

    Returns:

    """
    args = get_args(args)
    loglevel = args.loglevel
    if args.loglevel is None:
        loglevel = logging.INFO
    setup_logging(loglevel)
    logging.info(args)

    if args.which == 'upload':
        upload_config = UploadConfig(args.config_file)

        if args.action == 'plain':
            encrypt = False
        if args.action == 'encrypted':
            encrypt = True

        run_upload(source=args.source, destination=args.destination,
                   bucket_name=args.bucket,
                   config=upload_config, encrypt=encrypt,
                   location_id=args.location, key_ring_id=args.keyring,
                   key_id=args.key
                   )

    if args.which == 'decrypt':
        config = UploadConfig(args.config_file)
        run_decryption(args.source, args.bucket, config, args.location,
                       args.keyring, args.key)

    if args.which == 'bq_view':
        logger.info("Creating Biq Query View")
        client_bq = bigquery.Client()
        client_gcs = storage.Client()
        submission_config_exists = check_submission_config_file_exists(
            client=client_gcs, bucket_name=args.bucket,
            source_blob_name=args.submission_config_blob)
        if submission_config_exists:
            bq_config_obj = get_config_obj_from_submission(
                action="view",
                client=client_gcs, bucket_name=args.bucket,
                source_blob_name=args.submission_config_blob)
            create_bq_views(client=client_bq,
                            bq_config_obj=bq_config_obj)
        else:
            assert submission_config_exists, "Submission yaml file is not found in the GCS bucket, please upload!"

    if args.which == 'load':
        client_gcs = storage.Client()
        submission_config_exists = check_submission_config_file_exists(
            client=client_gcs, bucket_name=args.bucket,
            source_blob_name=args.submission_config_blob)
        if submission_config_exists:
            load_config = get_config_obj_from_submission(
                action="load",
                client=client_gcs,
                bucket_name=args.bucket,
                source_blob_name=args.submission_config_blob)
            run_load(load_config)
        else:
            assert submission_config_exists, "Submission yaml file is not found in the GCS bucket, please upload!"

    if args.which == 'fe':
        logger.info("Performing feature engineering tasks")
        client_gcs = storage.Client()
        submission_config_exists = check_submission_config_file_exists(
            client=client_gcs, bucket_name=args.bucket,
            source_blob_name=args.submission_config_blob)
        if submission_config_exists:
            fe_config_obj = get_config_obj_from_submission(
                action="feature_engineering",
                client=client_gcs,
                bucket_name=args.bucket,
                source_blob_name=args.submission_config_blob)
            job_transport = (
                job_controller_grpc_transport.JobControllerGrpcTransport(
                    address='{}-dataproc.googleapis.com:443'.format(args.region)))
            dataproc_job_client = dataproc_v1.JobControllerClient(job_transport)
            # jar file for bq connector
            jar_file_uris_bq_connector = ["gs://spark-lib/bigquery/spark-bigquery-latest.jar"]

            run_submit_job_to_dataproc_cluster(region=args.region,
                                               cluster_name=args.cluster_name,
                                               pyspark_file_path=args.pyspark_file,
                                               other_python_file_path=args.other_python_files,
                                               jar_file_uris=jar_file_uris_bq_connector,
                                               config_obj=fe_config_obj,
                                               dataproc_job_client=dataproc_job_client)
        else:
            assert submission_config_exists, "Submission yaml file is not found in the GCS bucket, please upload!"


def run():
    """

    """
    main(sys.argv[1:])


if __name__ == '__main__':
    run()
