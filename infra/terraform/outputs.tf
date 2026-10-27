output "vpc_id" {
  description = "VPC ID of the ArthMitra isolated network"
  value       = aws_vpc.arthmitra_vpc.id
}

output "public_subnets" {
  description = "Public subnets for load balancers and ingress gateways"
  value       = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

output "private_db_subnets" {
  description = "Private isolated subnets for database and cache instances"
  value       = [aws_subnet.private_db_1.id, aws_subnet.private_db_2.id]
}

output "db_endpoint" {
  description = "Connection endpoint hostname and port for PostgreSQL 16 + PostGIS instance"
  value       = aws_db_instance.postgres_postgis.endpoint
}

output "db_address" {
  description = "DNS address of the RDS PostgreSQL instance"
  value       = aws_db_instance.postgres_postgis.address
}

output "db_port" {
  description = "Listening port of the RDS PostgreSQL instance"
  value       = aws_db_instance.postgres_postgis.port
}

output "db_name" {
  description = "Primary database name"
  value       = aws_db_instance.postgres_postgis.db_name
}

output "redis_endpoint" {
  description = "Redis cluster primary endpoint address"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "redis_port" {
  description = "Redis cluster primary port"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].port
}

output "s3_bucket_name" {
  description = "S3 bucket ID for encrypted consent audio and bank DPR storage"
  value       = aws_s3_bucket.object_storage.id
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.object_storage.arn
}

output "ecs_cluster_name" {
  description = "ECS cluster name hosting FastAPI backend and worker tasks"
  value       = aws_ecs_cluster.main_cluster.name
}

output "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  value       = aws_ecs_cluster.main_cluster.arn
}
