import os
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
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
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
    
    try:
        # Call the AWS AI Runtime
        response = aws_client.invoke_model(
            modelId=model_id,
            body=bytes(import_json_string(native_request), 'utf-8')
        )
        
        # Parse output body
        response_body = response.get("body").read().decode('utf-8')
        import json
        result = json.loads(response_body)
        
        return {
            "status": "success",
            "output": result["content"][0]["text"]
        }
        
    except (BotoCoreError, ClientError) as aws_err:
        raise HTTPException(status_code=502, detail=f"AWS Service error: {str(aws_err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

def import_json_string(data):
    import json
    return json.dumps(data)

if __name__ == "__main__":
    import uvicorn
    # Run locally on http://localhost:8000
    filename = os.path.basename(__file__)
    print(f"FILE : {filename}")
    uvicorn.run(f"{filename[:-3]}:app", host="0.0.0.0", port=8000, reload=True)
