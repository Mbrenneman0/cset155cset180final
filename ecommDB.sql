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
    color VARCHAR(255) NOT NULL,
    size VARCHAR(50) NOT NULL,
    description VARCHAR(2048) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    warranty_period VARCHAR(255),
    is_removed BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (vendor_id) REFERENCES users(user_id) ON DELETE CASCADE
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
    msg_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB;

-- example data:

INSERT INTO users (name, username, password, email, role) VALUES
-- Admins
('Admin One', 'admin1', 'pass', 'admin1@mail.com', 'Admin'),
('Admin Two', 'admin2', 'pass', 'admin2@mail.com', 'Admin'),

-- Customers
('Alice Smith', 'cust1', 'pass', 'alice@mail.com', 'Customer'),
('Bob Jones', 'cust2', 'pass', 'bob@mail.com', 'Customer'),
('Charlie Brown', 'cust3', 'pass', 'charlie@mail.com', 'Customer'),
('Diana Prince', 'cust4', 'pass', 'diana@mail.com', 'Customer'),
('Ethan Hunt', 'cust5', 'pass', 'ethan@mail.com', 'Customer'),

-- Vendors
('Vendor A', 'vendor1', 'pass', 'vendor1@mail.com', 'Vendor'),
('Vendor B', 'vendor2', 'pass', 'vendor2@mail.com', 'Vendor'),
('Vendor C', 'vendor3', 'pass', 'vendor3@mail.com', 'Vendor');

INSERT INTO products VALUES
('SKU001', 8, 50, 'Laptop', 'Black', '15in', 'Gaming laptop', 1200.00, '1 year', FALSE),
('SKU002', 8, 30, 'Phone', 'White', '6in', 'Smartphone', 800.00, '1 year', FALSE),
('SKU003', 8, 20, 'Tablet', 'Gray', '10in', 'Android tablet', 400.00, '6 months', FALSE),
('SKU004', 8, 100, 'Headphones', 'Black', 'Std', 'Wireless', 150.00, NULL, FALSE),
('SKU005', 9, 75, 'Keyboard', 'Black', 'Full', 'Mechanical', 100.00, NULL, FALSE),
('SKU006', 9, 60, 'Mouse', 'White', 'Std', 'Wireless mouse', 50.00, NULL, FALSE),
('SKU007', 9, 40, 'Monitor', 'Black', '24in', 'LED monitor', 200.00, '1 year', FALSE),
('SKU008', 10, 25, 'Printer', 'White', 'Std', 'Laser printer', 300.00, '1 year', FALSE),
('SKU009', 10, 80, 'USB Drive', 'Blue', '32GB', 'Flash storage', 20.00, NULL, FALSE),
('SKU010', 10, 15, 'Camera', 'Black', 'Std', 'Digital camera', 500.00, '2 years', FALSE),
('SKU011', 10, 2, 'RAM', 'Gold', '4GB', '4GBx1 RAM, extremely valuable and rare', 6000.00, '4 weeks', FALSE);

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

INSERT INTO orders (user_id, status) VALUES
(3, 'Shipped'), -- order 1
(3, 'Pending'), -- order 2
(4, 'Confirmed'), -- order 3
(5, 'Picked Up'), -- order 4
(6, 'Picked Up'), -- order 5
(7, 'Shipped'), -- order 6
(3, 'Confirmed'); -- order 7

INSERT INTO order_items VALUES
-- Order 1 (shipped)
(1, 'SKU001', 1, 1200.00, '1 year'),

-- Order 2 (pending)
(2, 'SKU002', 2, 800.00, '1 year'),

-- Order 3 (confirmed)
(3, 'SKU003', 1, 400.00, '6 months'),

-- Order 4 (Picked Up)
(4, 'SKU004', 1, 150.00, NULL),

-- Order 5 (Picked Up)
(5, 'SKU005', 2, 100.00, NULL),

-- Order 6 (shipped)
(6, 'SKU006', 1, 50.00, NULL),

-- Order 7 (confirmed)
(7, 'SKU007', 1, 200.00, '1 year');

INSERT INTO reviews (user_id, sku, rating, content, rvw_time) VALUES
(3, 'SKU001', 5, 'Great laptop!', NOW()),
(6, 'SKU001', 5, 'It runs Oregon Trail at 7000 frames per second!', NOW()),
(3, 'SKU002', 4, 'Nice phone for the price.', NOW()),
(4, 'SKU002', 3, 'Battery life is terrible.', NOW()),
(4, 'SKU003', 4, 'Pretty good tablet', NOW()),
(5, 'SKU011', 3, "I couldn't find it anywhere else!", NOW()),
(6, 'SKU011', 3, "It's a little overpriced.", NOW()),
(7, 'SKU011', 2, "Thanks Elon, for making RAM so expensive :(", NOW()),
(3, 'SKU011', 5, "I'm pretty sure the diamonds make it faster", NOW());

INSERT INTO complaints (order_num, sku, content, comp_time, type, is_accepted) VALUES
(1, "SKU001", "Product lowkey exploded", NOW(), 'Warranty', TRUE),
(4, "SKU004", "Product arrived late", NOW(), 'Refund', NULL),
(5, "SKU005", "RAM didnt work at all", NOW(), 'Return', FALSE);

INSERT INTO chats (complaint_id, customer_id, support_id) VALUES
(1, 3, 1),
(2, 4, 2);

INSERT INTO messages (chat_id, user_id, content, msg_time) VALUES
(1, 3, 'My product arrived damaged', NOW()),
(1, 1, 'We are reviewing your complaint', NOW()),
(2, 4, 'Order is late', NOW());
