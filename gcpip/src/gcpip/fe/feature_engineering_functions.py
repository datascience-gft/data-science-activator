#!/opt/anaconda3/bin/python


from __future__ import print_function

from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.context import SparkContext
from pyspark.sql.window import Window
from pyspark.sql import functions as func


def create_spark_session(config_properties):
    """
    This function create a SparkContext connection and return SparkSession
    object.
    Returns (SparkSession)

    """
    sc_conf = SparkConf()
    for sc_conf_property in config_properties:
        sc_conf.set(sc_conf_property[0], sc_conf_property[1])
    sc = SparkContext(conf=sc_conf)
    spark = SparkSession(sc)

    return spark


def read_data_from_bq(table_id, spark_session):
    """
    This function read the data to PySpark dataframe from a bq table.
    Args:
        table_id (str): Table id,  dataset_id + '.' + tablename
        spark_session (SparkSession): SparkSession object

    Returns (PySpark dataframe): PySpark dataframe of bq table data.

    """
    sdf = spark_session.read.format('bigquery') \
        .option('table', table_id) \
        .option('viewsEnabled', 'true') \
        .load()
    sdf = sdf.orderBy(['Date'])
    return sdf


def write_to_bq(sdf, table_id):
    """
    This function write the data from pyspark dataframe to a bq table.
    Args:
        sdf (Spark dataframe): Spark dataframe
        table_id (str): Table id,  dataset_id + '.' + tablename
    Returns: write the data into a table and print the success report.

    """
    sdf.write.mode('overwrite').format('bigquery') \
        .option('table', table_id) \
        .save()


def cal_simple_moving_average(sdf, col_name, n_days, group_col, sort_col):
    """
    This function calculate the simple moving average (sma) on a column from a
    pyspark dataframe, and add a new column sma_col_name_n_days, that has
    the sma result.
    Args:
        sdf (Spark dataframe): Spark dataframe
        col_name (str): Name of the column to calculate moving average
        n_days (int): Number of days back to calculate moving average
        group_col (str): Name of the column to group by the data.
        sort_col (str): Name of the column to order the data.

    Returns (Spark dataframe): Return Spark dataframe with new column
    sma_col_name_n_days, that has he sma result

    """
    sdf = sdf.withColumn('sma_{}_{}'.format(col_name, n_days),
                         func.avg(col_name).over
                         (Window.partitionBy(group_col).orderBy([
                             sort_col]).rowsBetween(-n_days, 0)))

    return sdf


def cal_mid(sdf, col1, col2):
    """
    This function calculate mid price of two given columns of a pyspark
    datafrome.
    Args:
        sdf (Spark dataframe): Spark dataframe
        col1 (str): First column name
        col2 (str): Second column name

    Returns (PySpark dataframe): PySpark dataframe of with calculated mid
    price column, named {}_{}_mid

    """
    sdf = sdf.withColumn('{}_{}_mid'.format(col1, col2), (sdf[col1] + sdf[
        col2]) / 2)

    return sdf


def cal_spread(sdf, col1, col2):
    """
    This function calculate spread of two given columns of a pyspark
    datafrome.
    Args:
        sdf (Spark dataframe): Spark dataframe
        col1 (str): First column name
        col2 (str): Second column name

    Returns (PySpark dataframe): PySpark dataframe of with calculated spread
     column, named {}_{}_spread

    """
    sdf = sdf.withColumn('{}_{}_spread'.format(col1, col2), (sdf[col1] - sdf[
        col2]))

    return sdf


def run_moving_averages(sdf, l_cols, l_days, group_col, sort_col):
    """
    This function run simple moving average for multiple columns with
    multiple time interval per calculation
    Args:
        group_col (str): Name of the column to group by the data.
        sort_col (str): Name of the column to order the data.
        sdf (Spark dataframe): Spark dataframe
        l_cols (list(str)): List of columns to calculate moving average.
        l_days (list(int)): List of time interval for moving average
        calculation.

    Returns (PySpark dataframe): PySpark dataframe with all the
    calculated moving averages.

    """
    for col in l_cols:
        for day in l_days:
            sdf = cal_simple_moving_average(sdf=sdf, col_name=col,
                                            n_days=day, group_col=group_col,
                                            sort_col=sort_col)
    return sdf


def execute(fe_parameters, spark_config_properties):
    """
    """

    spark = create_spark_session(spark_config_properties)
    input_table = fe_parameters.input_table
    output_table = fe_parameters.output_table

    sdf_market = read_data_from_bq(table_id=input_table,
                                   spark_session=spark)

    # Manipulate pySpark dataframe
    # moving average
    if fe_parameters.ma == "True":
        sdf_market = run_moving_averages(sdf=sdf_market,
                                         l_cols=fe_parameters.ma_target_columns,
                                         l_days=fe_parameters.ma_time_intervals,
                                         group_col=fe_parameters.ma_group_column,
                                         sort_col=fe_parameters.ma_sort_column)

    # mid price
    if fe_parameters.mp == "True":
        sdf_market = cal_mid(sdf=sdf_market, col1=fe_parameters.mp_col1, col2=fe_parameters.mp_col2)

    # spread
    if fe_parameters.spread == "True":
        sdf_market = cal_spread(sdf=sdf_market, col1=fe_parameters.spread_col1, col2=fe_parameters.spread_col2)

    sdf_market.show(100, False)

    # Writing back the data into bq
    write_to_bq(sdf=sdf_market, table_id=output_table)

    spark.stop()
