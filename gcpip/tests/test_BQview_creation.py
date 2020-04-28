from gcpip.bq_view_generator import create_bq_views
from gcpip.runner import (check_submission_config_file_exists, check_config_file_exists,
                          get_config_obj_from_submission, get_submission_config_obj)
from google.cloud import bigquery, storage


def test_check_submission_config_file_exists():
    """
    This function tests check_submission_config_file_exists function.
    Returns:

    """
    bucket_name = "data-science-activator-landing-data-bucket-mssb-sandbox"
    source_blob_name = "submissions/submission_config.yaml"
    client_gcs = storage.Client()
    assert check_submission_config_file_exists(client_gcs, bucket_name, source_blob_name)


def test_get_submission_config_obj():
    bucket_name = "data-science-activator-landing-data-bucket-mssb-sandbox"
    source_blob_name = "submissions/submission_config.yaml"
    client_gcs = storage.Client()
    assert get_submission_config_obj(client_gcs, bucket_name, source_blob_name)


def test_check_config_file_exists():
    bucket_name = "data-science-activator-landing-data-bucket-mssb-sandbox"
    blob_name = "meta/view.yaml"
    client_gcs = storage.Client()
    assert check_config_file_exists(client_gcs, bucket_name, blob_name)


def test_get_bq_config_obj_from_submission():
    bucket_name = "data-science-activator-landing-data-bucket-mssb-sandbox"
    source_blob_name = "submissions/submission_config.yaml"
    client_gcs = storage.Client()
    action = "view"
    assert get_config_obj_from_submission(action, client_gcs, bucket_name, source_blob_name)


def test_create_bq_views():
    """

    Tests if BQ views are created accordingly

    """
    client_bq = bigquery.Client()
    client_gcs = storage.Client()
    data_landing_bucket = "data-science-activator-landing-data-bucket-mssb-sandbox"
    submission_config_file = "submissions/submission_config.yaml"
    bq_config_obj = get_config_obj_from_submission(action="view", client=client_gcs, bucket_name=data_landing_bucket,
                                                   source_blob_name=submission_config_file)
    create_bq_views(client=client_bq,
                    bq_config_obj=bq_config_obj)

    # Set dataset_id to the ID of the dataset that contains the tables to be listed
    view_list = list(bq_config_obj.get_views().keys())
    views_exist = True
    for view in view_list:
        view_schema = bq_config_obj.get_views()[view]
        destination_dataset = view_schema['dataset_des']
        view_name = view_schema['view_name']
        project_id = view_schema["project_id_des"]
        views_in_destination_dataset = [x.table_id for x in client_bq.list_tables(destination_dataset)]

        views_exist = views_exist and (view_name in views_in_destination_dataset)

        # delete the views
        table_id = '{}.{}.{}'.format(project_id, destination_dataset, view_name)
        client_bq.delete_table(table_id, not_found_ok=True)  # Make an API request.
        print("Deleted table '{}'.".format(table_id))

    assert views_exist
