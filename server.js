const express = require("express");
const http = require("http");
const bodyParser = require("body-parser");
const { Server } = require("socket.io");
require("dotenv").config();
const { MongoClient } = require("mongodb");
const authRouter = require("./routes/auth"); // Import your router
const app = express();
const server = http.createServer(app);
const io = new Server(server);
const cors = require("cors");
const mongoose = require("mongoose");

const uri = process.env.MONGODB_URI;


const connectToDatabase = async () => {
    try {
        await mongoose.connect(uri, {
            connectTimeoutMS: 30000,
            socketTimeoutMS: 30000,
        });
        app.set("db", mongoose.connection);
        console.log("Connected to MongoDB successfully!");
    } catch (error) {
        console.error("Error connecting to MongoDB:", error);
        process.exit(1); 
    }
};

connectToDatabase();

app.use(bodyParser.json());
app.use(cors());
// Use indexRouter to handle routes
app.use("/", authRouter);

// WebSocket connection handling
io.on("connection", (socket) => {
    console.log("A user connected");

    socket.on("disconnect", () => {
        console.log("A user disconnected");
    });

    socket.on("keyExchange", (data) => {
        console.log("Key exchange received:", data);
    });

    socket.on("encryptedMessage", (data) => {
        console.log("Encrypted message received:", data);
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
