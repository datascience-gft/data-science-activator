resource "google_project_service" "iam_googleapi_enable" {
  project = var.host_project_id
  service = "iam.googleapis.com"

  disable_dependent_services = false
  disable_on_destroy = true
}


resource "google_project_service" "compute_googleapis_enable" {
  project = var.host_project_id
  service = "compute.googleapis.com"

  disable_dependent_services = false
  disable_on_destroy = true
}

resource "google_project_service" "container_googleapis_enable" {
  project = var.host_project_id
  service = "container.googleapis.com"

  disable_dependent_services = false
  disable_on_destroy = true
}

resource "google_project_service" "dataproc_api_enable" {
  project = var.host_project_id
  service = "dataproc.googleapis.com"

  disable_dependent_services = false
}

