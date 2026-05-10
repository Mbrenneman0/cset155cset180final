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
) ENGINE = InnoDB;

CREATE TABLE products(
	sku VARCHAR(12) PRIMARY KEY,
    vendor_id INT NOT NULL,
    qty INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    color VARCHAR(255) NOT NULL,
    size VARCHAR(50) NOT NULL,
    description VARCHAR(2048) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    warranty_period VARCHAR(255),
    is_removed BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (vendor_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT category_values 
        CHECK(category IN (
            'Electronics',
            'Food and Beverage',
            'Decor',
            'Tools',
            'Sports',
            'Furniture',
            'Toys'
            ))
) ENGINE = InnoDB;

CREATE TABLE prod_imgs(
    img_index INT PRIMARY KEY AUTO_INCREMENT,
	sku VARCHAR(12) NOT NULL,
    img_url VARCHAR(1024),
    FOREIGN KEY (sku) REFERENCES products(sku) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE discounts(
	sku VARCHAR(12) NOT NULL,
    amount VARCHAR(10) NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
		CHECK (end_date > start_date),
    FOREIGN KEY (sku) REFERENCES products(sku) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE carts(
	user_id INT NOT NULL,
    sku VARCHAR(12) NOT NULL,
    qty INT NOT NULL,
    PRIMARY KEY (user_id, sku),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (sku) REFERENCES products(sku) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE orders(
	order_num INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    order_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT order_status_value CHECK(status IN ('Pending','Confirmed','Picked Up','Shipped'))
) ENGINE = InnoDB;

CREATE TABLE order_items(
	order_num INT NOT NULL,
    sku VARCHAR(12) NOT NULL,
    qty INT NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    warranty_period VARCHAR(20),
    PRIMARY KEY (order_num, sku),
    FOREIGN KEY (order_num) REFERENCES orders(order_num) ON DELETE CASCADE,
    FOREIGN KEY (sku) REFERENCES products(sku) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE reviews(
    review_id INT PRIMARY KEY AUTO_INCREMENT,
	user_id INT NOT NULL,
    sku VARCHAR(12) NOT NULL,
    rating INT NOT NULL 
		CHECK (rating BETWEEN 1 AND 5),
    content VARCHAR(2048) NOT NULL,
    rvw_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (sku) REFERENCES products(sku) ON DELETE CASCADE,
    CONSTRAINT unique_review UNIQUE (user_id, sku)
) ENGINE = InnoDB;

CREATE TABLE complaints(
	complaint_id INT PRIMARY KEY AUTO_INCREMENT,
    order_num INT NOT NULL,
    sku VARCHAR(12) NOT NULL,
    content VARCHAR(2048),
    comp_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    type VARCHAR(8) NOT NULL,
    is_accepted BOOLEAN DEFAULT NULL,
    FOREIGN KEY (order_num) REFERENCES orders(order_num) ON DELETE CASCADE,
    FOREIGN KEY (sku) REFERENCES products(sku) ON DELETE CASCADE,
    CONSTRAINT complaint_type_value CHECK(type IN ('Return','Refund','Warranty'))
) ENGINE = InnoDB;

CREATE TABLE chats(
	chat_id INT PRIMARY KEY AUTO_INCREMENT,
    complaint_id INT,
    customer_id INT NOT NULL,
    support_id INT NOT NULL,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (support_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE TABLE messages(
	msg_id INT PRIMARY KEY AUTO_INCREMENT,
	chat_id INT NOT NULL,
    user_id INT NOT NULL,
    content VARCHAR(2048) NOT NULL,
    msg_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE = InnoDB;

-- example data:

INSERT INTO users (name, username, password, email, role) VALUES
('Admin One', 'admin1', 'pass', 'admin1@mail.com', 'Admin'),
('Admin Two', 'admin2', 'pass', 'admin2@mail.com', 'Admin'),

('Alice Smith', 'cust1', 'pass', 'alice@mail.com', 'Customer'),
('Bob Jones', 'cust2', 'pass', 'bob@mail.com', 'Customer'),
('Charlie Brown', 'cust3', 'pass', 'charlie@mail.com', 'Customer'),
('Diana Prince', 'cust4', 'pass', 'diana@mail.com', 'Customer'),
('Ethan Hunt', 'cust5', 'pass', 'ethan@mail.com', 'Customer'),

('Vendor A', 'vendor1', 'pass', 'vendor1@mail.com', 'Vendor'),
('Vendor B', 'vendor2', 'pass', 'vendor2@mail.com', 'Vendor'),
('Vendor C', 'vendor3', 'pass', 'vendor3@mail.com', 'Vendor');

INSERT INTO products VALUES
('SKU001', 8, 50, 'Laptop', 'Electronics', 'Black', '15in', 'Gaming laptop', 1200.00, '1 year', FALSE),
('SKU002', 8, 30, 'Phone', 'Electronics', 'White', '6in', 'Smartphone', 800.00, '1 year', FALSE),
('SKU003', 8, 20, 'Tablet', 'Electronics', 'Gray', '10in', 'Android tablet', 400.00, '6 months', FALSE),
('SKU004', 8, 100, 'Headphones', 'Electronics', 'Black', 'Std', 'Wireless', 150.00, NULL, FALSE),
('SKU005', 9, 75, 'Keyboard', 'Electronics', 'Black', 'Full', 'Mechanical', 100.00, NULL, FALSE),
('SKU006', 9, 60, 'Mouse', 'Electronics', 'White', 'Std', 'Wireless mouse', 50.00, NULL, FALSE),
('SKU007', 9, 40, 'Monitor', 'Electronics', 'Black', '24in', 'LED monitor', 200.00, '1 year', FALSE),
('SKU008', 10, 25, 'Printer', 'Electronics', 'White', 'Std', 'Laser printer', 300.00, '1 year', FALSE),
('SKU009', 10, 80, 'USB Drive', 'Electronics', 'Blue', '32GB', 'Flash storage', 20.00, NULL, FALSE),
('SKU010', 10, 15, 'Camera', 'Electronics', 'Black', 'Std', 'Digital camera', 500.00, '2 years', FALSE),
('SKU011', 10, 2, 'RAM', 'Electronics', 'Gold', '4GB', '4GBx1 RAM, extremely valuable and rare', 6000.00, '4 weeks', FALSE);

INSERT INTO prod_imgs (sku, img_url) VALUES
('SKU001', 'images/prod-imgs/vendor1/sku001-1.png'),
('SKU002', 'images/prod-imgs/vendor1/sku002-1.png'),
('SKU003', 'images/prod-imgs/vendor1/sku003-1.png'),
('SKU004', 'images/prod-imgs/vendor1/sku004-1.png'),
('SKU005', 'images/prod-imgs/vendor2/sku005-1.png'),
('SKU006', 'images/prod-imgs/vendor2/sku006-1.png'),
('SKU007', 'images/prod-imgs/vendor2/sku007-1.png'),
('SKU008', 'images/prod-imgs/vendor3/sku008-1.png'),
('SKU009', 'images/prod-imgs/vendor3/sku009-1.png'),
('SKU010', 'images/prod-imgs/vendor3/sku010-1.png'),
('SKU010', 'images/prod-imgs/vendor3/sku010-2.png'),
('SKU011', 'images/prod-imgs/vendor3/sku011-1.png');

-- UNTIMED 
INSERT INTO discounts VALUES
('SKU001', '10%', '2000-01-01', '2099-12-31'),
('SKU002', '$5.00', '2000-01-01', '2099-12-31');

-- TIMED 
INSERT INTO discounts VALUES
('SKU003', '$15.00', '2026-01-01', '2026-12-31'),
('SKU004', '5%', '2026-03-01', '2026-06-01');

INSERT INTO carts VALUES
(3, 'SKU001', 1),
(3, 'SKU002', 2),

(4, 'SKU003', 1),
(4, 'SKU005', 1),

(5, 'SKU006', 3);


-- Additional Orders Across Several Months
INSERT INTO orders (user_id, order_time, status) VALUES
(3, NOW(), 'Shipped'),
(3, NOW(), 'Pending'),
(4, NOW(), 'Confirmed'),
(5, NOW(), 'Picked Up'),
(6, NOW(), 'Picked Up'),
(7, NOW(), 'Shipped'),
(3, NOW(), 'Confirmed'),

(3, '2026-01-04 10:15:00', 'Shipped'),
(4, '2026-01-08 12:30:00', 'Shipped'),
(5, '2026-01-10 09:45:00', 'Picked Up'),
(6, '2026-01-15 18:20:00', 'Confirmed'),
(7, '2026-01-22 14:00:00', 'Pending'),

(3, '2026-02-02 11:10:00', 'Shipped'),
(4, '2026-02-05 15:22:00', 'Shipped'),
(5, '2026-02-09 17:40:00', 'Picked Up'),
(6, '2026-02-14 20:00:00', 'Confirmed'),
(7, '2026-02-20 13:12:00', 'Shipped'),

(3, '2026-03-03 08:15:00', 'Shipped'),
(4, '2026-03-07 16:42:00', 'Confirmed'),
(5, '2026-03-11 12:55:00', 'Picked Up'),
(6, '2026-03-16 19:30:00', 'Shipped'),
(7, '2026-03-21 09:20:00', 'Pending'),

(3, '2026-04-01 10:05:00', 'Shipped'),
(4, '2026-04-06 11:15:00', 'Confirmed'),
(5, '2026-04-12 13:00:00', 'Picked Up'),
(6, '2026-04-18 18:10:00', 'Shipped'),
(7, '2026-04-24 20:30:00', 'Confirmed'),

(3, '2026-05-02 09:00:00', 'Shipped'),
(4, '2026-05-05 14:45:00', 'Confirmed'),
(5, '2026-05-10 12:20:00', 'Picked Up'),
(6, '2026-05-15 17:35:00', 'Pending'),
(7, '2026-05-20 21:10:00', 'Shipped');



INSERT INTO order_items VALUES
(1, 'SKU001', 1, 1200.00, '1 year'),

(2, 'SKU002', 2, 800.00, '1 year'),

(3, 'SKU003', 1, 400.00, '6 months'),

(4, 'SKU004', 1, 150.00, NULL),

(5, 'SKU005', 2, 100.00, NULL),

(6, 'SKU006', 1, 50.00, NULL),

(7, 'SKU007', 1, 200.00, '1 year'),

(8, 'SKU001', 1, 1200.00, '1 year'),
(8, 'SKU004', 2, 150.00, NULL),

(9, 'SKU002', 1, 800.00, '1 year'),

(10, 'SKU005', 1, 100.00, NULL),
(10, 'SKU006', 2, 50.00, NULL),

(11, 'SKU003', 1, 400.00, '6 months'),

(12, 'SKU007', 1, 200.00, '1 year'),

(13, 'SKU001', 1, 1200.00, '1 year'),
(13, 'SKU009', 3, 20.00, NULL),

(14, 'SKU010', 1, 500.00, '2 years'),

(15, 'SKU005', 2, 100.00, NULL),

(16, 'SKU006', 1, 50.00, NULL),
(16, 'SKU004', 1, 150.00, NULL),

(17, 'SKU011', 1, 6000.00, '4 weeks'),

(18, 'SKU002', 1, 800.00, '1 year'),

(19, 'SKU003', 2, 400.00, '6 months'),

(20, 'SKU005', 1, 100.00, NULL),

(21, 'SKU001', 1, 1200.00, '1 year'),
(21, 'SKU007', 2, 200.00, '1 year'),

(22, 'SKU008', 1, 300.00, '1 year'),

(23, 'SKU004', 3, 150.00, NULL),

(24, 'SKU002', 1, 800.00, '1 year'),

(25, 'SKU009', 5, 20.00, NULL),

(26, 'SKU010', 1, 500.00, '2 years'),

(27, 'SKU006', 2, 50.00, NULL),

(28, 'SKU001', 1, 1200.00, '1 year'),

(29, 'SKU011', 1, 6000.00, '4 weeks'),

(30, 'SKU005', 3, 100.00, NULL),

(31, 'SKU003', 1, 400.00, '6 months'),

(32, 'SKU007', 1, 200.00, '1 year');


INSERT INTO reviews (user_id, sku, rating, content, rvw_time) VALUES
(4, 'SKU004', 5, 'Very comfortable headphones.', '2026-01-10 12:00:00'),
(5, 'SKU005', 4, 'Keyboard feels great.', '2026-01-16 15:30:00'),
(6, 'SKU006', 5, 'Mouse battery lasts forever.', '2026-02-02 18:20:00'),
(7, 'SKU010', 4, 'Camera quality is solid.', '2026-02-22 10:10:00'),
(3, 'SKU009', 5, 'Cheap and useful.', '2026-03-05 08:50:00'),
(4, 'SKU008', 3, 'Printer setup was annoying.', '2026-03-28 17:10:00'),
(5, 'SKU007', 5, 'Monitor looks amazing.', '2026-04-11 14:25:00'),
(6, 'SKU003', 4, 'Tablet is good for school.', '2026-04-25 11:40:00'),
(7, 'SKU004', 2, 'Stopped working after a month.', '2026-05-03 09:15:00');


INSERT INTO complaints (order_num, sku, content, comp_time, type, is_accepted) VALUES
(14, 'SKU010', 'Lens arrived scratched.', '2026-02-25 13:00:00', 'Refund', TRUE),

(21, 'SKU001', 'Laptop overheats while gaming.', '2026-03-20 19:45:00', 'Warranty', NULL),

(27, 'SKU006', 'Mouse disconnects randomly.', '2026-05-04 10:30:00', 'Return', FALSE);


INSERT INTO chats (complaint_id, customer_id, support_id) VALUES
(1, 7, 1),
(2, 6, 2),
(3, 7, 1);


INSERT INTO messages (chat_id, user_id, content, msg_time) VALUES
(1, 7, 'The camera lens was scratched on arrival.', '2026-02-25 13:10:00'),
(1, 1, 'We are reviewing your refund request.', '2026-02-25 14:00:00'),

(2, 6, 'Laptop gets extremely hot during use.', '2026-03-20 20:00:00'),
(2, 2, 'Can you upload photos of the issue?', '2026-03-20 20:15:00'),

(3, 7, 'Mouse disconnects every few minutes.', '2026-05-04 11:00:00'),
(3, 1, 'Return request has been denied.', '2026-05-04 12:30:00');