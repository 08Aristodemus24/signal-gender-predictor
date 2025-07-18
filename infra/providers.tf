# Configure the Azure provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0.2"
    }
  }

  required_version = ">= 1.1.0"
}

# The provider block configures the specified provider, 
# in this case azurerm. A provider is a plugin that 
# Terraform uses to create and manage your resources. 
# You can define multiple provider blocks in a Terraform
# configuration to manage resources from different providers.
provider "azurerm" {
  features {

  }
}