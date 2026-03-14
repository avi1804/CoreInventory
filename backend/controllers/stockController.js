const db = require("../config/db");

exports.addStock = (req, res) => {
  const { product_id, warehouse_id, quantity } = req.body;

  const sql =
    "INSERT INTO stock (product_id,warehouse_id,quantity) VALUES (?,?,?)";

  db.query(sql, [product_id, warehouse_id, quantity], (err, result) => {
    if (err) {
      return res.status(500).json(err);
    }

    res.json("Stock Added");
  });
};
