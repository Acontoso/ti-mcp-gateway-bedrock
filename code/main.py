from utils.logs import logger
import json
from tools.recordedFuture import searchMalware, searchIOC, searchSandbox
from models.models import IOCLookupPayload, MalwareLookupPayload

# Access context properties in your Lambda function
def lambda_handler(event, context):
    """Lambda function to handle incoming requests and process them based on the tool name."""
    delimiter = "___"
    
    originalToolName = context.client_context.custom['bedrockAgentCoreToolName']
    toolName = originalToolName[originalToolName.index(delimiter) + len(delimiter):]
    # Process the request based on the tool name
    if toolName == 'searchMalware':
        logger.info(f"Tool selected is searchMalware with event: {json.dumps(event)}")
        payload = MalwareLookupPayload(**event)
        return {"data": [item.model_dump() for item in searchMalware(payload)]}
    elif toolName == 'lookupIOC':
        logger.info(f"Tool selected is lookupIOC with event: {json.dumps(event)}")
        payload = IOCLookupPayload(**event)
        # model_dump coversion of pydantic model to dict, exclude_defaults and exclude_unset to remove keys with default values or not set values
        # Can call model_dump_json() if you want to return a JSON string instead of a dict
        return {"data": searchIOC(payload).model_dump()}
    elif toolName == 'searchSandbox':
        logger.info(f"Tool selected is searchSandbox with event: {json.dumps(event)}")
        hash_value = event.get("hash")
        return {"data": searchSandbox(hash_value).model_dump(exclude_defaults=True, exclude_unset=True)}
    else:
        return {"error": f"Unknown tool name: {toolName}"}

if __name__ == "__main__":
    lambda_handler(None, None)
