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

resource "aws_instance" "magg_instance" {
  ami           = "ami-014d05e6b24240371" # us-west-1 ubuntu 22.04
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

output "aws_magg_ip" {
  value = aws_instance.magg_instance.*.public_ip
}
