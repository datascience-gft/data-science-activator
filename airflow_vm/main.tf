
### Create VM from a machine image in another project.
# terraform example: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance_from_machine_image
resource "google_compute_instance_from_machine_image" "tpl" {
  provider = google-beta
  name     = "vm-from-image-of-ford-poc"
  zone     = var.zone

  source_machine_image = "projects/ford-battery-poc/global/machineImages/airflow-mlflow-v2"

  // Override fields from machine image
  // can_ip_forward = false
  labels = {
    scheduled = "true"
  }
  network_interface {
  subnetwork = var.standard_subnetwork
  subnetwork_project = var.host_project_id
  access_config {
  }
  }
  #boot_disk {
  #  initialize_params {
  #    size  = 100
  #  }
  #}
  service_account {
    scopes = ["cloud-platform"]
  }
}

### Cloud SQL PostgresSQL instance
# terraform example: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/sql_database_instance
resource "google_compute_global_address" "private_ip_address" {
  provider = google-beta

  name          = "private-ip-address"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = var.standard_network
}

resource "google_service_networking_connection" "private_vpc_connection" {
  provider = google-beta

  network       = var.standard_network
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}


resource "google_sql_database_instance" "postgressql" {
  provider = google-beta
  database_version = "POSTGRES_13"
  name             = "experiment-tracking-db"
  project       = var.host_project_id
  depends_on = [google_service_networking_connection.private_vpc_connection]

  settings {
    tier              = "db-custom-2-13312"
    availability_type = "ZONAL"
    disk_autoresize   = true
    disk_size         = 250
    ip_configuration {
      ipv4_enabled    = false
      private_network = var.standard_network
	}

    location_preference {
      zone = var.zone
    }
  }

}

### Cloud SQL database
# terraform example: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/sql_database
resource "google_sql_database" "database" {
  name     = "mlflow"
  instance = google_sql_database_instance.postgressql.name
}


### Cloud SQL database
# terraform example: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/sql_user
resource "google_sql_user" "users" {
  name     = "mlfow"
  instance = google_sql_database_instance.postgressql.name
  password = "mlfow"
}

### Cloud Storage
# terraform example: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket

resource "google_storage_bucket" "airflow" {
  name          = "${var.host_project_id}-airflow"
  location      = var.region
  project       = var.host_project_id
  force_destroy = "true"

  labels = {
    logical_functional_zone = "ai-dev"
    logical_group           = "ai"
    logical_group_types     = "store"
  }
}
resource "google_storage_bucket" "mlflow"{
  name          = "${var.host_project_id}-mlflow"
  location      = var.region
  project       = var.host_project_id
  force_destroy = "true"

  labels = {
    logical_functional_zone = "ai-dev"
    logical_group           = "ai"
    logical_group_types     = "store"
  }
}
resource "google_storage_bucket" "great_expectations" {
  name          = "${var.host_project_id}-great_expectations"
  location      = var.region
  project       = var.host_project_id
  force_destroy = "true"

  labels = {
    logical_functional_zone = "ai-dev"
    logical_group           = "ai"
    logical_group_types     = "store"
  }
}
