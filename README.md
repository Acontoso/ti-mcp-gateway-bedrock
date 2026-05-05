# Recorded Future MCP Bedrock Gateway

An AWS Lambda-based gateway that integrates AWS Bedrock Agent Core with Recorded Future's threat intelligence services. This project enables seamless threat intelligence lookups and malware analysis through Bedrock agents.

## 🎯 Overview

The **Recorded Future MCP Bedrock Gateway** is a serverless integration layer that bridges AWS Bedrock Agent Core with Recorded Future's threat intelligence APIs. It provides a unified interface for security teams to query threat data, including malware analysis, indicators of compromise (IOCs), and sandbox intelligence, directly from Bedrock-powered agents.

### Use Cases

- **Threat Intelligence Enrichment**: Enrich security investigations with real-time threat data
- **Automated Malware Analysis**: Query malware risk scores, file extensions, and sandbox signatures
- **IOC Lookup**: Search for intelligence on file hashes, domains, and IP addresses
- **Agent-Driven Security**: Enable Bedrock agents to autonomously pull threat intelligence

## ✨ Features

- **Malware Intelligence Search**: Query Recorded Future for malware data using SHA256 hashes
- **IOC Enrichment**: Look up multiple indicators of compromise (hashes, domains, IPs) in one request
- **Sandbox Analysis**: Retrieve detailed malware analysis reports from Recorded Future's sandbox
- **Lambda Integration**: Serverless deployment with minimal operational overhead
- **Pydantic Models**: Type-safe request/response handling
- **AWS SSM Parameter Store Integration**: Secure API credential management
- **JSON Logging**: CloudWatch-compatible JSON-formatted logs
- **Infrastructure as Code**: Complete Terraform deployment configuration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   AWS Bedrock Agent Core                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│    AWS Lambda Function (recorded-future-mcp-gateway)        │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Tool Dispatcher (searchMalware, lookupIOC, searchSand) ││
│  └──────────────────────┬────────────────────────────────┬┘│
│                         │                                │  │
│  ┌──────────────────────▼─────────────────────────────┐  │  │
│  │         Recorded Future API Client                │  │  │
│  │  • generate_headers()                             │  │  │
│  │  • Model Validation (Pydantic)                    │  │  │
│  └──────────────────────┬─────────────────────────────┘  │  │
│                         │                                │  │
│  ┌──────────────────────▼─────────────────────────────┐  │  │
│  │      AWS SSM Parameter Store (API Key)            │  │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
              ┌──────────────────────────┐
              │  Recorded Future API     │
              │  (SOAR v3, Malware v1)   │
              └──────────────────────────┘
```

## 📦 Prerequisites

- **Python 3.11+**
- **AWS Account** with appropriate permissions for:
  - Lambda
  - IAM
  - SSM Parameter Store
  - CloudWatch
- **Terraform 1.0+**
- **Recorded Future API Token** (stored in AWS SSM Parameter Store)
- **AWS CLI** configured with appropriate credentials

## 📁 Project Structure

```
.
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── code/                              # Lambda function code
│   ├── __init__.py
│   ├── main.py                        # Lambda handler
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py                  # Pydantic data models
│   ├── services/
│   │   ├── __init__.py
│   │   └── aws.py                     # AWS service integrations
│   ├── tools/
│   │   ├── __init__.py
│   │   └── recordedFuture.py          # Recorded Future API client
│   └── utils/
│       ├── __init__.py
│       └── logs.py                    # Logging configuration
└── terraform/                         # Infrastructure as Code
    ├── main.tf                        # Terraform provider config
    ├── lambda.tf                      # Lambda function definition
    ├── iam.tf                         # IAM roles and policies
    ├── gateway.tf                     # API Gateway config
    ├── sns.tf                         # SNS topic configuration
    ├── locals.tf                      # Local variables
    ├── variables.tf                   # Input variables
    ├── data.tf                        # Data sources
    └── terraform.tfvars               # Variable values
