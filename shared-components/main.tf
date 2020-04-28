# Copyright 2019 The Tranquility Base Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

###
# Shared VPC setup
###

#resource "google_compute_shared_vpc_host_project" "host" {
#  project = var.host_project_id
#}

###
# Network and Subnetworks
###

resource "google_compute_network" "shared_network" {
  name                    = var.shared_vpc_name
  auto_create_subnetworks = "false"
  routing_mode            = "REGIONAL"
  project                 = var.host_project_id
  #depends_on              = [google_compute_shared_vpc_host_project.host]
}

resource "google_compute_subnetwork" "standard-subnetwork" {
  count            = length(var.standard_network_subnets)
  name             = var.standard_network_subnets[count.index]["name"]
  ip_cidr_range    = var.standard_network_subnets[count.index]["cidr"]
  region           = var.region
  project          = var.host_project_id
  network          = google_compute_network.shared_network.name
  #enable_flow_logs = var.enable_flow_logs

  #labels           = "${var.tags}"
  depends_on = [google_compute_network.shared_network]
}

resource "google_compute_subnetwork" "gke-subnetwork" {
  count                    = length(var.gke_network_subnets)
  name                     = var.gke_network_subnets[count.index]["name"]
  ip_cidr_range            = var.gke_network_subnets[count.index]["cidr"]
  region                   = var.region
  private_ip_google_access = true
  project                  = var.host_project_id
  network                  = google_compute_network.shared_network.name
  #enable_flow_logs         = var.enable_flow_logs

  #labels           = "${var.tags}"
  depends_on = [google_compute_network.shared_network]

  # Kubernetes Secondary Networking
  secondary_ip_range {
    range_name    = var.gke_pod_network_name
    ip_cidr_range = var.gke_network_subnets[count.index]["pod_cidr"]
  }

  secondary_ip_range {
    range_name    = var.gke_service_network_name
    ip_cidr_range = var.gke_network_subnets[count.index]["service_cidr"]
  }
}

resource "google_compute_subnetwork" "ds-bastion-subnetwork" {
  name                     = "bastion-subnetwork"
  ip_cidr_range            = "10.0.6.0/24"
  region                   = var.region
  private_ip_google_access = true
  project                  = var.host_project_id
  network                  = google_compute_network.shared_network.name
  depends_on = [google_compute_network.shared_network]
}
###
# Additional Networking Resources
###
resource "google_compute_address" "static" {
  name   = "nat-static-ip"
  project = var.host_project_id
}

resource "google_compute_router" "router" {
  name    = var.router_name
  network = google_compute_network.shared_network.self_link
  project = var.host_project_id
  region  = var.region
}

resource "google_compute_router_nat" "simple-nat" {
  count                              = var.create_nat_gateway ? 1 : 0
  name                               = var.router_nat_name
  project                            = var.host_project_id
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "MANUAL_ONLY"
  nat_ips                             = google_compute_address.static.*.self_link
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}


resource "google_compute_firewall" "fwegress" {
  name    = "fwegress"
  #network = google_compute_network.default.name
  network = google_compute_network.shared_network.self_link
  enable_logging = false
  priority = "1000"
  direction = "EGRESS"
  disabled = false
  # Why 10.1.2.0/24? This needs to be checked.
  destination_ranges = ["10.1.2.0/24"]
  target_tags = ["dsactivatortag1", "dsactivatortag2"]

  allow {
    protocol = "icmp"
  }
}


resource "google_compute_firewall" "fwingress" {
  name    = "fwingress"
  #network = google_compute_network.default.name
  network = google_compute_network.shared_network.self_link
  enable_logging = false
  priority = "1000"
  direction = "INGRESS"
  disabled = false
  target_tags = ["dsactivatortag1", "dsactivatortag2"]


  allow {
    protocol = "icmp"
  }



}
resource "google_compute_firewall" "mssb-sandbox-vpc-allow-http" {
  name    = "mssb-sandbox-vpc-allow-http"
  #network = google_compute_network.default.name
  network = google_compute_network.shared_network.self_link
  enable_logging = false
  priority = "1000"
  direction = "INGRESS"
  disabled = false
  # why 0.0.0.0/0? This opens it up to all the IPs. How does this work with
  # VPC? is VPC stop the outside connections.
  source_ranges = ["0.0.0.0/0"]
  target_tags = ["http-server"]

  allow {
    protocol = "icmp"
  }
}

resource "google_compute_firewall" "mssb-sandbox-vpc-allow-https" {
  name    = "mssb-sandbox-vpc-allow-https"
  #network = google_compute_network.default.name
  network = google_compute_network.shared_network.self_link
  enable_logging = false
  priority = "1000"
  direction = "INGRESS"
  disabled = false
  # why 0.0.0.0/0? This opens it up to all the IPs. How does this work with
  # VPC? is VPC stop the outside connections.
  source_ranges = ["0.0.0.0/0"]
  target_tags = ["http-server"]

  allow {
    protocol = "icmp"
  }
}

resource "google_compute_firewall" "all-ssh" {
  name    = "all-ssh"
  #network = google_compute_network.default.name
  network = google_compute_network.shared_network.self_link
  enable_logging = false
  priority = "1000"
  direction = "INGRESS"
  disabled = false
  target_tags = ["dsactivatortag1", "dsactivatortag2"]


  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
  #  ports    = ["80", "8080", "1000-2000"]
    # Why 1-65535?
    ports    = ["1-65535"]
  }

}



###
# Attaching service projects
###

#resource "google_compute_shared_vpc_service_project" "service_project" {
#  count           = var.service_projects_number
#  host_project    = var.host_project_id
#  service_project = var.service_project_ids[count.index]

  #labels          = "${var.tags}"
#  depends_on = [
#    google_compute_shared_vpc_host_project.host,
#    google_compute_subnetwork.gke,
#    google_compute_subnetwork.standard,
#  ]
#}
