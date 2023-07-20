terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    bucket = "magg-tfstate"
    key    = "terraform.tfstate"
    region = "us-west-1"
  }
}

provider "aws" {
  region = "us-west-1"
}

resource "aws_iam_role" "magg_role" {
  name = "magg_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ses_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
  role       = aws_iam_role.magg_role.name
}

resource "aws_iam_role_policy_attachment" "s3_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  role       = aws_iam_role.magg_role.name
}

resource "aws_iam_role_policy_attachment" "ssm_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
  role       = aws_iam_role.magg_role.name
}

resource "aws_cloudwatch_event_rule" "weekly_event" {
  name                = "magg_weekly_event"
  schedule_expression = "cron(0 15 ? * WED *)" # Every Wednesday at 3 PM
}

resource "aws_ssm_parameter" "config_json" {
  name  = "config.json"
  type  = "SecureString"
  value = file("config.s3.json") # this file should exist in the same directory as main.tf
}

resource "aws_lambda_function" "magg_task" {
  function_name = "MaggTask"
  handler       = "magg.lambda_handler"
  runtime       = "python3.10"

  filename         = "magg.zip"
  source_code_hash = filebase64sha256("magg.zip")

  role = aws_iam_role.magg_role.arn

  timeout = 300
}

resource "aws_cloudwatch_event_target" "execute_weekly_lambda" {
  rule      = aws_cloudwatch_event_rule.weekly_event.name
  target_id = "MaggTask"
  arn       = aws_lambda_function.magg_task.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.magg_task.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_event.arn
}

