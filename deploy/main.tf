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
  ami           = "ami-014d05e6b24240371" # us-west-1 ubuntu 22.04
  instance_type = "t2.micro"
  key_name      = "aws-magg"
  security_groups = [
    aws_security_group.magg_sg.name,
  ]
  iam_instance_profile = aws_iam_instance_profile.magg_instance_profile.name
  user_data            = <<-EOF
              #!/bin/bash
              echo ${var.metaculus_api_key} > /metaculus_api_key
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


resource "null_resource" "magg_data" {
  connection {
    host        = aws_instance.magg_instance.public_ip
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("~/.ssh/aws-magg.pem")
  }

  provisioner "file" {
    source      = "magg-1.0.0.tar.gz"
    destination = "/tmp/magg-1.0.0.tar.gz"
  }

  provisioner "file" {
    source      = "config.json"
    destination = "/tmp/config.json"
  }

  provisioner "file" {
    source      = "deploy.sh"
    destination = "/tmp/deploy.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/deploy.sh",
      "sudo /tmp/deploy.sh",
    ]
  }

  provisioner "local-exec" {
    command = "echo The server IP address is ${aws_instance.magg_instance.public_ip}"
  }
}
