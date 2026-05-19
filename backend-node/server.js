const express = require("express");
const axios = require("axios");
const cors = require("cors");

const app = express();
app.use(express.json());
app.use(cors());

app.post("/analyze", async (req, res) => {
    try {
        const result = await axios.post("http://127.0.0.1:5000/analyze", req.body);
        res.json(result.data);
    } catch (err) {
        res.status(500).send("Error processing request");
    }
});

app.listen(3000, () => console.log("Server running on 3000"));