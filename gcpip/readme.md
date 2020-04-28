# gcpip

Data pipeline for GCP to create a Cloud Storage data lake and a Big Query data warehouse.

## Description

This package contains tools for moving data into the cloud, creating pipelines from the data landing zone to a Big Query
data warehouse and performing feature engineering tasks using Dataproc.

There are four main functions of the package:
1. Migrate data external to GCP to a controlled data landing zone within GCS.
2. Run ETL pipelines taking data from GCS to a warehouse in BQ.
3. Create views of requested data for access by wider team.
4. Perform feature engineering tasks, such as calculation of moving average, etc.

To run call `python runner.py` via terminal. The `runner.py` file with the given `action` 
(e.g, `fe` for feature engineering) first read the submission configuration file at the given location from the GCS 
bucket and decide where to get the task-specific configuration file. Then, execute the ETL tasks as configured.

## Installation

To install package, change working directory to package parent directory and run, `python setup.py install`.

## Tests
Unit tests are provided to confirm the package functions properly in your environment. 
To run tests run, `pytest` in terminal.

## The configuration files
There are two types of configuration files (in _yaml_ format): 
submission configuration files defining each submission and the task-specific configuration files defining the
configurations of different tasks, such as the load configuration file, view configuration file and 
feature engineering configuration files. They are stored in the GCS data-landing bucket and usually put in two 
different folders for the purpose of classification. For example, put submission configuration files in submissions 
folder and put task-specific configuration files in meta folder, but this is not necessary.

### The submission configuration files
```yaml
submissions:
    submission1:
        submission_name: test_sub2
        metadata_file: bucket1/meta/load1.yaml
        data_file: bucket1/data/data1.csv
        action: load
    submission2:
        submission_name: test_sub2
        metadata_file: bucket1/meta/view.yaml
        action: view
    submission3:
        submission_name: test_sub3
        metadata_file: bucket1/meta/fe.yaml
        action: feature_engineering
```

An example submission configuration file can be found at [submission_example.yaml](resources/config/submission_example.yaml).
There are three fields in each submission: the `submission_name`, `metadata_file` and the `action`.

- `submission_name`: is the name of the submission;
- `metadata_file`: is the path of the metadata blob in the GCS-data-landing bucket, in the form of
  `<bucket name>/<folder name>/<configuration file name>`;
- `action`: defines the types of the submission and it can be one of the following three values:
    - `load`: is for loading files from GCS bucket to a table in a BigQuery dataset
    - `view`: is for generating BigQuery views from tables in BigQuery dataset
    - `feature_engineering`: is for performing feature engineering tasks, such as calculation of moving average,
      mid-price and spread.

### Task-specific configuration files

The task-specific configuration files define the configurations for individual tasks.
They are stored in the GCS bucket at the location defined as the `metadata_file` of the submission configuration file.

#### The load configuration file
```yaml
key_file:
project_id:
mode: big_query
sources:
  source1:
    bucket_id: data-sc-activation-test-bucket
    file_path: test/upload_example1.csv
    file_type: csv
    skip_leading_rows: 1
destination:
  schema:
    field1:
      name: name
      type: STRING
      mode: required
    field2:
      name: birth_date
      type: STRING
      mode: nullable
    field3:
      name: register_date
      type: STRING
      mode: nullable
    field4:
      name: credit_card
      type: INTEGER
      mode: nullable
    field5:
      name: password
      type: STRING
      mode: required
  dataset: landing_data
  table: landing_table17
```
An example load configuration file can be found at 
[load_example.yaml](resources/config/load_example.yaml). Key configuration fields are:

- `key_file`: defines the location of the GCP credentials;
- `project_id`: is the GCP project id;
- `mode`: defines the mode of the loading, such as `big_query` for loading data from GCS bucket to BigQuery table;
- `sources`: defines the source file information such as `path`, `type`, `with/without header`;
- `destination`: defines the destination location, `dataset` and `table` and the `schema` of the destination table

