import os
from gcpip.config.config_reader import BigQueryViewConfig, FeatureEngineeringConfig
from gcpip.config.config_reader import SubmissionConfig
from google.cloud import bigquery
from google.cloud import storage


def get_sql_query_for_views(bq_config_obj):
    """
    This function create sql queries for big query views
    Note: this function now only performs basic queries (selecting columns from the source table)
    Args:
        bq_config_obj (object): BigQuery configuration object
    Returns:
        sql_queries (dictionary): dictionary for storing sql query of views
    """

    view_list = list(bq_config_obj.get_views().keys())
    sql_queries = {view: "" for view in view_list}
    for view in view_list:
        view_schema = bq_config_obj.get_views()[view]
        cols_list = list(view_schema['cols'].keys())
        sql_columns = ''
        for i, col in enumerate(cols_list):
            col_schema = view_schema['cols'][col]
            project = col_schema['project_id_src']
            source_dataset = col_schema['dataset_src']
            source_table = col_schema['table_src']
            if i > 0:
                sql_columns = sql_columns + ', ' + view_schema['cols'][col]['name_src'] + \
                              " as " + view_schema['cols'][col]['name_des']
            else:
                sql_columns = sql_columns + view_schema['cols'][col]['name_src'] + \
                              " as " + view_schema['cols'][col]['name_des']
            sql_source_table = '`{}.{}.{}`'.format(project, source_dataset, source_table)
        sql_queries[view] = 'SELECT ' + sql_columns + ' FROM ' + sql_source_table
    return sql_queries


def create_bq_views(client, bq_config_obj):
    """
    This function create BQ views from the source_table in the source_dataset
    Args:
        client (bigquery.Client): bigquery.Client object.
        bq_config_obj (object): BigQuery configuration object
    """
    sql_queries = get_sql_query_for_views(bq_config_obj)
    view_list = list(bq_config_obj.get_views().keys())
    for view in view_list:
        view_schema = bq_config_obj.get_views()[view]
        destination_dataset = view_schema['dataset_des']
        view_name = view_schema['view_name']

        destination_dataset_ref = client.dataset(destination_dataset)
        bq_view_ref = destination_dataset_ref.table(view_name)
        bq_view = bigquery.Table(bq_view_ref)

        bq_view.view_query = sql_queries[view]
        bq_view = client.create_table(bq_view, exists_ok=True)  # API request
