const db = require("../config/db");

exports.transferStock = (req, res) => {
  const { product_id, from_warehouse, to_warehouse, quantity } = req.body;

  const transferSQL =
    "INSERT INTO transfers (product_id,from_warehouse,to_warehouse,quantity) VALUES (?,?,?,?)";

  db.query(
    transferSQL,
    [product_id, from_warehouse, to_warehouse, quantity],
    (err, result) => {
      if (err) {
        return res.status(500).json(err);
      }

      const decreaseStock =
        "UPDATE stock SET quantity = quantity - ? WHERE product_id=? AND warehouse_id=?";

      db.query(
        decreaseStock,
        [quantity, product_id, from_warehouse],
        (err2) => {
          if (err2) {
            return res.status(500).json(err2);
          }

          const increaseStock =
            "UPDATE stock SET quantity = quantity + ? WHERE product_id=? AND warehouse_id=?";

          db.query(
            increaseStock,
            [quantity, product_id, to_warehouse],
            (err3) => {
              if (err3) {
                return res.status(500).json(err3);
              }

              res.json("Stock Transferred Successfully");
            },
          );
        },
      );
    },
  );
};
