const { runPythonScript } = require("../utils/pythonRunner");

// Send an encrypted message
const sendMessage = (req, res) => {
    const { sender, recipient, message } = req.body;

    runPythonScript("alice.py", { sender, recipient, message })
        .then((encryptedMessage) => {
            res.status(200).json({ encryptedMessage });
        })
        .catch((err) => {
            res.status(500).json({ message: "Error encrypting message", error: err.message });
        });
};

// Fetch messages (mocked for now)
const fetchMessages = (req, res) => {
    res.status(200).json({ messages: ["Mocked message 1", "Mocked message 2"] });
};

module.exports = { sendMessage, fetchMessages };
