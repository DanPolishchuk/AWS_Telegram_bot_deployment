variable "access_key" {
  type = string
  default = ""
  description = "AWS Access Key"
}

variable "secret_key" {
  type = string
  default = ""
  description = "AWS Secret Key"
}

variable "ami" {
  type = string
  default = "ami-0ec7f9846da6b0f61"
  description = "AWS AMI for EC2 instance"
}

variable "instance_type" {
  type = string
  default = "t2.micro" 
  description = "Size of EC2 instance"
}

variable "region" {
  type = string
  default = "eu-central-1"
  description = "AWS region"
}

variable "rt_cidr_block" {
  type        = string
  description = "Route Table CIDR block"
  default     = "0.0.0.0/0"
}

variable "aws_vpc_cidr_block" {
  type        = string
  description = "VPC CIDR block"
  default     = "10.0.0.0/16"
}

variable "allowed_ports" {
    type = list
    default = ["80", "443", "22"]
    description = "Allowed ports for inbound traffic"
}

variable "subnet_cidr_block" {
  type = string
  default = "10.0.0.0/24"
  description = "Subnet CIDR block"
}

variable "key_name" {
  type = string
  default = "my-key-pair"
  description = "Name for key pair"
}
