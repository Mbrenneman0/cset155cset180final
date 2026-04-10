use ecommDB;

INSERT INTO users (name, username, password, email) VALUES
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
('Vendor A', 'vendor1', 'pass', 'vendor1@mail.com', 'Vender'),
('Vendor B', 'vendor2', 'pass', 'vendor2@mail.com', 'Vender'),
('Vendor C', 'vendor3', 'pass', 'vendor3@mail.com', 'Vender');

INSERT INTO product VALUES
('SKU001', 1, 50, 'Laptop', 'Black', '15in', 'Gaming laptop', 1200.00, '1 year', FALSE),
('SKU002', 1, 30, 'Phone', 'White', '6in', 'Smartphone', 800.00, '1 year', FALSE),
('SKU003', 1, 20, 'Tablet', 'Gray', '10in', 'Android tablet', 400.00, '6 months', FALSE),
('SKU004', 1, 100, 'Headphones', 'Black', 'Std', 'Wireless', 150.00, NULL, FALSE),
('SKU005', 2, 75, 'Keyboard', 'Black', 'Full', 'Mechanical', 100.00, NULL, FALSE),
('SKU006', 2, 60, 'Mouse', 'White', 'Std', 'Wireless mouse', 50.00, NULL, FALSE),
('SKU007', 2, 40, 'Monitor', 'Black', '24in', 'LED monitor', 200.00, '1 year', FALSE),
('SKU008', 3, 25, 'Printer', 'White', 'Std', 'Laser printer', 300.00, '1 year', FALSE),
('SKU009', 3, 80, 'USB Drive', 'Blue', '32GB', 'Flash storage', 20.00, NULL, FALSE),
('SKU010', 3, 15, 'Camera', 'Black', 'Std', 'Digital camera', 500.00, '2 years', FALSE);

INSERT INTO prod_imgs VALUES
('SKU001', 'img1.jpg'),
('SKU002', 'img2.jpg'),
('SKU003', 'img3.jpg'),
('SKU004', 'img4.jpg');

-- UNTIMED 
INSERT INTO discount VALUES
('SKU001', '10%', '2000-01-01', '2099-12-31'),
('SKU002', '$5.00', '2000-01-01', '2099-12-31');

-- TIMED 
INSERT INTO discount VALUES
('SKU003', '$15.00', '2026-01-01', '2026-12-31'),
('SKU004', '5%', '2026-03-01', '2026-06-01');

INSERT INTO cart VALUES
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

INSERT INTO review VALUES
(3, 'SKU001', 5, 'Great laptop!', NOW()),
(4, 'SKU003', 4, 'Pretty good tablet', NOW());

INSERT INTO complaint (order_num, comp_time, type, is_accepted) VALUES
(1, NOW(), 'damage', TRUE),
(4, NOW(), 'late', FALSE);

INSERT INTO chat (complaint_id, customer_id, support_id) VALUES
(1, 3, 1),
(2, 4, 2);

INSERT INTO message (chat_id, user_id, content, msg_time) VALUES
(1, 3, 'My product arrived damaged', NOW()),
(1, 1, 'We are reviewing your complaint', NOW()),
(2, 4, 'Order is late', NOW());




SELECT * FROM users;
SELECT * FROM product;
SELECT * FROM prod_imgs;
SELECT * FROM discount;
SELECT * FROM cart;
SELECT * FROM orders;
SELECT * FROM order_items;
SELECT * FROM review;
SELECT * FROM complaint;
SELECT * FROM chat;
SELECT * FROM message;


INSERT INTO users (name, username, password, email) VALUES ('test', 'aaaa', 'pass', 'alice@mail.com', 'Customer')



