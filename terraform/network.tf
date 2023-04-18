############################################# resources #########################################

resource "aws_vpc" "vpc" {
  cidr_block = var.aws_vpc_cidr_block
  enable_dns_hostnames = true
}

resource "aws_key_pair" "my_key_pair" {
  key_name   = var.key_name
  public_key = file("/home/i573830/.ssh/authorized_keys") 
}

resource "aws_instance" "ec2" {
  ami                         = var.ami
  associate_public_ip_address = true
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.subnet.id
  vpc_security_group_ids      = [aws_security_group.ec2-sg.id]
  key_name                    = aws_key_pair.my_key_pair.key_name
}

resource "aws_subnet" "subnet" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = var.subnet_cidr_block
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc.id
}

resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = var.rt_cidr_block
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "rta-subnets" {
  subnet_id      = aws_subnet.subnet.id
  route_table_id = aws_route_table.rt.id
}

resource "aws_security_group" "ec2-sg" {
  vpc_id = aws_vpc.vpc.id

  dynamic "ingress" {
    for_each = var.allowed_ports
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
