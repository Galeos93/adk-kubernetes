# Kubernetes Ingress for FastAPI Agent
resource "kubernetes_ingress_v1" "agent_ingress" {
  count = var.domain_name != "" ? 1 : 0

  metadata {
    name      = "agent-ingress"
    namespace = "default"
    labels = {
      app = "agent-service"
    }
    annotations = {
      # AWS Load Balancer Controller annotations for ALB
      "alb.ingress.kubernetes.io/scheme"      = "internet-facing"
      "alb.ingress.kubernetes.io/target-type" = "ip"
      "alb.ingress.kubernetes.io/listen-ports" = jsonencode([
        { HTTP = 80 },
        { HTTPS = 443 }
      ])
      # Redirect HTTP to HTTPS
      "alb.ingress.kubernetes.io/ssl-redirect" = "443"
      # ACM certificate for HTTPS
      "alb.ingress.kubernetes.io/certificate-arn" = aws_acm_certificate_validation.api[0].certificate_arn
      # Health check configuration
      "alb.ingress.kubernetes.io/healthcheck-path"              = "/health"
      "alb.ingress.kubernetes.io/healthcheck-interval-seconds"  = "15"
      "alb.ingress.kubernetes.io/healthcheck-timeout-seconds"   = "5"
      "alb.ingress.kubernetes.io/healthy-threshold-count"       = "2"
      "alb.ingress.kubernetes.io/unhealthy-threshold-count"     = "2"
      # AWS tags for the ALB
      "alb.ingress.kubernetes.io/tags" = "Environment=production,Application=fastapi-agent,ManagedBy=terraform"
    }
  }

  spec {
    ingress_class_name = "alb"

    rule {
      host = var.domain_name
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = "agent-service"
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }

  depends_on = [
    aws_acm_certificate_validation.api
  ]
}