#### The view configuration file
```yaml
views:
  view1:
    view_name: test_BQ_view1
    project_id_des: data-science-activator
    dataset_des: dataset_for_holding_views
    cols:
      col1:
        name_des: Date
        name_src: Date
        project_id_src: data-science-activator
        dataset_src: market_dataset
        table_src: market
        condition:
      col2:
        name_des: Open
        name_src: Open
        project_id_src: data-science-activator
        dataset_src: market_dataset
        table_src: market
        condition:
      col3:
        name_des: Close
        name_src: Close
        project_id_src: data-science-activator
        dataset_src: market_dataset
        table_src: market
        condition:
```
An example BigQuery view generation configuration file can be found at [view.yaml](resources/config/view.yaml). 
Key configuration fields are:

- `view_name`: is the name of the BigQuery view;
- `project_id_des`: is the destination project id of the BigQuery view;
- `dataset_des`: is the BigQuery dataset where the views are generated;
- `cols`: defines the properties of each columns, such as the `source project id`, `dataset` and `table`, `column name` 
  and the `destination column name`, and the `condition`

#### Feature engineering file

```yaml
project_id:
source_dataset:
source_table:
destination_table:
destination_dataset:
staging_bucket:
engineered_features:
    engineered_feature1:
        name: moving_average
        target_columns:
            - High
            - Low
            - Open
            - Volume
        parameters:
            parameter1:
              name: time_intervals
              value:
                - 5
                - 20
                - 60
            parameter2:
              name: group_column
              value:
                - ticker
            parameter3:
              name: sort_column
              value:
                - Date
    engineered_feature2:
        name: mid_price
        target_columns:
            - High
            - Low
    engineered_feature3:
        name: spread
        target_columns:
            - High
            - Low
```


An example feature engineering configuration file can be found at [fe_example.yaml](resources/config/fe_example.yaml). 
Key configuration fields are listed below and they need to be updated according to the requirements of each individual 
feature engineering tasks:

- `project_id`: is the project id;
- `source_dataset`: the source BigQuery dataset name;
- `source_table`: the source BigQuery table (or view) name;
- `destination_table`: the destination BigQuery table name;
- `destination_dataset`: the destination BigQuery dataset name;
- `staging_bucket`: is the temporary staging bucket for performing feature engineering tasks;
- `engineered_features`: defines each engineered feature configurations;
  such as `name` defines the type of the feature engineering, e.g., moving_average, mid-price and spread,
  `target_column` specifies the columns selected for feature engineering from the source table (or view), 
  `parameters` list the feature engineering related parameters

## Basic operations
Four basic operations are listed below as examples of using gcpip for ETL tasks. Before running each task, it is
recommended to set the following variables for the convenience:
```shell script
BUCKET=<name of the data landing bucket>
SUBMISSION_BLOB=<path of the submission configuration blob>
CLUSTER_NAME=<dataproc cluster name>
REGION=<region of the GCP project>
PYSPARK_FILE_PATH=<local path of the pyspark file>
OTHER_PYTHON_FILE=<local path of the complementary python file>
```
For example:
```shell script
BUCKET=data-science-activator-landing-data-bucket-mssb-sandbox
SUBMISSION_BLOB=submissions/submission_config.yaml
CLUSTER_NAME=dataproc-cluster
REGION=europe-west2
PYSPARK_FILE_PATH=fe/feature_engineering_runner.py
OTHER_PYTHON_FILE=fe/feature_engineering_functions.py
```

### Data migration

This package can be used to upload data external to GCP into GCS. Tools are provided to encrypt data locally before 
transit using Cloud KMS.

To encrypt and upload data run the following command on a machine with the data to migrate,

```shell script
python runner.py upload --action=encrypted --config_file=path/to/config/file.yaml --bucket=gcp_bucket_name --source=path/to/file --destination=path/to/destination --key==id_kms_key --keyring=id_kms_key_ring --location location_of_resources
```

This will upload the encrypted data file and also a key to decrypt the data. The data encryption key is also encrypted 
before transit using Cloud KMS. The encrypted file will have a `.encrypted` extension added and the key will be named after the file but with a `.dek` extension.

Once uploaded run this command on a GCP VM,

