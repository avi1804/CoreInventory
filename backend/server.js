const express = require("express");
const cors = require("cors");

const db = require("./config/db");
const authRoutes = require("./routes/authRoutes");
const productRoutes = require("./routes/productRoutes");
const warehouseRoutes = require("./routes/warehouseRoutes");
const stockRoutes = require("./routes/stockRoutes");
const receiptRoutes = require("./routes/receiptRoutes");
const deliveryRoutes = require("./routes/deliveryRoutes");
const transferRoutes = require("./routes/transferRoutes");

const app = express();

app.use(express.json());
app.use(cors());

app.use("/api/auth", authRoutes);
app.use("/api/products", productRoutes);
app.use("/api/warehouses", warehouseRoutes);
app.use("/api/stock", stockRoutes);
app.use("/api/receipts", receiptRoutes);
app.use("/api/deliveries", deliveryRoutes);
app.use("/api/transfers", transferRoutes);
app.get("/", (req, res) => {
  res.send("CoreInventory API Running");
});

app.listen(5000, () => {
  console.log("Server running on port 5000");
});
