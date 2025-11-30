output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.fastapi_agent.repository_url
}

output "ecr_repository_arn" {
  description = "ARN of the ECR repository"
  value       = aws_ecr_repository.fastapi_agent.arn
}

output "ecr_repository_name" {
  description = "Name of the ECR repository"
  value       = aws_ecr_repository.fastapi_agent.name
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "domain_name" {
  description = "The domain name configured for the API"
  value       = var.domain_name != "" ? var.domain_name : "not configured"
}

output "certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = var.domain_name != "" ? aws_acm_certificate.api[0].arn : "not configured"
}

output "route53_zone_id" {
  description = "ID of the Route53 hosted zone"
  value       = var.domain_name != "" ? aws_route53_zone.main[0].zone_id : "not configured"
}

output "route53_name_servers" {
  description = "Name servers for the Route53 hosted zone (update these in your domain registrar)"
  value       = var.domain_name != "" ? aws_route53_zone.main[0].name_servers : []
}

# Database outputs
output "db_endpoint" {
  description = "PostgreSQL database endpoint (host:port)"
  value       = aws_db_instance.postgres.endpoint
}

output "db_host" {
  description = "PostgreSQL database hostname"
  value       = aws_db_instance.postgres.address
}

output "db_port" {
  description = "PostgreSQL database port"
  value       = aws_db_instance.postgres.port
}

output "db_name" {
  description = "PostgreSQL database name"
  value       = aws_db_instance.postgres.db_name
}

output "db_username" {
  description = "PostgreSQL master username"
  value       = aws_db_instance.postgres.username
  sensitive   = true
}

output "db_master_user_secret_arn" {
  description = "ARN of the Secrets Manager secret containing the master user password"
  value       = aws_db_instance.postgres.master_user_secret[0].secret_arn
}
