const mysql = require('mysql');

const db = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "meher@2005",
    database: "loan_system"
});

db.connect(err => {
    if (err) throw err;
    console.log("MySQL Connected!");
});

module.exports = db;
