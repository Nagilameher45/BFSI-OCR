<?php
$servername = "localhost";
$username = "root";
$password = "meher@2005";
$dbname = "bfsi_ocr_db";

// Create MySQL connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get form data
$username = $_POST['username'];
$email = $_POST['email'];
$password = password_hash($_POST['password'], PASSWORD_DEFAULT); // Secure password
$phone = $_POST['phone'];
$dob = $_POST['dob'];
$gender = $_POST['gender'];

// Insert into database
$sql = "INSERT INTO users (username, password, phone, dob, email, gender) 
        VALUES ('$username', '$password', '$phone', '$dob', '$email', '$gender')";

if ($conn->query($sql) === TRUE) {
    echo "Registration successful!";
} else {
    echo "Error: " . $sql . "<br>" . $conn->error;
}

// Close connection
$conn->close();
?>
