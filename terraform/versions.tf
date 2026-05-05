provider "aws" {
  region = local.aws_region
}
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "<= 6.34.0"
    }
  }

  backend "s3" {}
}
