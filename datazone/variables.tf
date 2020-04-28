variable "dataproc_workers_machine_type" {
  description = "Machine type for dataproc workers, example 'custom-1-6656-ext'"
  type    = string
  default = "n1-standard-1"
  #default = "custom-1-6656-ext"
}

variable "vm1_name" {
  description = "Name of the first virtual machine, example 'asset-vm-1'"
  default = "vm1"
}

variable "vms_machine_type" {
  description = "Machine type of the virtual machines, example 'n1-standard-2'"
  type    = string
  default = "n1-standard-2"
  #default = "n1-standard-2"
}

variable "vms_size" {
  description = "VMs sizes (storage) in GB, example 200."
  type    = number
  default = 20
  #default = 200
}

variable "dataproc_workers_size" {
  description = "Datapro worker sizes (storage) in GB, example 50."
  type    = number
  default = 20
  #default = 50
}

variable "dataproc_workers_num_instances" {
  description = "Number of worker instances for dataproc cluster, example 2."
  type    = number
  default = 2
  #default = 3
}

variable "vm2_name" {
  description = "Name of the second virtual machine, example 'asset-vm-2'"
  default = "vm2"
}

variable "host_project_id" {
  description = "Project ID, example 'data-science-activator'"
  default     = ""
}

#EDW
variable "landing_bucket_name" {
  description = "Name of the storage bucket for incoming data, example 'landing-data-bucket'."
  type    = string
  default = "landing-data-bucket-mssb-sandbox"
}

# EDW
variable "staging_bucket_name" {
  description = "Name of the staging storage bucket for Dataproc, example 'staging-data-bucket'."
  type    = string
  default = "staging-data-bucket-mssb-sandbox"
}


variable "region" {
  description = "General location of the project, example 'europe-west2'"
  default     = "europe-west2"
  #default     = "europe-west2"
}

variable "zone" {
  description = "General zone of the project, example 'europe-west2-b'"
  default     = "europe-west2-b"
  #default     = "europe-west2-b"
}


#EDW
variable "standard_subnetwork" {
  description = "VPC subnetwork"
  default     = "main-network-subnet"
}

