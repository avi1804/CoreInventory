const db = require("../config/db");

exports.addReceipt = (req, res) => {
  const { product_id, warehouse_id, quantity } = req.body;

  const receiptSQL =
    "INSERT INTO receipts (product_id,warehouse_id,quantity) VALUES (?,?,?)";

  db.query(receiptSQL, [product_id, warehouse_id, quantity], (err, result) => {
    if (err) {
      return res.status(500).json(err);
    }

    const stockSQL =
      "UPDATE stock SET quantity = quantity + ? WHERE product_id=? AND warehouse_id=?";

    db.query(
      stockSQL,
      [quantity, product_id, warehouse_id],
      (err2, result2) => {
        if (err2) {
          return res.status(500).json(err2);
        }

        res.json("Receipt Added & Stock Updated");
      },
    );
  });
};
