terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = ">= 6.15.0"
        }
        kubernetes = {
            source  = "hashicorp/kubernetes"
            version = ">= 2.20"
        }
        helm = {
            source  = "hashicorp/helm"
            version = ">= 2.9"
        }
    }

    required_version = ">= 1.2"
}