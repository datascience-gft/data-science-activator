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

variable "host_project_id" {
  type        = string
  default     = ""
  description = "Identifier for the host project to be used"
}

variable "shared_vpc_name" {
  type        = string
  default     = "shared-network"
  description = "Name for the shared vpc network"
}

variable "standard_network_subnets" {
  type        = list(object({
    name = string
    cidr = string
  }))
  default     = [{ name = "main-network-subnet", cidr = "10.1.2.0/24"}]
  description = "cidr ranges for standard (non-gke) subnetworks"
}

variable "region" {
  type        = string
  default     = "europe-west2"
  description = "region name"
}

variable "enable_flow_logs" {
  type        = string
  default     = "false"
  description = "Boolean value to determine whether to enable flowlogs in subnet creation"
}

variable "gke_network_subnets" {
  type        = list(object({
    name = string
    cidr = string
    pod_cidr = string
    service_cidr = string
  }))
  default     = [{ name = "gke-network-subnet", cidr = "10.2.0.0/24", pod_cidr = "10.3.0.0/20", service_cidr = "10.4.0.0/21"}]
  description = "cidr ranges for gke subnetworks"
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

variable "tags" {
  type        = map(string)
  default     = {}
  description = "A map of tags to add to all resources"
}

variable "router_name" {
  type        = string
  default     = "vpc-network-router"
  description = "router name"
}

variable "create_nat_gateway" {
  type        = string
  default     = "true"
  description = "Boolean value to determine whether to create a NAT gateway"
}

variable "router_nat_name" {
  type        = string
  default     = "vpc-network-nat-gateway"
  description = "Name for the router NAT gateway"
}

variable "service_project_ids" {
  type        = list(string)
  default     = []
  description = "Associated service projects to link with the host project."
}

variable "service_projects_number" {
  type        = string
  default     = "activator-kubernetes"
  description = "Number of service projects attached to shared vpc host"
}

