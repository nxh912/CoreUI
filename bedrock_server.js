require("dotenv").config();

console.log("ACCESS KEY:", process.env.AWS_ACCESS_KEY_ID ? "loaded ✅" : "missing ❌");
console.log("ACCESS KEY:", process.env.AWS_ACCESS_KEY_ID)
console.log("SECRET:", process.env.AWS_SECRET_ACCESS_KEY);

console.log("REGION:", process.env.AWS_REGION);

const express = require("express");
const { BedrockRuntimeClient, ConverseCommand } = require("@aws-sdk/client-bedrock-runtime");

const app = express();
app.use(express.json());

// Initialize the Bedrock Client
const client = new BedrockRuntimeClient({ region: process.env.AWS_REGION || "us-east-1" });
console.log("LINE 14: Region config:", process.env.AWS_REGION || "us-east-1");

app.post("/api/bedrock/invoke", async (req, res) => {
  const { prompt } = req.body;
  
  // Guard clause if prompt is missing
  if (!prompt) {
    return res.status(400).json({ error: "Prompt is required in the request body." });
  }

  console.log("LINE 18: /api/bedrock/invoke");
  console.log("LINE 19: prompt:", prompt);

  // Configure payload for the Converse API
  const payload = {
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
  console.log("LINE 33: payload ready");

  try {
    const command = new ConverseCommand(payload); 
    const response = await client.send(command);  
    console.log("LINE 38: response received");

    // Extract the text reply from AWS Bedrock response structure
    const replyText = response.output.message.content[0].text;
    console.log("LINE 41: replyText:", replyText);

    res.json({ output: replyText });
  } catch (err) {
    console.error("Bedrock error:", err.message);
    res.status(500).json({ error: err.message });
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🚀 Bedrock proxy server running on http://localhost:${PORT}`);
});