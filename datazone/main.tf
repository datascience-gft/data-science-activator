# Google Storage
resource "google_storage_bucket" "landing_data" {
  name          = "${var.host_project_id}-${var.landing_bucket_name}"
  location      = var.region
  project       = var.host_project_id
  force_destroy = "true"

  labels = {
    logical_functional_zone = "landing"
    logical_group           = "landing-group"
    logical_group_types     = "store"
  }
}

resource "google_storage_bucket" "staging_bucket" {
  name          = "${var.host_project_id}-${var.staging_bucket_name}"
  location      = var.region
  project       = var.host_project_id
  force_destroy = "true"

  labels = {
    logical_functional_zone = "staging"
    logical_group           = "staging-group"
    logical_group_types     = "store"
  }
}



resource "google_storage_bucket_object" "market_data" {
  name   = "prepared_data/market_data.csv"
  source = "market_data.csv"
  bucket = google_storage_bucket.landing_data.name

}


# Google Compute Engines
resource "google_compute_instance" "vm_instance" {
  name         = var.vm1_name
  machine_type = var.vms_machine_type
  zone         = var.zone

  metadata = {
    startup-script = file("init_vms.sh")
  }

  boot_disk {
    initialize_params {
      image = "ubuntu-1404-trusty-v20190514"
      size  = var.vms_size
    }
  }
  service_account {
    scopes = ["useraccounts-ro", "storage-rw", "logging-write", "bigquery", "compute-rw"]
  }

  allow_stopping_for_update = true

  tags = ["dsactivatortag1", "dsactivatortag2"] 
  network_interface {
   subnetwork = var.standard_subnetwork
   subnetwork_project = var.host_project_id
    access_config {
    }
  }
}

