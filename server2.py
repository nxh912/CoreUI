import os
import json
import boto3
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from botocore.exceptions import BotoCoreError, ClientError


app = FastAPI(title="Cortex AI Bridge Engine")

# Configure CORS so your VueUI Frontend can access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, swap "*" for your exact Vue app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the expected JSON payload from VueUI
class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 500
    temperature: float = 0.7

# Initialize AWS Client safely using environment variables
def get_aws_client():
    try:
        # Boto3 automatically searches for AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
        # and AWS_DEFAULT_REGION in your environment.
        return boto3.client(
            service_name="bedrock-runtime", 
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AWS Initialization Error: {str(e)}")

@app.post("/api/v1/generate")
async def generate_ai_response(request: PromptRequest, aws_client=Depends(get_aws_client)):
    # Example using AWS Bedrock (e.g., Claude 3 Sonnet model)
    model_id = "anthropic.claude-sonnet-4-6"
    model_id = "us.anthropic.claude-3-sonnet-20240229-v1"




    if False:
        from openai import OpenAI

        client = OpenAI()

        response = client.responses.create(
            model=model_id,
            input="What is the most popular song on Radio Free Mars?",
            tools=[
                {
                    "type": "function",
                    "name": "get_most_popular_song",
                    "description": "Returns the most popular song on a radio station",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "station_name": {
                                "type": "string",
                                "description": "Name of the radio station"
                            }
                        },
                        "required": ["station_name"]
                    }
                }
            ]
        )

        print(response.output)
        assert(0)
        if response.output and response.output[0].content:
            tool_call = response.output[0].content[0]
            args = json.loads(tool_call["arguments"])
            result = get_most_popular_song(args["station_name"])
            
            final_response = client.responses.create(
                model="gpt-4o",
                input=[
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result
                    }
                ]
            )
            
            print(final_response.output_text)

    if False:
        from openai import OpenAI

        client = OpenAI()

        response = client.responses.create(
            model="gpt-4o",
            input="What is the most popular song on Radio Free Mars?",
            tools=[
                {
                    "type": "function",
                    "name": "get_most_popular_song",
                    "description": "Returns the most popular song on a radio station",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "station_name": {
                                "type": "string",
                                "description": "Name of the radio station"
                            }
                        },
                        "required": ["station_name"]
                    }
                }
            ]
        )

        if response.output and response.output[0].content:
            tool_call = response.output[0].content[0]
            args = json.loads(tool_call["arguments"])
            result = get_most_popular_song(args["station_name"])
            
            final_response = client.responses.create(
                model="oss-gpt-120b",
                input=[
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result
                    }
                ]
            )
            
            print(final_response.output_text)

    # Structure the payload according to your specific AWS model's expectations
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
        "messages": [
            {
                "role": "user",
                "content": request.prompt
            }
        ]
    }
    
    if False:
        models = [
            #"anthropic.claude-opus-4-5-20251101-v1:0",
            #"anthropic.claude-fable-5",
            #"anthropic.claude-opus-4-8",
            #"amazon.nova-2-lite-v1:0",
            'anthropic.claude-opus-4-7',
            
            "anthropic.claude-haiku-4-5-20251001-v1:0",
            "anthropic.claude-opus-4-6-v1",
            "twelvelabs.pegasus-1-2-v1:0",
            "anthropic.claude-sonnet-4-6",
            "cohere.embed-v4:0",
            "anthropic.claude-sonnet-4-5-20250929-v1:0",
            "amazon.nova-pro-v1:0",
            "amazon.nova-lite-v1:0",
            "amazon.nova-micro-v1:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
            "anthropic.claude-3-5-sonnet-20240620-v1:0",
            "anthropic.claude-3-sonnet-20240229-v1:0:28k",
            "anthropic.claude-3-sonnet-20240229-v1:0:200k",
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "anthropic.claude-sonnet-4-20250514-v1:0",
            "cohere.embed-english-v3",
            "cohere.embed-multilingual-v3"
        ]

        for model_id in models:
            try:
                # Call the AWS AI Runtime
                response = aws_client.invoke_model(
                    modelId = model_id,
                    body=bytes( import_json_string(native_request), 'utf-8')
                )
                
                # Parse output body
                response_body = response.get("body").read().decode('utf-8')
                result = json.loads(response_body)
                
                print(f"MODEL : {model_id}")
                print(f"RESPONSE : {response}")

                return {
                    "status": "success",
            
                    "model_id": f"{model_id}",

                    "output": result["content"][0]["text"]
                }
                
            except (BotoCoreError, ClientError) as aws_err:
                raise HTTPException(status_code=502, detail=f"AWS Service error: {str(aws_err)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    if True:
        client = anthropic.Anthropic(
            default_headers={"anthropic-workspace-id": os.environ["ANTHROPIC_WORKSPACE_ID"]},
        )

        message = client.messages.create(
            model="anthropic.claude-haiku-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": "What is Amazon Bedrock?"}],
        )
        print(message.content[0].text)

    if False:
        import anthropic
        from aws_bedrock_token_generator import provide_token

        client = anthropic.Anthropic(
            api_key=provide_token(),
            base_url="https://bedrock-mantle.ap-northeast-1.api.aws/anthropic",
            default_headers={"anthropic-workspace-id": "default"},
        )

        message = client.messages.create(
            model="anthropic.claude-haiku-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": "What is Amazon Bedrock?"}],
        )
        print(message.content[0].text)

    if False:
        client = boto3.client("bedrock-runtime", region_name="ap-southeast-1")

        #model_id = "anthropic.claude-haiku-4-5" # Or your intended model
        model_id = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
        #model_id = "anthropic.claude-fable-5"

        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {
                    "role": "user",
                    "content": "Explain how to call AWS Bedrock via REST in one sentence."
                }
            ]
        }

        # 2. Serialize to JSON string, then encode to bytes
        body_bytes = json.dumps(native_request).encode('utf-8')

        # 3. Call invoke_model
        response = aws_client.invoke_model(
            modelId=model_id,
            body=body_bytes,        # Use the bytes object here
            contentType="application/json"
        )

        print(response)
        assert(0)

def import_json_string(data):
    import json
    return json.dumps(data)

if __name__ == "__main__":
    import uvicorn
    # Run locally on http://localhost:8000
    filename = os.path.basename(__file__)
    print(f"FILE : {filename}")
    uvicorn.run(f"{filename[:-3]}:app", host="0.0.0.0", port=8000, reload=True)
