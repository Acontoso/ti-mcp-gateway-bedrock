variable "gateway_name" {
  type        = string
  description = "Name of the gateway"
}

variable "gateway_description" {
  type        = string
  description = "Description of the gateway"
}

variable "authorization_type" {
  type        = string
  description = "Authorization type used to authenticate to the gateway"
}

variable "tenant_id" {
  type        = string
  description = "Microsoft Tenant ID used for authentication to the gateway"
}

variable "audience_values" {
  type        = list(string)
  description = "List of audience values used for authentication to the gateway"
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to the gateway"
}

variable "lambda_function_arn" {
  type        = string
  description = "ARN of the Lambda function to apply to the gateway that handles the application logic for the gateway targets"
}

variable "gateway_targets" {
  description = "Map of gateway targets to create"
  type = map(object({
    name                     = string
    description              = string
    tool_description         = string
    input_schema_description = string
    properties = list(object({
      name        = string
      type        = string
      description = string
      required    = bool
      items_type  = optional(string)
    }))
  }))
}
