const router = require("express").Router();
const delivery = require("../controllers/deliveryController");

router.post("/add", delivery.addDelivery);

module.exports = router;
