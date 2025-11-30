# ECR Repository for FastAPI Agent
resource "aws_ecr_repository" "fastapi_agent" {
  name                 = "fastapi-agent"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name        = "fastapi-agent"
    Environment = "development"
    Project     = "adk-kubernetes"
  }
}

# ECR Lifecycle Policy to manage image retention
resource "aws_ecr_lifecycle_policy" "fastapi_agent_lifecycle" {
  repository = aws_ecr_repository.fastapi_agent.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Delete untagged images older than 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# Data source to get current AWS account ID
data "aws_caller_identity" "current" {}
