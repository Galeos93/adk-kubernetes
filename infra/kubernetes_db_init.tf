# Kubernetes Secret for database initialization

# Mark the password as sensitive
locals {
  db_master_password = sensitive(jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["password"])
}

resource "kubernetes_secret" "db_init" {
  metadata {
    name      = "db-init-secret"
    namespace = "default"
  }

  data = {
    db-host          = aws_db_instance.postgres.address
    db-port          = tostring(aws_db_instance.postgres.port)
    db-name          = aws_db_instance.postgres.db_name
    admin-user       = aws_db_instance.postgres.username
    admin-password   = local.db_master_password
    app-user         = var.db_app_username
    app-password     = var.db_app_password
    "init-script.sql" = <<-EOT
      -- Database initialization script
      -- Creates application user and grants privileges
      
      DO $$
      BEGIN
          -- Create user if doesn't exist
          IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '${var.db_app_username}') THEN
              CREATE USER "${var.db_app_username}" WITH PASSWORD '${var.db_app_password}';
              RAISE NOTICE 'User ${var.db_app_username} created';
          ELSE
              RAISE NOTICE 'User ${var.db_app_username} already exists';
          END IF;
      END
      $$;
      
      -- Grant privileges
      GRANT ALL PRIVILEGES ON DATABASE "${aws_db_instance.postgres.db_name}" TO "${var.db_app_username}";
      GRANT ALL PRIVILEGES ON SCHEMA public TO "${var.db_app_username}";
      ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "${var.db_app_username}";
      ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "${var.db_app_username}";
    EOT
  }

  depends_on = [
    aws_db_instance.postgres,
    data.aws_secretsmanager_secret_version.db_password
  ]
}

# Kubernetes Job for database initialization
resource "kubernetes_job" "db_init" {
  metadata {
    name      = "db-init-job"
    namespace = "default"
  }

  spec {
    backoff_limit = 3

    template {
      metadata {
        labels = {
          app = "db-init"
        }
      }

      spec {
        restart_policy = "Never"

        container {
          name  = "db-init"
          image = "postgres:16"

          env {
            name = "PGHOST"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.db_init.metadata[0].name
                key  = "db-host"
              }
            }
          }

          env {
            name = "PGPORT"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.db_init.metadata[0].name
                key  = "db-port"
              }
            }
          }

          env {
            name = "PGDATABASE"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.db_init.metadata[0].name
                key  = "db-name"
              }
            }
          }

          env {
            name = "PGUSER"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.db_init.metadata[0].name
                key  = "admin-user"
              }
            }
          }

          env {
            name = "PGPASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.db_init.metadata[0].name
                key  = "admin-password"
              }
            }
          }

          command = ["/bin/bash", "-c"]
          args = [
            <<-EOT
              set -e
              echo "Connecting to PostgreSQL at $PGHOST:$PGPORT..."
              echo "Running database initialization script..."
              PGSSLMODE=require psql -f /scripts/init-script.sql
              echo "✅ Database initialization complete!"
            EOT
          ]

          volume_mount {
            name       = "init-scripts"
            mount_path = "/scripts"
            read_only  = true
          }
        }

        volume {
          name = "init-scripts"
          secret {
            secret_name = kubernetes_secret.db_init.metadata[0].name
            items {
              key  = "init-script.sql"
              path = "init-script.sql"
            }
          }
        }
      }
    }
  }

  wait_for_completion = true

  depends_on = [
    kubernetes_secret.db_init,
    aws_db_instance.postgres
  ]
}
