variable "lambda_function_name" {
  type        = string
  description = "Name of lambda function"
}

variable "runtime" {
  type        = string
  description = "Lambda runtime language and version"
}

variable "handler" {
  type        = string
  description = "Specify file & main entry point of Lambda function"
}

variable "memory_size" {
  type        = string
  description = "Size of memory to allocate Lambda function during runtime"
}

variable "timeout" {
  type        = number
  description = "Lambda function timeout"
}

variable "description" {
  type        = string
  description = "Description of the Lambda function"
}

variable "sns_topic_arn" {
  type        = string
  description = "ARN of the SNS topic to allow failures to be published from the Lambda function"
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to the gateway"
}

variable "ssm_param_path_api_key" {
  type        = string
  description = "Path of the SSM parameter that contains the API key"
  default = "/soar-api/recorded_future_api"
}
