const router = require("express").Router();
const transfer = require("../controllers/transferController");

router.post("/transfer", transfer.transferStock);

module.exports = router;