```

## 🔐 Security Considerations

- **API Credentials**: Stored securely in AWS SSM Parameter Store with encryption
- **IAM Permissions**: Lambda execution role has minimal required permissions
- **HTTPS Only**: All API calls to Recorded Future use HTTPS
- **Input Validation**: All inputs validated using Pydantic models
- **Error Handling**: Sensitive information not exposed in error messages

## 📚 Dependencies

Key dependencies:

- **boto3**: AWS SDK for Python
- **requests**: HTTP client library
- **pydantic**: Data validation and settings management

See `requirements.txt` for the complete list.

### Application Registration & Integration with Azure AD
Example will be integrating CoPilot as the MCP/Agentic AI solution with the MCP services provided by AWS Bedrock Gateway. This will use Oauth Authorization flow to allow set users that are assigned to an Azure AD application to access the MCP server. Requested scopes are scopes that can be attached to the users JWT token, and be used to determine what gateways the authenticated user has access too.

#### Application Registration 1 - Resource Server (MCP)
This application registration represents the resource server, and will expose an API and a series of scopes (delegated) that can be used to define the level of access the authenticated user has to the MCP tools and services. The bedrock agentcore gateway will see the JWT token based on the application ID represented by this Azure AD application registration. The things to do when creating this registration.
- Add the `accessTokenAcceptedVersion` to the manifest file, with the value being `2`
- Expose an API, and define the scopes that are available to be requested and specify if these scopes need admin consent or standard user consent.
- Pre-authorize `front-end` client application (the one users sign into). This is to ensure no admin consent prompt is shown.


#### Application Registration 2 - Client App
This client application is what signs in users and requests the API resource from the resource server application registration. This can be a public application that allows for implicit flows (or public client flows) that will return an ID token and or a Access token directly from the authorization endpoint. For this case, its using the oauth authorization code flow to recieve the access token that will be used when agentic solution is communicating to our MCP server.
- API Permissions: Grant delegated (or app) permissions to the resource servers scopes, and what scopes can be requested.
- Redirect URI: Add the redirect URI on where the token will be recieved (In Agentic solutions, or for Security CoPilot the callback being `https://securitycopilot.microsoft.com/auth/v1/callback`)
- Since this is a secure client, create a secret that is used for this integration (Some can use PKCE but most ask for secret)
- Provide admin consent to the application permissions. (add email, openid & profile to the scopes) & offline_access for access token refresh can occur

#### Bedrock Agentcore Authentication
For Entra ID, add the discovery endpoint v2 `https://login.microsoftonline.com/<TENANT_ID>/v2.0/.well-known/openid-configuration"`, and define the allowed audiences `app reg id of resource server SP`, the scopes required and any custom claims defined in the token (can also include group memberships if the claim is configured to include).

To test out the entire flow, can run the following python script. This will get the access token for the app registration for resource server as the client app. Only thing you need to do is add the redirect uri of `http://localhost` to the Client app.

```python
import msal
import json
import base64

# Configuration
TENANT_ID = "<your-tenant-id>"
CLIENT_ID = "<App #2 Client ID>"
CLIENT_SECRET = "<App #2 Client Secret>"
SCOPE = ["api://<App #1 Application ID>/Mcp.Tools.ReadWrite", "offline_access"]
REDIRECT_URI = "http://localhost"  # Add this to App #2 redirect URIs in Azure Portal

# Create MSAL confidential client
app = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    client_credential=CLIENT_SECRET,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}"
)

# Step 1: Get the authorization URL
auth_url = app.get_authorization_request_url(
    scopes=SCOPE,
    redirect_uri=REDIRECT_URI
)

print("🌐 Open this URL in your browser to sign in:\n")
print(auth_url)
print("\nAfter signing in, you will be redirected to a localhost URL.")
print("Copy the full redirect URL from your browser address bar and paste it below.\n")

# Step 2: Get the auth code from the redirect
redirect_response = input("Paste the full redirect URL here: ").strip()

# Extract the auth code from the redirect URL
from urllib.parse import urlparse, parse_qs
parsed = urlparse(redirect_response)
auth_code = parse_qs(parsed.query).get("code", [None])[0]

if not auth_code:
    print("❌ Could not extract authorization code from URL")
    exit(1)

print(f"\n✅ Authorization code extracted successfully")

# Step 3: Exchange auth code for access token
result = app.acquire_token_by_authorization_code(
    code=auth_code,
    scopes=SCOPE,
    redirect_uri=REDIRECT_URI
)

if "access_token" in result:
    print("✅ Token acquired successfully!\n")
    print(f"Access Token:\n{result['access_token']}\n")

    # Decode and pretty print the token claims
    token_parts = result['access_token'].split('.')
    payload = token_parts[1] + "=" * (4 - len(token_parts[1]) % 4)
    decoded = json.loads(base64.b64decode(payload).decode('utf-8'))

    print("📋 Decoded Token Claims:")
    print(json.dumps(decoded, indent=2))

    print(f"\n🔍 Key Claims to Check:")
    print(f"  aud (audience) : {decoded.get('aud')}")
    print(f"  iss (issuer)   : {decoded.get('iss')}")
    print(f"  appid          : {decoded.get('appid')}")
    print(f"  scp (scopes)   : {decoded.get('scp')}")
    print(f"  roles          : {decoded.get('roles')}")

    if result.get("refresh_token"):
        print(f"\n🔄 Refresh token also received (offline_access granted)")

else:
    print("❌ Failed to acquire token:")
    print(f"  Error       : {result.get('error')}")
    print(f"  Description : {result.get('error_description')}")
```

