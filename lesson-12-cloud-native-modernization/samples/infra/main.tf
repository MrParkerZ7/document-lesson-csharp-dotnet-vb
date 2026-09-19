# MotorQuote on AWS: an HTTP API in front of a .NET 10 Lambda, and the same API as a container
# on ECS Fargate. A SKETCH read into lesson 12 and checked with `terraform validate`; it is never
# applied from this repository. The VPC, load-balancer listener, ECS cluster and service, ECR
# repository, IAM roles and the state backend are outside its scope and arrive as variables.

terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

variable "lambda_zip" { type = string }
variable "lambda_role_arn" { type = string }
variable "image" { type = string }
variable "task_execution_role_arn" { type = string }
variable "vpc_id" { type = string }

locals {
  asm = "L12.QuoteLambda"
}

#region lambda
resource "aws_lambda_function" "create_quote" {
  function_name    = "motorquote-create-quote"
  role             = var.lambda_role_arn
  runtime          = "dotnet10"
  architectures    = ["arm64"]
  memory_size      = 1024
  timeout          = 10
  filename         = var.lambda_zip
  source_code_hash = filebase64sha256(var.lambda_zip)
  handler          = "${local.asm}::${local.asm}.QuoteFunctions_CreateQuote_Generated::CreateQuote"

  publish = true # SnapStart snapshots published versions, never $LATEST
  snap_start {
    apply_on = "PublishedVersions"
  }

  logging_config {
    log_format = "JSON" # message-template arguments become JSON fields
  }
}

resource "aws_lambda_alias" "live" {
  name             = "live"
  function_name    = aws_lambda_function.create_quote.function_name
  function_version = aws_lambda_function.create_quote.version
}
#endregion

#region api
resource "aws_apigatewayv2_api" "http" {
  name          = "motorquote"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "create_quote" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_alias.live.invoke_arn
  payload_format_version = "2.0" # APIGatewayHttpApiV2ProxyRequest in .NET
}

resource "aws_apigatewayv2_route" "create_quote" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "POST /quotes"
  target    = "integrations/${aws_apigatewayv2_integration.create_quote.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_quote.function_name
  qualifier     = aws_lambda_alias.live.name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}
#endregion

#region ecs
resource "aws_ecs_task_definition" "api" {
  family                   = "motorquote-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = var.task_execution_role_arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }

  container_definitions = jsonencode([{
    name         = "quote-api"
    image        = var.image
    essential    = true
    portMappings = [{ containerPort = 8080 }] # .NET 8+ images listen on 8080
    stopTimeout  = 30                         # SIGTERM, wait, then SIGKILL
    # no container healthCheck: a chiseled image has no shell and no curl
  }])
}

resource "aws_lb_target_group" "api" {
  name        = "motorquote-api"
  port        = 8080
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    path = "/health/ready" # the load balancer probes readiness from outside
  }
}
#endregion
