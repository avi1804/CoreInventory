const router = require("express").Router();
const receipt = require("../controllers/receiptController");

router.post("/add", receipt.addReceipt);

module.exports = router;
