import boto3
import json

# This automatically picks up AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY from your environment
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

# Format the payload for Anthropic Claude
payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "messages": [
        {"role": "user", "content": "Hello!"}
    ]
}

try:
    response = bedrock_client.invoke_model(
        modelId="us.anthropic.claude-sonnet-4-6",
        body=json.dumps(payload)
    )
    
    # Parse and print the text block from the response
    response_body = json.loads(response.get("body").read())
    print(response_body["content"][0]["text"])

except Exception as e:
    print(f"Error invoking model: {e}")