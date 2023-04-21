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

# Configure the AWS Provider
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
  user_data = file("deploy.sh")

  connection {
    host        = self.public_ip
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("~/.ssh/aws-magg.pem")
  }

  provisioner "file" {
    source      = "magg-1.0.0.tar.gz"
    destination = "/tmp/magg-1.0.0.tar.gz"
  }

  provisioner "local-exec" {
    command = "echo The server IP address is ${self.public_ip}"
  }

}
