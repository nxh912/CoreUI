require("dotenv").config();
const express = require("express");
// 1. Import ConverseCommand instead of InvokeModelCommand
const { BedrockRuntimeClient, ConverseCommand } = require("@aws-sdk/client-bedrock-runtime");

const app = express();
app.use(express.json());

// 2. Initialize the client (SDK automatically reads credentials from your environment)
// const client = new BedrockRuntimeClient({ region: "us-east-1" });
const client = new BedrockRuntimeClient({ region: process.env.AWS_REGION || "us-east-1" });

// Add this to confirm the actual resolved region:
console.log("LINE 14: Region config:", process.env.AWS_REGION || "us-east-1");

app.post("/api/bedrock/invoke", async (req, res) => {
  const { prompt } = req.body;
  console.log("LINE 18: /api/bedrock/invoke");
  console.log("LINE 19: prompt : ", prompt);
  const payload = {    
    //modelId: "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    modelId: "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    messages: [
      {
        role: "user",
        content: [{ text: prompt }],
      },
    ],
    inferenceConfig: {
      maxTokens: 1024,
      temperature: 0.7,
    },
  };
  console.log("LINE 33: /api/bedrock/invoke");

  //res.send('Hello World!');
  try {
    const command = new InvokeModelCommand(payload);
    console.log("LINE 36: command:", command); 

    const response = await client.send(command);
    console.log("LINE 36: result:", result); 

    const result = JSON.parse(Buffer.from(response.body).toString("utf-8"));
    console.log("LINE 36: response:", response); 

    res.json(result);
  } catch (err) {
    console.error("Bedrock error:", err.message);
    res.status(500).json({ error: err.message });
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🚀 Bedrock proxy server running on http://localhost:${PORT}`);
});
