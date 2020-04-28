# Building google dataproc cluster

resource "google_dataproc_cluster" "dataproc-cluster" {
  name   = "dataproc-cluster"
  region = var.region

  cluster_config {
    staging_bucket = google_storage_bucket.staging_bucket.name


    master_config {

      num_instances = 1
      machine_type  = "custom-1-6656-ext"

      disk_config {

        boot_disk_type    = "pd-ssd"
        boot_disk_size_gb = 100
      }

    }

    worker_config {
      num_instances = var.dataproc_workers_num_instances
      machine_type  = var.dataproc_workers_machine_type
      disk_config {
        boot_disk_size_gb = var.dataproc_workers_size
        num_local_ssds    = 1
      }
    }

    preemptible_worker_config {
      num_instances = 0
    }

    # Override or set some custom properties
    software_config {
      image_version = "1.3.7-deb9"
      override_properties = {
        "dataproc:dataproc.allow.zero.workers" = "true"
      }
    }


    gce_cluster_config {
      #metadata = {
       # startup-script = file("init_dataproc.sh")
      #}
#EDW

	zone = var.zone
#	network = var.vpc_network 
	subnetwork = var.standard_subnetwork

	tags = ["dsactivatortag1", "dsactivatortag2"]


      service_account_scopes = [
        #   User supplied scopes
        "https://www.googleapis.com/auth/monitoring",
        "useraccounts-ro", "storage-rw", "logging-write", "bigquery", "compute-rw"
      ]
    }
  }
  timeouts {
    create = "60m"
    delete = "60m"
  }
}

