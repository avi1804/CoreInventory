const db = require("../config/db");

exports.addWarehouse = (req, res) => {
  const { name, location } = req.body;

  const sql = "INSERT INTO warehouses (name,location) VALUES (?,?)";

  db.query(sql, [name, location], (err, result) => {
    if (err) {
      return res.status(500).json(err);
    }

    res.json("Warehouse Added");
  });
};
