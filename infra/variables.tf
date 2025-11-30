variable "eks_cluster_availability_zones" {
  description = "List of availability zones to deploy resources in"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "domain_name" {
  description = "Domain name for the API (e.g., api.example.com)"
  type        = string
  default     = "agent-playground.online"  # Set this to your domain or leave empty to skip Route53/ACM setup
}

# Database configuration
variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "fastapi_agent_db"
}

variable "db_username" {
  description = "Master username for the PostgreSQL database"
  type        = string
  default     = "postgres"
  sensitive   = true
}

variable "db_instance_class" {
  description = "Instance class for the RDS database"
  type        = string
  default     = "db.t4g.micro"  # Free tier eligible
}

variable "db_allocated_storage" {
  description = "Allocated storage for the RDS database in GB"
  type        = number
  default     = 20
}

variable "db_app_username" {
  description = "Application username for the PostgreSQL database"
  type        = string
  default     = "fastapi_app"
  sensitive   = true
}

variable "db_app_password" {
  description = "Application user password for the PostgreSQL database"
  type        = string
  sensitive   = true
}