```shell script
python runner.py decrypt --config_file=path/to/config/file.yaml --bucket=gcp_bucket_name --source=path/to/file --key=id_kms_key --keyring=id_kms_key_ring --location=location_of_resources
```

This will decrypt the data, remove the `.encrypted` extension and delete the data encryption key. The data located 
within GCS will only be accessible to a GCP service account which runs this service. Human interaction should only 
occur with data located within a Big Query View.

### Data loading

Once data is within the GCS landing zone requests can be made for data to be loaded to BigQuery. 
To request a data load a user should upload a submission config file requesting a load job and a load config file 
providing details of the job. Once these files are uploaded a load can be started by running,

```shell script
python runner.py load --bucket=$BUCKET --submission_config_blob=$SUBMISSION_BLOB
```
It first checks if the submission configuration file exists at the GCS bucket ```$BUCKET``` as specified as 
```$SUBMISSION_BLOB```. If the submission file exists, it will read the path of the loading configuration file at 
the path specified in the `metadata_file` field from the submission with the `action` of `loading`. 
Then, the data will be loaded into BQ following the specifications in the load config.

### Create BigQuery views

To generate BigQuery views from tables in Bigquery, run

```shell script
python runner.py bq_view --bucket=$BUCKET --submission_config_blob=$SUBMISSION_BLOB
```
Similar to "Data loading" above, if the submission configuration file exists at the GCS bucket ```$BUCKET``` as 
specified as ```$SUBMISSION_BLOB```, it will read the path of the view configuration file at the path specified in 
the `metadata_file` field from the submission with the `action` of `view`. 
Then, views will be created following the specifications in the view config.

### Feature engineering

Run the following to perform feature engineering tasks:

```shell script
python runner.py fe --region=$REGION --bucket=$BUCKET --pyspark_file=$PYSPARK_FILE_PATH --submission_config_blob=$SUBMISSION_BLOB --cluster_name=$CLUSTER_NAME --other_python_files=$OTHER_PYTHON_FILE
```
Similarly, it first goes to the GCS bucket ```$BUCKET``` to find the submission configuration file 
at ```$SUBMISSION_BLOB```. If the submission file exists, it will read the path of the feature engineering
configuration file at the path specified in the `metadata_file` field from the submission with the `action` of 
`feature_engineering`. Then, it goes to fetch the feature engineering configuration file and read the feature 
engineering configurations from it. 

Next, it creates a `dataproc_job_client` object using:
```python
job_transport = (
                job_controller_grpc_transport.JobControllerGrpcTransport(
                    address='{}-dataproc.googleapis.com:443'.format(args.region)))
dataproc_job_client = dataproc_v1.JobControllerClient(job_transport)
```
Finally, it submits a pyspark job to Dataproc cluster `$CLUSTER_NAME` where it performs the feature
engineering tasks (e.g., calculation of moving average, mid-price and spread) as configured. 
The following items  need to be included in the `job_details` of the submission:
1. `main_python_file_uri`: The HCFS URI of the main Python file to use as the driver. In this case, it is
[feature_engineering_runner.py](src/gcpip/fe/feature_engineering_runner.py) uploaded 
to the staging bucket from as specified locally at `$PYSPARK_FILE_PATH`.
2. `python_file_uris`: HCFS file URIs of Python files to pass to the PySpark framework. It is 
[feature_engineering_functions.py](src/gcpip/fe/feature_engineering_functions.py) specified at `$OTHER_PYTHON_FILES` 
uploaded to the staging bucket.
3. `jar_file_uris`: URIs of jar files to add to the CLASSPATHs of the Python driver and tasks.
4. `args`: which is a list of arguments to pass to the driver. In this case, it is parsed from the 
feature_engineering configuration file.

```python
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
```
Further information about the job details of a pyspark job submitted to Dataproc can be found at 
[Pyspark job](https://cloud.google.com/dataproc/docs/reference/rpc/google.cloud.dataproc.v1#pysparkjob).

## Further readings

Apache Spark SQL connector for Google BigQuery https://github.com/GoogleCloudDataproc/spark-bigquery-connector

Dataproc job recources
https://cloud.google.com/dataproc/docs/reference/rpc/google.cloud.dataproc.v1#job
