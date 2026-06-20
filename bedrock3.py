import os
import json

# Force clear the broken token variable 
os.environ.pop("AWS_BEARER_TOKEN_BEDROCK", None)
# ap-southeast-1
import boto3

## AS IN IAM SETTING
env_region="ap-northeast-1"

if True: ### Converse

    # Initialize the native Bedrock client
    bedrock_client = boto3.client(
        service_name="bedrock-runtime",
        region_name=env_region
    )

    print(f"### Converse api, region : {env_region}")
    ### ResourceNotFoundException

    # Use the unified Converse structure (no provider-specific wrappers needed!)
    messages = [
        {
            "role": "user",
            "content": [{"text": "Hello! Introduce yourself briefly."}]
        }
    ]

    try:
        # Call the converse method instead of invoke_model
        print("### converse api")
        response = bedrock_client.converse(
            modelId="global.anthropic.claude-sonnet-4-6",
            messages=messages,
            inferenceConfig={
                "maxTokens": 1000,
                "temperature": 0.7
            }
        )
        
        # Extracting the text is much simpler with Converse
        output_text = response["output"]["message"]["content"][0]["text"]
        print(output_text)

    except Exception as e:
        print(f"Error invoking model: {e}")

else:
    #NOT USED
    ### Invoke
    print(f"### Invoke api, region : {region}")

    bedrock_client = boto3.client(
        service_name= "bedrock-runtime",
        region_name= region
    )

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": "Hello!"}
        ]
    }

    try:
        response = bedrock_client.invoke_model(
            # FIX: Update the retired 3.5 model ID to the active Claude Sonnet 4.6 cross-region ID
            # modelId="global.anthropic.claude-sonnet-4-6",
            modelId="global.anthropic.claude-sonnet-4-6",
            body=json.dumps(payload)
        )
        
        response_body = json.loads(response.get("body").read())
        print(response_body["content"][0]["text"])

    except Exception as e:
        print(f"Error invoking model: {e}")