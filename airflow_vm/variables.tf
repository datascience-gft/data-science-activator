########################
#   Project variables  #
########################

variable "host_project_id" {
  description = "Project ID, example 'data-science-activator'"
  default     = "ford-battery-dev"
}

variable "standard_subnetwork" {
  description = "VPC subnetwork such as main-network-subnet"
  default     = "projects/ford-battery-dev/regions/europe-west2/subnetworks/main-network-subnet"
}

variable "standard_network" {
  description = "VPC subnetwork such as main-network-subnet"
  default     = "projects/ford-battery-dev/global/networks/shared-network"
}

variable "region" {
	type        = string
	description = "General location of the project"
	default     = "europe-west2"
}

variable "zone" {
  type        = string
  description = "General zone of the project"
  default     = "europe-west2-a"
  
}

###################################
#         Storage buckets         #
###################################

variable "evidance_bucket_name" {
  description = "Name of the storage bucket for Airflow data, example 'landing-data-bucket'."
  type        = string
  default     = "assembly-evidance"
}

########################
#   Virtual Machines   #
########################


variable "ai_notebook_name" {
  description = "Name of the notebooks instance"
  default     = "notebooks-instance"
}


variable "machine_type" {
  description = "Machine type of the virtual machines, example 'n1-standard-2'"
  type        = string
  default     = "n1-standard-2"
}

variable "vms_size" {
  description = "VMs sizes (storage) in GB, example 200."
  type        = number
  default     = 100
}
