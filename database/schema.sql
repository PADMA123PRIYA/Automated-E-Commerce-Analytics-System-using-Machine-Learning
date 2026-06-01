CREATE DATABASE ecommerce;
USE ecommerce;

CREATE TABLE orders (
    order_id INT,
    product VARCHAR(50),
    city VARCHAR(50),
    price INT,
    date DATETIME
);