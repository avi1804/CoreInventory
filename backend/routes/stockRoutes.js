const router = require("express").Router();
const stock = require("../controllers/stockController");

router.post("/add", stock.addStock);

module.exports = router;
