const express = require("express");
const axios = require("axios");
const cors = require("cors");
const path = require("path");

const app = express();
app.use(express.json());
app.use(cors());

app.use(express.static(path.join(__dirname, "..", "frontend")));

app.post("/analyze", async (req, res) => {
    try {
        const result = await axios.post("http://127.0.0.1:5000/analyze", req.body);
        res.json(result.data);
    } catch (err) {
        res.status(500).send("Error processing request");
    }
});

app.get("/*", (req, res) => {
    res.sendFile(path.join(__dirname, "..", "frontend", "index.html"));
});

app.listen(3000, () => console.log("Server running on http://localhost:3000"));