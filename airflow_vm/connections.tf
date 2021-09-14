provider "google-beta" {
  credentials = file("/Users/yeso/workspace/ds_gcp_tools_pool/gcp_key/ford-battery-dev-a02cec3b8ccf.json")
  project     = var.host_project_id
  region      = var.region
  #version = "~> 3.17.0"
}

provider "google" {
  credentials = file("/Users/yeso/workspace/ds_gcp_tools_pool/gcp_key/ford-battery-dev-a02cec3b8ccf.json")
  project     = var.host_project_id
  region      = var.region
  #version = "~> 3.17.0"
}
