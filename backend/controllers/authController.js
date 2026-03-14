const db = require("../config/db");
const bcrypt = require("bcryptjs");

exports.signup = async (req, res) => {
  const { name, email, password } = req.body;

  const hashedPassword = await bcrypt.hash(password, 10);

  const sql = "INSERT INTO users (name,email,password) VALUES (?,?,?)";

  db.query(sql, [name, email, hashedPassword], (err, result) => {
    if (err) {
      return res.status(500).json(err);
    }

    res.json("User Registered");
  });
};

exports.login = (req, res) => {
  const { email, password } = req.body;

  const sql = "SELECT * FROM users WHERE email = ?";

  db.query(sql, [email], async (err, result) => {
    if (err) return res.status(500).json(err);

    if (result.length === 0) {
      return res.status(400).json("User not found");
    }

    const user = result[0];

    const valid = await bcrypt.compare(password, user.password);

    if (!valid) {
      return res.status(400).json("Wrong password");
    }

    res.json({
      message: "Login success",
      user: user,
    });
  });
};
