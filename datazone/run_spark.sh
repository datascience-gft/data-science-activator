#!/bin/sh

gcloud dataproc jobs submit pyspark $1  --cluster dataproc-cluster --region europe-west2 --jars=gs://spark-lib/bigquery/spark-bigquery-latest.jar

