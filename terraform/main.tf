locals {
  tags = merge(
    {
      "env"        = "${var.environment}"
      "terraform"  = "true"
      "bu"         = "security"
      "RepoUrl"    = "${var.source_code_repo_url}"
      "service"    = "bedrock-gateway-recordedFuture"
      "owner"      = "patrick-robertson"
      "author"     = "alex skoro"
      "costcentre" = "${var.cost_centre}"
    }
  )
  aws_region = "ap-southeast-2"
}

module "sns" {
  source         = "./modules/sns"
  sns_topic_name = var.sns_topic_name
  tags           = local.tags
}

module "lambda" {
  source               = "./modules/lambda"
  lambda_function_name = var.lambda_function_name
  runtime              = var.runtime
  handler              = var.handler
  memory_size          = var.memory_size
  timeout              = var.timeout
  description          = var.description
  sns_topic_arn        = module.sns.sns_arn
  tags                 = local.tags
}

module "bedrock_gateway" {
  source              = "./modules/bedrockgateway"
  gateway_name        = var.gateway_name
  gateway_description = var.gateway_description
  lambda_function_arn = module.lambda.lambda_function_arn
  tenant_id           = var.tenant_id
  audience_values     = var.audience_values
  authorization_type  = var.authorization_type
  tags                = local.tags
  gateway_targets = {
    searchMalware = {
      name                     = "searchMalware"
      description              = "Query malware intelligence for one or more SHA256 file hashes. This function calls Recorded Future's malware IOC endpoint and returns a normalized list of malware attributes per matched hash."
      tool_description         = "Query malware intelligence for one or more SHA256 file hashes. This function calls Recorded Future's malware IOC endpoint and returns a normalized list of malware attributes per matched hash. Call this tool when you need malware metadata for known sample hashes (for example: triage enrichment, scoring, tagging, extension profiling). This strictly requires a SHA256 hash as input and will not return results for other IOC types."
      input_schema_description = "Input schema for malware search"
      properties = [{
        name        = "sha256_list"
        type        = "array"
        description = "List of SHA256 hashes to search. This strictly requires a SHA256 hash as input and will not return results for other IOC types."
        required    = true
        items_type  = "string"
      }]
    }
    lookupIOC = {
      name                     = "lookupIOC"
      description              = "Perform multi-type IOC enrichment for hashes, domains, and IP addresses."
      tool_description         = "Perform multi-type IOC enrichment for hashes, domains, and IP addresses. Use this tool for general IOC - Indicator of Compromise enrichment workflows during a security event or incident investigation, where inputs may include one or more IOC types (IP address, domain name, hash) in a single request."
      input_schema_description = "Input schema for IOC lookup"
      properties = [{
        name        = "ip"
        type        = "array"
        description = "List of IP addresses, IPv4 & IPv6 used to enrich their corresponding intelligence from Recorded Future"
        required    = false
        items_type  = "string"
      },
      {
        name        = "domain"
        type        = "array"
        description = "List of domain names used to enrich their corresponding intelligence from Recorded Future"
        required    = false
        items_type  = "string"
      },
      {
        name        = "hash"
        type        = "array"
        description = "List of hashes used to enrich their corresponding intelligence from Recorded Future. This will accept any file hash type (SHA256, MD5, SHA1) but results may vary based on the prevalence of each hash type in Recorded Future's data."
        required    = false
        items_type  = "string"
      }]
    }
    searchSandbox = {
      name                     = "searchSandbox"
      description              = "Retrieve malware dynamic-analysis (sandbox) reports for a SHA256 hash."
      tool_description         = "Retrieve malware dynamic-analysis (sandbox) reports for a SHA256 hash. This function queries malware sandbox reports and returns behavioral analysis data such as signatures, network activity, processes, and extracted artifacts. Use this MCP tool after hash triage when detailed behavioral evidence is needed (for example: incident investigation or malware detonation context) & when you specifically need sandbox report content, not just IOC risk scoring. This strictly requires a SHA256 hash as input and will not return results for other IOC types."
      input_schema_description = "Input schema for sandbox search"
      properties = [{
        name        = "hash"
        type        = "string"
        description = "SHA256 hash to search. This strictly requires a SHA256 hash as input and will not return results for other IOC types."
        required    = true
      }]
    }
  }
}
