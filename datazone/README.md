
# Deploying data landing zone

Pre-requisite to build the data science environment is to build the shared
-components infrastructures, and also terraform has been installed and project and service accounts have already been created.

After that please follow the following steps:

* Update connections.tf and add your service account file (json) to provider "google
", full directory to the your file shall be added to file("").
```hcl-terraform
provider "google" {
  credentials = file("")
  project     = var.cluster_project_id
  region      = var.region
}
```
* Update variables.tf and add your project_id to the following in default = "":
```hcl-terraform
variable "host_project_id" {
  description = "Project ID, example 'data-science-activator'"
  default     = ""
}
```

You can run terraform as follow:
```shell script
terraform init

terraform validate
 
terraform plan 

terraform apply
```

This activator builds the following components:
    
 
  
## Resources:
### GCE (Google Cloud Compute) 
Virtual machines that can be used to perform ETL tasks. This activator creates 1 virtual machines. The types of machine can be
 configured at terraform apply stage using the following variable:
 
 ```
 vms_machine_type: Machine type of the virtual both machines, example 'n1-standard-2'
 ``` 

It also installs important python packages such as: 
* pandas
* numpy
* scikit-learn
* tensorflow
* keras
* pytorch
* google-cloud-storage
* google-cloud-bigquery
* google-cloud-sdk
* google-cloud-core
* gcsfs
* plotly
* pip
* pyspark  
 

### GCS (Google Cloud Storage)
In this activator, we creates two google storage buckets. 
 * landing-data-bucket: To be used for landing incoming data.
 * staging-data-bucket: To be used by Dataproc.
 
There is an example data file 'market_data.csv', which will be uploaded into
 landing-data-bucket as part of this infrastructure building, It will be
  uploaded into ```landing-data-bucket/prepared_data/```.

### BigQuery

BigQuery is a serverless, highly scalable, and cost-effective cloud data
 warehouse. In this infrastructure building task, the following resources
  will be created. 
  * google_bigquery_dataset, named market_dataset
  * google_bigquery_table, named market


### Dataproc cluster
Dataproc is a fast, easy-to-use, fully managed cloud service for running
Apache Spark and Apache Hadoop clusters. In Dataproc creation, the
following specification can be configured:

* dataproc_workers_size: Datapro worker sizes (storage) in GB, example 50.
* dataproc_workers_num_instances: Number of worker instances for dataproc
  cluster, example 3.
* dataproc_workers_machine_type: Machine type for dataproc workers, 
  example 'custom-1-6656-ext'


### Gcpip package 
This is a python package that you can use to:
* Encrypt data 
* Upload encrypted data securely into the infrastructure using Clopud KMS
* Perform DLP 
* Load data into BQ
* Create Views in BQ
* Performing feature engineering using Daraproc