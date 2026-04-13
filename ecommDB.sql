DROP DATABASE ecommDB;
CREATE DATABASE ecommDB;
USE ecommDB;

CREATE TABLE users(
	user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL
);

CREATE TABLE product(
	sku VARCHAR(12) PRIMARY KEY,
    vender_id INT NOT NULL,
    qty INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    color VARCHAR(255) NOT NULL,
    size VARCHAR(50) NOT NULL,
    description VARCHAR(2048) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    warranty_period VARCHAR(255),
    is_removed BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (vender_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE prod_imgs(
	sku VARCHAR(12) NOT NULL,
    img_url VARCHAR(1024),
    FOREIGN KEY (sku) REFERENCES product(sku) ON DELETE CASCADE
);

CREATE TABLE discount(
	sku VARCHAR(12) NOT NULL,
    amount VARCHAR(10) NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
		CHECK (end_date > start_date),
    FOREIGN KEY (sku) REFERENCES product(sku) ON DELETE CASCADE
);

CREATE TABLE cart(
	user_id INT NOT NULL,
    sku VARCHAR(12) NOT NULL,
    qty INT NOT NULL,
    PRIMARY KEY (user_id, sku),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (sku) REFERENCES product(sku) ON DELETE CASCADE
);

CREATE TABLE orders(
	order_num INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    order_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT order_status_value CHECK(status IN ('Pending','Confirmed','Picked Up','Shipped'))
);

CREATE TABLE order_items(
	order_num INT NOT NULL,
    sku VARCHAR(12) NOT NULL,
    qty INT NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    warranty_period VARCHAR(20),
    PRIMARY KEY (order_num, sku),
    FOREIGN KEY (order_num) REFERENCES orders(order_num) ON DELETE CASCADE,
    FOREIGN KEY (sku) REFERENCES product(sku) ON DELETE CASCADE
);

CREATE TABLE review(
	user_id INT NOT NULL,
    sku VARCHAR(12) NOT NULL,
    rating INT NOT NULL 
		CHECK (rating BETWEEN 1 AND 5),
    content VARCHAR(2048) NOT NULL,
    rvw_time DATETIME NOT NULL,
    PRIMARY KEY (user_id, sku),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (sku) REFERENCES product(sku) ON DELETE CASCADE
);

CREATE TABLE complaint(
	complaint_id INT PRIMARY KEY AUTO_INCREMENT,
    order_num INT NOT NULL,
    comp_time DATETIME NOT NULL,
    type VARCHAR(8) NOT NULL,
    is_accepted BOOLEAN,
    FOREIGN KEY (order_num) REFERENCES orders(order_num) ON DELETE CASCADE
);

CREATE TABLE chat(
	chat_id INT PRIMARY KEY AUTO_INCREMENT,
    complaint_id INT NOT NULL,
    customer_id INT NOT NULL,
    support_id INT NOT NULL,
    FOREIGN KEY (complaint_id) REFERENCES complaint(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (support_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE message(
	msg_id INT PRIMARY KEY AUTO_INCREMENT,
	chat_id INT NOT NULL,
    user_id INT NOT NULL,
    content VARCHAR(2048) NOT NULL,
    msg_time DATETIME NOT NULL
);