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

variable "metaculus_api_key" {
  type = string
}

variable "mail_from" {
  type = string
}

variable "mail_to" {
  type = string
}

provider "aws" {
  region = "us-west-1"
}

resource "aws_key_pair" "aws_magg" {
  key_name   = "aws-magg"
  public_key = file("~/.ssh/aws-magg.pub")
}

resource "aws_security_group" "magg_sg" {
  name = "magg-sg"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "magg_instance" {
  instance_type = "t2.micro"
  key_name      = "aws-magg"
  security_groups = [
    aws_security_group.magg_sg.name,
  ]
  iam_instance_profile = aws_iam_instance_profile.magg_instance_profile.name
  user_data            = <<-EOF
              #!/bin/bash
              echo ${var.metaculus_api_key} > ~/metaculus_api_key
              export MAIL_FROM=${var.mail_from}
              export MAIL_TO=${var.mail_to}
              /opt/magg/env/bin/python /opt/magg/src/magg.py --renew --mail --mail-from=$MAIL_FROM --mail-to=$MAIL_TO >> /var/log/magg.log 2>&1
              EOF
}

resource "aws_iam_instance_profile" "magg_instance_profile" {
  name = "magg_instance_profile"
  role = aws_iam_role.ses_role.name
}

resource "aws_iam_role_policy_attachment" "ses_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
  role       = aws_iam_role.ses_role.name
}

resource "aws_iam_role" "ses_role" {
  name = "ses_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

output "ec2_global_ips" {
  value = ["${aws_instance.magg_instance.public_ip}"]
}
