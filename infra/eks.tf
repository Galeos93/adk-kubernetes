module "eks" {
    source  = "terraform-aws-modules/eks/aws"
    version = "21.8.0"

    name = "eks-cluster"

    vpc_id     = module.vpc.vpc_id
    subnet_ids = module.vpc.private_subnets

    endpoint_public_access = true

    enable_cluster_creator_admin_permissions = true

  # Enable IAM Roles for Service Accounts
    enable_irsa = true

    compute_config = {
        enabled    = true
        node_pools = ["general-purpose"]
    }

}