import os
import json
import boto3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Cortex AI Bridge Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ENV_REGION = "ap-southeast-1"  # Singapore
MODEL_ID = "global.anthropic.claude-sonnet-4-6"
MAX_TOKENS = 1000

def get_prompt(instruction, text):
    return [
        {
            "role": "user",
            "content": [
                {"text": instruction},
                {"text": text},
            ]
        }
    ]

def clean_response(text):
    if text:
        return text.replace("```json", "").replace("```", "").strip()
    return text

def bedrock_converse(instruction, text, temperature_val):
    # CRITICAL ENVIRONMENT CLEANUP: Pop out conflicting bearer keys before client initiation
    os.environ.pop("AWS_BEARER_TOKEN_BEDROCK", None)

    bedrock_client = boto3.client(
        service_name="bedrock-runtime",
        region_name=ENV_REGION
    )

    print(f"### Converse api, region : {ENV_REGION}")
    prompt = get_prompt(instruction, text)

    try:
        print(f"### converse api... PROMPT:\n{prompt}\n")
        response = bedrock_client.converse(
            modelId=MODEL_ID,
            messages=prompt,
            inferenceConfig={
                "maxTokens": MAX_TOKENS,
                "temperature": temperature_val,
            }
        )
        
        output_text = response["output"]["message"]["content"][0]["text"]
        print(f"### output_text:\n{output_text}\n")

        return {"result": clean_response(output_text)}
    except Exception as e:
        print(f"Error invoking model: {e}")
        raise HTTPException(status_code=500, detail=f"Bedrock Error: {str(e)}")

@app.post("/api/v1/mro_data")
async def generate_ai_response(data: PromptRequest):
    return bedrock_converse(
        instruction=data.instruction, 
        text=data.context, 
        temperature_val=data.temperature
    )

if __name__ == "__main__":
    import uvicorn
    filename = os.path.basename(__file__)
    print(f"FILE : {filename}")
    uvicorn.run(f"{filename[:-3]}:app", host="0.0.0.0", port=8000, reload=True)
    '''testing
    curl -X POST -H "Content-Type: application/json" "http://127.0.0.1:8000/api/v1/mro_data" -d '{
        "instruction": "you are super coder in health care",
        "context": "list all specialist in medicine",
        "temperature": 0.7
    }'
    '''