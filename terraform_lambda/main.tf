### VARIABLES
variable "bucket_name" {
    type      = string
    default   = "somebucketname"
}

variable "sg_name" {
    type      = string
    default   = "rds_access_group" 
}

variable "db_instance_name" {
    type      = string
    default   = "somedbinstancename"
}

### PROVIDERS
provider "aws" {
    alias  = "north"
    region = "eu-north-1"
}

provider "aws" {
    alias  = "uswest"
    region = "us-west-1"
}

### RESOURCES

## ROLE
resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "role-policy-attachment" {
  for_each = toset([
    "arn:aws:iam::aws:policy/AdministratorAccess", 
    # "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    # "arn:aws:iam::aws:policy/CloudWatchFullAccess"
  ])

  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = each.value
}

## S3
resource "aws_s3_bucket" "bucket" {
    provider = aws.uswest
    bucket   = var.bucket_name
}

resource "aws_s3_bucket_object" "deployment_lambda_package" {
    bucket = aws_s3_bucket.bucket.id
    acl    = "private"
    key    = "deployment-lambda-package.zip"
    source = "my-deployment-package.zip"
    etag   = filemd5("my-deployment-package.zip")
}

resource "aws_s3_bucket_object" "folder1" {
    bucket = aws_s3_bucket.bucket.id
    acl    = "private"
    key    = "folder1/"
    source = "/dev/null"
}

resource "aws_s3_bucket_object" "folder2" {
    bucket = aws_s3_bucket.bucket.id
    acl    = "private"
    key    = "folder2/"
    source = "/dev/null"
}

## Lambda Function
resource "aws_lambda_function" "terraform_lambda" {
    provider      = aws.uswest
    s3_bucket     = aws_s3_bucket.bucket.id
    s3_key        = aws_s3_bucket_object.deployment_lambda_package.id
    function_name = "terraform-lambda-function"
    role          = aws_iam_role.iam_for_lambda.arn
    handler       = "lambda_function.lambda_handler"
    memory_size   = 256
    timeout       = 15
    runtime       = "python3.8"
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.terraform_lambda.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bucket.arn
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.terraform_lambda.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "folder1/"
    filter_suffix       = ".csv"
  }

  depends_on = [aws_lambda_permission.allow_bucket]
}

## CloudWatch event rule
resource "aws_cloudwatch_event_rule" "workdays_18_pm" {
    name                = "workdays-18-pm"
    description         = "Fires every workday at 18 pm"
    schedule_expression = "cron(0 18 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_target" "start_lambda_workdays" {
    rule            = aws_cloudwatch_event_rule.workdays_18_pm.name
    target_id       = "terraform-lambda-function"
    arn             = aws_lambda_function.terraform_lambda.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_lambda" {
    statement_id    = "AllowExecutionFromCloudWatch"
    action          = "lambda:InvokeFunction"
    function_name   = aws_lambda_function.terraform_lambda.function_name
    principal       = "events.amazonaws.com"
    source_arn      = aws_cloudwatch_event_rule.workdays_18_pm.arn
}

## Security group
resource "aws_security_group" "rds_access_group" {
    name_prefix = var.sg_name
    description = "Allows access to RDS"
    lifecycle {
        create_before_destroy = true
    }

    ingress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        ipv6_cidr_blocks = ["::/0"]
    }
}

## RDS
resource "aws_db_instance" "postgresdb" {
    provider             = aws.uswest
    identifier           = var.db_instance_name
    allocated_storage    = 20
    storage_type         = "gp2"
    engine               = "postgres"
    engine_version       = "12.4"
    instance_class       = "db.t2.micro"
    name                 = "mydb"
    username             = "admin1"
    password             = "foo123bar"
    publicly_accessible  = true
    skip_final_snapshot  = true
    apply_immediately    = true
    backup_retention_period = 0
    vpc_security_group_ids = [ aws_security_group.rds_access_group.id ]
}