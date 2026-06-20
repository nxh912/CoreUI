import os
import json

# Force clear the broken token variable 
os.environ.pop("AWS_BEARER_TOKEN_BEDROCK", None)
# ap-southeast-1
import boto3

## AS IN IAM SETTING
env_region="ap-southeast-1"
model_id = "global.anthropic.claude-sonnet-4-6"
max_tokens = 1000
temperture = 0.7

def get_prompt( instruction, text):
    prompt = [
        {
            "role": "user",
            "content": [
                {"text": instruction},
                {"text": text},
            ]
        }
    ]
    return prompt

# Initialize the native Bedrock client
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=env_region
)

print(f"### Converse api, region : {env_region}")
# Use the unified Converse structure (no provider-specific wrappers needed!)


instruction = "You are a professional coder, and output in JSON format"
text = "Hello! Introduce yourself briefly"
prompt = get_prompt( instruction, text)

try:
    # Call the converse method instead of invoke_model
    print(f"### converse api... PROMPT:\n{prompt}\n")
    response = bedrock_client.converse(
        modelId= model_id,
        messages= prompt,
        inferenceConfig= {
            "maxTokens": max_tokens,
            "temperature": temperture,
        }
    )
    
    # Extracting the text is much simpler with Converse
    output_text = response["output"]["message"]["content"][0]["text"]
    print(f"### output_text:\n{output_text}\n")
except Exception as e:
    print(f"Error invoking model: {e}")
