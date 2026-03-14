const router = require("express").Router();
const product = require("../controllers/productController");
router.post("/add", product.addProduct);
router.get("/all", product.getProducts);
router.put("/update/:id", product.updateProduct);
router.delete("/delete/:id", product.deleteProduct);

module.exports = router;
