provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "Prowess" {
  ami           = "ami-035be7bafff33b6b6"
  instance_type = "t3.nano"

  tags = {
    Name = "Prowess Consumer"
  }
}