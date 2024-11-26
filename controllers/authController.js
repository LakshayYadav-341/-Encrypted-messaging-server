const { runPythonScript } = require("../utils/pythonRunner");
const User = require("../models/userModel");
const fs = require("fs");
const path = require("path");

// Register user (store public key)
// const registerUser = async (req, res) => {

//     const { formData, publicKey } = req.body;

//     if (!formData || !publicKey) {
//         return res.status(400).json({ message: "Missing required fields" });
//     }

//     const { firstName, lastName } = formData;
//     if (!firstName || !lastName) {
//         return res.status(400).json({ message: "Missing required fields" });
//     }

//     const db = req.app.get("db");
//     if (!db) {
//         return res
//             .status(500)
//             .json({ message: "Database connection is not established" });
//     }
//     const collection = db.collection("user");
//     console.log(collection);

//     try {
//         console.log("here1");
//         const existingUser = await collection.findOne({ publicKey });
//         console.log(existingUser);

//         if (existingUser)
//             return res.status(400).json({ message: "User with this public key already exist" });

//         const newUser = {
//             firstName,
//             lastName,
//             publicKey,
//         };
//         // console.log("here: ", newUser);

//         await collection.insertOne(newUser);
//         return res
//             .status(201)
//             .json({ message: "Usecr registered successfully" });
//     } catch (error) {
//         return res.status(500).json({ message: "Server error!" });
//     }
// };

const registerUser = async (req, res) => {
    const { formData, publicKey } = req.body;
    if (!formData || !publicKey) {
        return res.status(400).json({ message: "Missing required fields" });
    }

    const { firstName, lastName } = formData;
    if (!firstName || !lastName) {
        return res
            .status(400)
            .json({ message: "First name and last name are required" });
    }

    try {
        const existingUser = await User.findOne({
            "publicKey.x": publicKey.x,
            "publicKey.y": publicKey.y,
        });

        if (existingUser) {
            return res
                .status(400)
                .json({ message: "User with this public key already exists" });
        }

        const newUser = new User({
            firstName,
            lastName,
            publicKey,
        });

        await newUser.save();

        return res
            .status(201)
            .json({ message: "User registered successfully" });
    } catch (error) {
        console.error("Error registering user:", error);
        return res.status(500).json({ message: "Server error" });
    }
};

// Login user (validate public key)
const loginUser = (req, res) => {
    const { username } = req.body;
    if (!users[username]) {
        return res.status(404).json({ message: "User not found" });
    }

    // Generate challenge using Bob's script
    runPythonScript("bob.py", { publicKey: users[username].publicKey })
        .then((challenge) => {
            res.status(200).json({ challenge });
        })
        .catch((err) => {
            res.status(500).json({
                message: "Error generating challenge",
                error: err.message,
            });
        });
};

// Initiate key exchange
const initiateKeyExchange = (req, res) => {
    const { username, response } = req.body;

    // Validate response with Bob's script
    runPythonScript("bob.py", { response })
        .then((validationResult) => {
            if (validationResult.isValid) {
                res.status(200).json({
                    message: "Key exchange successful",
                    sessionToken: validationResult.sessionToken,
                });
            } else {
                res.status(400).json({ message: "Key exchange failed" });
            }
        })
        .catch((err) => {
            res.status(500).json({
                message: "Error validating key exchange",
                error: err.message,
            });
        });
};

module.exports = { registerUser, loginUser, initiateKeyExchange };
