-- ایجاد جدول دسته‌بندی‌ها
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- ایجاد جدول محصولات
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL,
    category_id INTEGER REFERENCES categories(category_id)
);

-- درج داده‌های نمونه
INSERT INTO categories (name, description) VALUES 
('موبایل', 'گوشی‌های هوشمند'),
('لپ‌تاپ', 'لپ‌تاپ‌های اداری و گیمینگ');

INSERT INTO products (name, price, stock, category_id) VALUES
('گوشی شیائومی', 8000000, 50, 1),
('لپ‌تاپ ایسوس', 45000000, 15, 2);