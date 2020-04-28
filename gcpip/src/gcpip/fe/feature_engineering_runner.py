import sys

import argparse
from feature_engineering_functions import execute


def get_args(args):
    """
    Parse command line arguments

    Returns: args object

    """
    # defined command line options
    CLI = argparse.ArgumentParser()

    CLI.add_argument(
        "--input_table",
        type=str,
        default="market_dataset.market_data")

    CLI.add_argument(
        "--output_table",
        type=str,
        default="market_dataset.market_data_fe")

    CLI.add_argument(
        "--temporary_gcs_bucket",
        type=str,
        default="")

    # moving average arguments (optional)
    CLI.add_argument(
        "--ma",
        type=str,
        default="False")

    CLI.add_argument(
        "--ma_target_columns",
        nargs="*",
        type=str,
        default=["High", "Low", "Open", "Volume"])

    CLI.add_argument(
        "--ma_time_intervals",
        nargs="*",
        type=int,
        default=[5, 20, 60])

    CLI.add_argument(
        "--ma_group_column",
        type=str,
        default="ticker")
    CLI.add_argument(
        "--ma_sort_column",
        type=str,
        default="Date")

    # mid price arguments (optional)
    CLI.add_argument(
        "--mp",
        type=str,
        default="False")

    CLI.add_argument(
        "--mp_col1",
        type=str,
        default="High")
    CLI.add_argument(
        "--mp_col2",
        type=str,
        default="Low")

    # spread arguments (optional)
    CLI.add_argument(
        "--spread",
        type=str,
        default="False")
    CLI.add_argument(
        "--spread_col1",
        type=str,
        default="High")
    CLI.add_argument(
        "--spread_col2",
        type=str,
        default="Low")

    # parse the command line
    args = CLI.parse_args()
    return args


def main(args):
    fe_parameters = get_args(args)
    spark_config_properties = [('spark.executor.memory', '2g'),
                               ("spark.sql.execution.arrow.enabled", "true"),
                               ("spark.driver.maxResultSize", "2g"),
                               ("spark.driver.memory", "3g"),
                               ("temporaryGcsBucket", fe_parameters.temporary_gcs_bucket)]
    execute(fe_parameters, spark_config_properties)


def run():
    main(sys.argv[1:])


if __name__ == '__main__':
    run()
