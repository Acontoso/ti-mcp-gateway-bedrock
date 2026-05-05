data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "aws_bedrockagentcore_gateway" "recordedfurture_gateway" {
  name            = var.gateway_name
  description     = var.gateway_description
  role_arn        = aws_iam_role.gateway_role.arn
  authorizer_type = var.authorization_type
  protocol_type   = "MCP"
  region          = data.aws_region.current.name
  authorizer_configuration {
    custom_jwt_authorizer {
      discovery_url    = "https://login.microsoftonline.com/${var.tenant_id}/v2.0/.well-known/openid-configuration"
      allowed_audience = var.audience_values
    }
  }
  tags = var.tags
}

resource "aws_bedrockagentcore_gateway_target" "targets" {
  for_each = var.gateway_targets

  name               = each.value.name
  gateway_identifier = aws_bedrockagentcore_gateway.recordedfurture_gateway.gateway_id
  description        = each.value.description
  region             = data.aws_region.current.name

  credential_provider_configuration {
    gateway_iam_role {}
  }

  target_configuration {
    mcp {
      lambda {
        lambda_arn = var.lambda_function_arn

        tool_schema {
          inline_payload {
            name        = each.value.name
            description = each.value.tool_description

            input_schema {
              type        = "object"
              description = each.value.input_schema_description

              dynamic "property" {
                for_each = each.value.properties
                content {
                  name        = property.value.name
                  type        = property.value.type
                  description = property.value.description
                  required    = property.value.required

                  dynamic "items" {
                    for_each = property.value.items_type != null ? [property.value.items_type] : []
                    content {
                      type = items.value
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

############################Gateway####################################

data "aws_iam_policy_document" "assume_role_gateway" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock-agentcore.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "gateway_custom_execution_policy" {
  version = "2012-10-17"
  statement {
    sid    = "AmazonBedrockAgentCoreGatewayLambdaProd"
    effect = "Allow"
    actions = [
      "lambda:InvokeFunction"
    ]
    resources = [
      var.lambda_function_arn
    ]
  }
}

resource "aws_iam_policy" "gateway_iam_policy" {
  name   = "recorded-future-gateway-policy"
  policy = data.aws_iam_policy_document.gateway_custom_execution_policy.json
  tags   = var.tags
}

resource "aws_iam_policy_attachment" "gateway_policy_attachment_role" {
  name       = "role-policy-attachment-gateway"
  roles      = [aws_iam_role.gateway_role.name]
  policy_arn = aws_iam_policy.gateway_iam_policy.arn
}

resource "aws_iam_role" "gateway_role" {
  name               = "bedrock-agentcore-gateway-role-recorded-future"
  assume_role_policy = data.aws_iam_policy_document.assume_role_gateway.json
}

resource "aws_iam_role_policy_attachment" "default_policy_attachment_lambda_role_gateway" {
  role       = aws_iam_role.gateway_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_permission" "bedrock_agent" {
  statement_id  = "AllowExecutionFromBedrockAgent"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_arn
  principal     = "bedrock-agentcore.amazonaws.com"
  source_arn    = aws_iam_role.gateway_role.arn
}
