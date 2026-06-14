const express = require("express");
const axios = require("axios");
const cors = require("cors");
const path = require("path");

const app = express();
const pythonService = process.env.PYTHON_SERVICE_URL || "http://127.0.0.1:5000";
app.use(express.json());
app.use(cors());

app.use(express.static(path.join(__dirname, "..", "frontend")));

app.post("/analyze", async (req, res) => {
  try {
    const result = await axios.post(`${pythonService}/analyze`, req.body, {
      headers: { "Content-Type": "application/json" }
    });
    res.json(result.data);
  } catch (err) {
    const message = err.response?.data?.error || err.message || "Error processing request.";
    res.status(500).json({ error: message });
  }
});

app.post("/chat", async (req, res) => {
  try {
    const result = await axios.post(`${pythonService}/chat`, req.body, {
      headers: { "Content-Type": "application/json" }
    });
    res.json(result.data);
  } catch (err) {
    const message = err.response?.data?.error || err.message || "Error processing request.";
    res.status(500).json({ error: message });
  }
});

app.get("/*", (req, res) => {
    res.sendFile(path.join(__dirname, "..", "frontend", "index.html"));
});

app.listen(3000, () => console.log("Server running on http://localhost:3000"));