const db = require("../config/db");

exports.addProduct = (req, res) => {
  const { name, sku, category, unit, stock } = req.body;

  const sql =
    "INSERT INTO products (name,sku,category,unit,stock) VALUES (?,?,?,?,?)";

  db.query(sql, [name, sku, category, unit, stock], (err, result) => {
    if (err) {
      return res.status(500).json(err);
    }

    res.json("Product Added");
  });
};

exports.getProducts = (req, res) => {
  const sql = "SELECT * FROM products";

  db.query(sql, (err, result) => {
    if (err) {
      return res.status(500).json(err);
    }

    res.json(result);
  });
};
exports.updateProduct = (req, res) => {
  const id = req.params.id;

  const { name, sku, category, unit, stock } = req.body;

  const sql =
    "UPDATE products SET name=?, sku=?, category=?, unit=?, stock=? WHERE id=?";

  db.query(sql, [name, sku, category, unit, stock, id], (err, result) => {
    if (err) {
      return res.status(500).json(err);
    }

    res.json("Product Updated");
  });
};
exports.deleteProduct = (req, res) => {
  const id = req.params.id;

  const sql = "DELETE FROM products WHERE id=?";

  db.query(sql, [id], (err, result) => {
    if (err) {
      return res.status(500).json(err);
    }

    res.json("Product Deleted");
  });
};
