const express = require("express");
const { registerUser, loginUser, initiateKeyExchange } = require("../controllers/authController");

const router = express.Router();

router.post("/register", registerUser);
router.post("/login", loginUser);
router.post("/keyExchange", initiateKeyExchange);

module.exports = router;
