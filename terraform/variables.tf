variable "source_code_repo_url" {
  type        = string
  description = "Repository where IaC and Lambda function source code resides"
}

variable "environment" {
  description = "Environment the infrastructure is deployed in"
  type        = string
}

variable "cost_centre" {
  description = "Cost centre to apply the resources too"
  type        = string
}

variable "lambda_function_name" {
  type        = string
  description = "Name of lambda function"
}

variable "sns_topic_name" {
  type        = string
  description = "SNS topic name"
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
  description = "What does this stupid function do"
}

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

variable "kms_key_alias" {
  type        = string
  description = "KMS key alias used for encryption"
}

variable "enc_string_recordedfuture_api_key" {
  type        = string
  description = "Encrypted RecordedFutures API key for creating SSM parameter"
}

variable "allowed_scopes" {
  type        = list(string)
  description = "Allowed scopes for authorization to the Bedrock Agentcore gateway"
}
