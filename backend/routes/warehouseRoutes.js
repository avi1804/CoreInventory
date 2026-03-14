const router = require("express").Router();
const warehouse = require("../controllers/warehouseController");

router.post("/add", warehouse.addWarehouse);

module.exports = router;
