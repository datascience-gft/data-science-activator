# Building Bigquery dataset and tables.

resource "google_bigquery_dataset" "big_data" {
  dataset_id  = "market_dataset"
  description = "This is a test description"
  location    = var.region

  labels = {
    env = "default"
  }
}

# This dataset is for holding different views for the other dataset
resource "google_bigquery_dataset" "big_data_copy" {
  dataset_id  = "dataset_for_holding_views"
  description = "This dataset is used to hold views of data from the other dataset."
  location    = var.region

  labels = {
    env = "default"
  }
}

resource "google_bigquery_table" "big_table" {
  dataset_id = google_bigquery_dataset.big_data.dataset_id
  table_id   = "market"

  schema = <<EOF
[
    {
        "description": "DESCRIPTION",
        "name": "Date",
        "type": "String",
        "mode": "Required"
    },
    {
        "description": "DESCRIPTION",
        "name": "High",
        "type": "FLOAT64",
        "mode": "Required"
    },
    {
        "description": "DESCRIPTION",
        "name": "Low",
        "type": "FLOAT64",
        "mode": "Required"
    },
    {
        "description": "DESCRIPTION",
        "name": "Open",
        "type": "FLOAT64",
        "mode": "Required"
    },
    {
        "description": "DESCRIPTION",
        "name": "Close",
        "type": "FLOAT64",
        "mode": "Required"
    },
    {
        "description": "DESCRIPTION",
        "name": "Volume",
        "type": "FLOAT64",
        "mode": "Required"
    },
    {
        "description": "DESCRIPTION",
        "name": "Adj_close",
        "type": "FLOAT64",
        "mode": "Required"
    },
    {
        "description": "DESCRIPTION",
        "name": "ticker",
        "type": "String",
        "mode": "Required"
    }
]
EOF
}
