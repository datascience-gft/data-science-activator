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

variable "region" {
  type        = string
  default     = "europe-west2"
  description = "The region to host the cluster in"
}

variable "sharedvpc_project_id" {
  default     = ""
  type = string
}

variable "sharedvpc_network" {
  type = string
  default     = "shared-network"
}

variable "cluster_project_id" {
  description = "The project ID to host the cluster in"
  default     = "activator-kubernetes"
}

variable "cluster_name" {
  description = "The cluster name"
  default     = "ds-kubernet-cluster"
}

variable "cluster_pool_name" {
  description = "The cluster pool name"
  default     = "ds-kubernet-pool"
}

variable "cluster_machine_type" {
  type    = string
  default = "n1-standard-2"
}

variable "cluster_enable_private_nodes" {
  default = "false"
  type    = string
}

variable "cluster_master_cidr" {
  type = string
  default = "172.16.0.32/28"
  #default = "10.2.0.0/24"
}

variable "cluster_subnetwork" {
  type = string
  default = "gke-network-subnet"
  description = "The subnetwork to host the cluster in"
}

variable "cluster_service_account" {
  description = "Service account to associate to the nodes in the cluster"
  default = "gke-service-acc"
}

variable "cluster_service_account_roles" {
  type        = list(string)
  default     = ["roles/compute.viewer", "roles/container.clusterAdmin", "roles/container.developer", "roles/iam.serviceAccountAdmin", "roles/iam.serviceAccountUser", "roles/resourcemanager.projectIamAdmin"]
  description = "Service account to associate to the nodes in the cluster"
}

variable "pod-mon-service" {
  type    = string
  default = "monitoring.googleapis.com/kubernetes"
}

variable "pod-log-service" {
  type    = string
  default = "logging.googleapis.com/kubernetes"
}

variable "cluster_min_master_version" {
  default     = "latest"
  description = "Master node minimal version"
  type        = string
}

variable "cluster_autoscaling_min_nodes" {
  type    = string
  default = "1"
}

variable "cluster_autoscaling_max_nodes" {
  type    = string
  default = "3"
}

variable "cluster_master_authorized_cidrs" {
  type = list(object({
    cidr_block = string
    display_name = string
  }))
  default = [{display_name = "cidr", cidr_block = "10.2.0.0/24"}, {display_name="pod_cidr", cidr_block = "10.3.0.0/20"}, {display_name="service_cidr", cidr_block = "10.4.0.0/21"}]
}

variable "cluster_daily_maintenance_start" {
  type    = string
  default = "02:00"
}

variable "cluster_node_disk_size" {
  type    = string
  default = "10"
}

variable "cluster_oauth_scopes" {
  type = list(string)
  default = [
    "compute-rw",
    "storage-ro",
    "logging-write",
    "monitoring",
    "https://www.googleapis.com/auth/userinfo.email",
  ]
}

#variable "apis_dependency" {
#  type        = string
#  description = "Creates dependency on apis-activation module"
#}

#variable "shared_vpc_dependency" {
#  type        = string
#  description = "Creates dependency on shared-vpc module"
#}

variable "istio_permissive_mtls" {
  type    = string
  default = "false"
}

variable "istio_status" {
  type    = string
  default = "true"
}

variable "gke_pod_network_name" {
  type        = string
  default     = "gke-pods-snet"
  description = "Name for the gke pod network"
}

variable "gke_service_network_name" {
  type        = string
  default     = "gke-services-snet"
  description = "Name for the gke service network"
}

