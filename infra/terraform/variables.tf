variable "aws_region" {
  type        = string
  default     = "ap-south-1"
  description = "AWS India region (Mumbai) for statutory data localization under DPDP Act"
}

variable "environment" {
  type        = string
  default     = "staging"
  description = "Environment tier: staging | production"
}

variable "db_username" {
  type        = string
  default     = "arthmitra_app"
  description = "Database administrator username"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "Database master password"
}
