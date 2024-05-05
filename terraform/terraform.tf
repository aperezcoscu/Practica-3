provider "aws" {
  region = "eu-west-3"
}

# ECR Repositories
resource "aws_ecr_repository" "scrapping_meff_s3_ecr" {
  name = "scrapping_meff_s3_ecr"
}

resource "aws_ecr_repository" "volatility_ecr" {
  name = "volatility_ecr"
}

resource "aws_ecr_repository" "app_dash_ecr" {
  name = "app_dash_ecr"
}

# S3 Bucket
resource "aws_s3_bucket" "data_bucket" {
  bucket = "miax-12-scrap-meff"
}

# DynamoDB Table
resource "aws_dynamodb_table" "volatiliy_table" {
  name           = "volatiliy_table"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "ID"

  attribute {
    name = "ID"
    type = "S"
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_iam_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect = "Allow"
        Sid    = ""
      },
    ]
  })
}

# Lambda Functions
resource "aws_lambda_function" "scrapp_meff_s3" {
  function_name = "scrapp_meff_s3"
  handler       = "index.handler" # Adjust based on your actual handler file and function
  role          = aws_iam_role.lambda_iam_role.arn
  runtime       = "python3.8"
  memory_size   = 400
  timeout       = 120

  code = {
    s3_bucket = "${aws_s3_bucket.data_bucket.id}"
    s3_key    = "scrapp_meff_s3.zip"
  }
}

resource "aws_lambda_function" "volatility_ddb" {
  function_name = "volatility_ddb"
  handler       = "index.handler" # Adjust based on your actual handler file and function
  role          = aws_iam_role.lambda_iam_role.arn
  runtime       = "python3.8"
  memory_size   = 400
  timeout       = 120

  code = {
    s3_bucket = "${aws_s3_bucket.data_bucket.id}"
    s3_key    = "volatility_ddb.zip"
  }
}

# Security Group
resource "aws_security_group" "sg_allow_ssh_http" {
  name = "allow_ssh_http_miax"

  ingress {
    from_port   = 22
    protocol    = "tcp"
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow SSH from anywhere"
  }

  ingress {
    from_port   = 8050
    protocol    = "tcp"
    to_port     = 8050
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP traffic on port 8050 from anywhere"
  }

  egress {
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
}

# EC2 Instance for the Web Application
resource "aws_instance" "web_app" {
  ami           = "ami-0111c5910da90c2a7"
  instance_type = "t2.micro"
  key_name      = "keypair"
  vpc_security_group_ids = [aws_security_group.sg_allow_ssh_http.id]

  tags = {
    Name = "Volatility Dash App"
  }
}

# Outputs for easy reference
output "ECR_Repository_URLs" {
  value = {
    "Scraping"  = aws_ecr_repository.scrapping_meff_s3_ecr.repository_url
    "Volatility" = aws_ecr_repository.volatility_ecr.repository_url
    "App"       = aws_ecr_repository.app_dash_ecr.repository_url
  }
}

output "Lambda_Function_ARNs" {
  value = {
    "Scraper"   = aws_lambda_function.scrapp_meff_s3.arn
    "Volatility" = aws_lambda_function.volatility_ddb.arn
  }
}

output "EC2_Instance_ID" {
  value = aws_instance.web_app.id
}
