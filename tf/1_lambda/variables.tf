variable "aws_region" {
  description = "AWS region to deploy resources in"
  type        = string
  default = "us-east-1"
}

variable "project" {
  description = "Project name, used for tagging and naming resources"
  type        = string
  default = "project-sba"
}

variable "environment" {
  description = "Deployment environment (e.g., live, nonlive, dev)"
  type        = string
  default = "dev"
}

variable "python_version" {
  type    = string
  default = "3.14"
}