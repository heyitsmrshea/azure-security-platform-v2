# Azure Security Platform V2 - Terraform Configuration

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
  
  backend "azurerm" {
    # Configure in backend.tfvars
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = false
    }
  }
}

# Variables
variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "location" {
  type        = string
  description = "Azure region"
  default     = "eastus"
}

variable "azure_ad_tenant_id" {
  type        = string
  description = "Azure AD tenant ID for authentication"
}

variable "azure_ad_client_id" {
  type        = string
  description = "Azure AD client ID for the application"
}

# Random suffix for unique names
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

locals {
  base_name     = "secplatform${var.environment}"
  unique_suffix = random_string.suffix.result
  tags = {
    environment = var.environment
    application = "azure-security-platform"
    managedBy   = "terraform"
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "rg-security-platform-${var.environment}"
  location = var.location
  tags     = local.tags
}

# CosmosDB Account
resource "azurerm_cosmosdb_account" "main" {
  name                = "${local.base_name}-cosmos-${local.unique_suffix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  
  capabilities {
    name = "EnableServerless"
  }
  
  consistency_policy {
    consistency_level = "Session"
  }
  
  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }
  
  tags = local.tags
}

# CosmosDB Database
resource "azurerm_cosmosdb_sql_database" "main" {
  name                = "security_platform"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
}

# CosmosDB Containers
locals {
  containers = {
    tenants             = { partition_key = "/id", ttl = -1 }
    security_scores     = { partition_key = "/tenantId", ttl = 7776000 }
    findings            = { partition_key = "/tenantId", ttl = 31536000 }
    alerts              = { partition_key = "/tenantId", ttl = 7776000 }
    backup_status       = { partition_key = "/tenantId", ttl = 7776000 }
    audit_logs          = { partition_key = "/tenantId", ttl = 7776000 }
    dashboard_snapshots = { partition_key = "/tenantId", ttl = 31536000 }
  }
}

resource "azurerm_cosmosdb_sql_container" "containers" {
  for_each = local.containers
  
  name                = each.key
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
  database_name       = azurerm_cosmosdb_sql_database.main.name
  partition_key_path  = each.value.partition_key
  default_ttl         = each.value.ttl
}

# Redis Cache
resource "azurerm_redis_cache" "main" {
  name                = "${local.base_name}-redis-${local.unique_suffix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = 0
  family              = "C"
  sku_name            = "Basic"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"
  
  redis_configuration {
    maxmemory_policy = "volatile-lru"
  }
  
  tags = local.tags
}

# Key Vault
resource "azurerm_key_vault" "main" {
  name                       = "${local.base_name}-kv-${local.unique_suffix}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = var.azure_ad_tenant_id
  sku_name                   = "standard"
  enable_rbac_authorization  = true
  soft_delete_retention_days = 90
  purge_protection_enabled   = true
  
  tags = local.tags
}

# App Service Plan
resource "azurerm_service_plan" "main" {
  name                = "${local.base_name}-plan-${local.unique_suffix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "B1"
  
  tags = local.tags
}

# App Service (Backend API)
resource "azurerm_linux_web_app" "api" {
  name                = "${local.base_name}-api-${local.unique_suffix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id
  https_only          = true
  
  site_config {
    application_stack {
      python_version = "3.11"
    }
    ftps_state        = "Disabled"
    minimum_tls_version = "1.2"
  }
  
  app_settings = {
    COSMOS_ENDPOINT     = azurerm_cosmosdb_account.main.endpoint
    REDIS_URL           = "rediss://${azurerm_redis_cache.main.hostname}:6380"
    KEY_VAULT_URL       = azurerm_key_vault.main.vault_uri
    AZURE_AD_TENANT_ID  = var.azure_ad_tenant_id
    AZURE_AD_CLIENT_ID  = var.azure_ad_client_id
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  tags = local.tags
}

# Outputs
output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "cosmos_endpoint" {
  value = azurerm_cosmosdb_account.main.endpoint
}

output "redis_hostname" {
  value = azurerm_redis_cache.main.hostname
}

output "key_vault_uri" {
  value = azurerm_key_vault.main.vault_uri
}

output "api_url" {
  value = "https://${azurerm_linux_web_app.api.default_hostname}"
}
