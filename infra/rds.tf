# RDS PostgreSQL Database

# Data source to fetch master user password from Secrets Manager
data "aws_secretsmanager_secret" "db_password" {
  arn = aws_db_instance.postgres.master_user_secret[0].secret_arn
}

data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = data.aws_secretsmanager_secret.db_password.id
}

# DB Subnet Group - Uses private subnets from VPC
resource "aws_db_subnet_group" "postgres" {
  name       = "eks-postgres-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name        = "eks-postgres-subnet-group"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name_prefix = "eks-rds-postgres-"
  description = "Security group for RDS PostgreSQL instance"
  vpc_id      = module.vpc.vpc_id

  # Allow PostgreSQL traffic from EKS nodes
  ingress {
    description     = "PostgreSQL from EKS nodes"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  # Allow PostgreSQL traffic from EKS cluster
  ingress {
    description     = "PostgreSQL from EKS cluster"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.cluster_security_group_id]
  }

  # Allow PostgreSQL from private subnets (for pods)
  ingress {
    description = "PostgreSQL from private subnets"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = module.vpc.private_subnets_cidr_blocks
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "eks-rds-postgres"
    Environment = "production"
    ManagedBy   = "terraform"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "postgres" {
  identifier = "eks-postgres"

  # Engine configuration
  engine               = "postgres"
  engine_version       = "16.11"
  instance_class       = var.db_instance_class
  allocated_storage    = var.db_allocated_storage
  storage_type         = "gp3"
  storage_encrypted    = true

  # Database configuration
  db_name  = var.db_name
  username = var.db_username
  manage_master_user_password = true  # AWS auto-generates and stores in Secrets Manager
  port     = 5432

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.postgres.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  multi_az               = false  # Set to true for production high availability

  # Backup configuration
  backup_retention_period = 7
  backup_window          = "03:00-04:00"  # UTC
  maintenance_window     = "mon:04:00-mon:05:00"  # UTC

  # Deletion protection
  deletion_protection       = false  # Set to true for production
  skip_final_snapshot      = true   # Set to false for production
  final_snapshot_identifier = "eks-postgres-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Performance insights
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  performance_insights_enabled    = true
  performance_insights_retention_period = 7

  # Auto minor version updates
  auto_minor_version_upgrade = true

  tags = {
    Name        = "eks-postgres"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
