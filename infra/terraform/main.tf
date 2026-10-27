terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Strictly pinned to India AWS Region (Mumbai) per DPDP Act Data Localization
provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "ArthMitra"
      Environment = var.environment
      ManagedBy   = "Terraform"
      DataSovereignty = "India-ap-south-1"
    }
  }
}

# --- VPC & Networking ---
resource "aws_vpc" "arthmitra_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "arthmitra-${var.environment}-vpc"
  }
}

resource "aws_subnet" "public_1" {
  vpc_id            = aws_vpc.arthmitra_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "arthmitra-public-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id            = aws_vpc.arthmitra_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"
  map_public_ip_on_launch = true

  tags = {
    Name = "arthmitra-public-2"
  }
}

resource "aws_subnet" "private_db_1" {
  vpc_id            = aws_vpc.arthmitra_vpc.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "arthmitra-private-db-1"
  }
}

resource "aws_subnet" "private_db_2" {
  vpc_id            = aws_vpc.arthmitra_vpc.id
  cidr_block        = "10.0.11.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "arthmitra-private-db-2"
  }
}

# --- Managed Database (PostgreSQL 16 + PostGIS) ---
resource "aws_db_subnet_group" "db_subnets" {
  name       = "arthmitra-${var.environment}-db-subnets"
  subnet_ids = [aws_subnet.private_db_1.id, aws_subnet.private_db_2.id]
}

resource "aws_db_instance" "postgres_postgis" {
  identifier        = "arthmitra-${var.environment}-db"
  allocated_storage = 50
  max_allocated_storage = 200
  storage_type      = "gp3"
  engine            = "postgres"
  engine_version    = "16.2"
  instance_class    = "db.t4g.medium"
  db_name           = "arthmitra"
  username          = var.db_username
  password          = var.db_password
  db_subnet_group_name = aws_db_subnet_group.db_subnets.name

  storage_encrypted   = true
  deletion_protection = var.environment == "production" ? true : false
  skip_final_snapshot = var.environment == "production" ? false : true

  backup_retention_period = 30
  backup_window           = "19:00-20:00" # 00:30-01:30 IST

  tags = {
    Name = "arthmitra-postgis-db"
  }
}

# --- Redis Cache & Queue Cluster ---
resource "aws_elasticache_subnet_group" "redis_subnets" {
  name       = "arthmitra-${var.environment}-redis-subnets"
  subnet_ids = [aws_subnet.private_db_1.id, aws_subnet.private_db_2.id]
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "arthmitra-${var.environment}-redis"
  engine               = "redis"
  node_type            = "cache.t4g.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis_subnets.name
}

# --- S3 Object Storage (Consent Audio & Bank DPRs) ---
resource "aws_s3_bucket" "object_storage" {
  bucket = "arthmitra-${var.environment}-assets-in"

  tags = {
    Classification = "EncryptedStorage"
    Purpose = "ConsentAudioAndBankDPR"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "s3_encrypt" {
  bucket = aws_s3_bucket.object_storage.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = aws_s3_bucket.object_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- ECS Fargate Task Definition & Service ---
resource "aws_ecs_cluster" "main_cluster" {
  name = "arthmitra-${var.environment}-cluster"
}
