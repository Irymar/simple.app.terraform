variable "hcloud_token" {
  type      = string
  sensitive = true
}

variable "ssh_key_name" {
  type = string
}

variable "server_name" {
  type    = string
  default = "tf-test-vm"
}

variable "server_type" {
  type    = string
  default = "cax11" # часто найдешевший (ARM)
}

variable "location" {
  type    = string
  default = "hel1"
}

variable "image" {
  type    = string
  default = "ubuntu-22.04"
}
