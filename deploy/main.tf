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

resource "aws_instance" "magg_instance" {
  ami           = "FILL_THIS_IN"
  instance_type = "t2.micro"
  key_name      = "aws-magg"
  security_groups = [
    aws_security_group.magg_sg.name,
  ]
  iam_instance_profile = aws_iam_instance_profile.magg_instance_profile.name
  user_data            = <<-EOF
              #!/bin/bash
              # run every Wednesday at 15:30
              echo "30 15 * * 3 /opt/magg/env/bin/python /opt/magg/src/magg.py --renew --mail  --config=/var/magg/config.json >> /var/magg/magg.log 2>&1" | crontab -
              EOF
}

resource "null_resource" "magg_data" {
  connection {
    host        = aws_instance.magg_instance.public_ip
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("~/.ssh/aws-magg.pem")
  }
  provisioner "file" {
    source      = "config.json"
    destination = "/tmp/config.json"
  }
  provisioner "remote-exec" {
    inline = [
      "cp /tmp/config.json /var/magg/config.json",
      "/opt/magg/env/bin/python /opt/magg/src/magg.py --renew --mail --config=/var/magg/config.json >> /var/magg/magg.log 2>&1",
    ]
  }
}

output "ec2_global_ips" {
  value = ["${aws_instance.magg_instance.public_ip}"]
}
