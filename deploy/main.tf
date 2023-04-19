terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "us-east-1"
}

resource "aws_key_pair" "aws_magg" {
  key_name   = "aws-magg"
  public_key = file("~/.ssh/aws-magg.pub")
}

resource "aws_instance" "magg_instance" {
  ami           = "ami-0638741e0c9aabde6" # ubuntu 22.10
  instance_type = "t2.micro"
  key_name      = "aws-magg"

  connection {
    type        = "ssh"
    user        = "ec2-user"
    private_key = file("~/.ssh/aws-magg.pem")
    host        = self.public_ip
  }

  provisioner "file" {
    source      = "magg-1.0.tar.gz"
    destination = "/opt/magg-1.0.tar.gz"
  }

  provisioner "remote-exec" {
    inline = [
      "pip3 install /opt/magg-1.0.tar.gz",
    ]
  }
}
