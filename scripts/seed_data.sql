-- Seed data for YourShoes Telegram Bot
-- Run with: sqlite3 data/shop.db < scripts/seed_data.sql

-- Insert sample shoe items
INSERT INTO items (sku, name, description, price, sizes, images, category) VALUES
(
    'NIKE-AIR-001',
    'Nike Air Max 270',
    'Легкі та зручні кросівки Nike Air Max 270 з інноваційною технологією амортизації. Ідеальні для повсякденного носіння та бігу. Дихаючий верх із сітки забезпечує відмінну вентиляцію.',
    2499.00,
    '["38", "39", "40", "41", "42", "43"]',
    '[]',
    'men'
),
(
    'ADIDAS-UB-002',
    'Adidas Ultraboost 22',
    'Преміальні бігові кросівки з революційною підошвою Boost. Забезпечують максимальний комфорт та повернення енергії при кожному кроці. Підходять для тренувань та марафонів.',
    3299.00,
    '["39", "40", "41", "42", "43", "44"]',
    '[]',
    'men'
),
(
    'PUMA-WOMEN-003',
    'Puma Cali Sport Жіночі',
    'Стильні жіночі кросівки Puma Cali Sport у класичному білому кольорі. Ідеально поєднуються з будь-яким casual образом. Комфортна підошва для цілоденного носіння.',
    1899.00,
    '["35", "36", "37", "38", "39", "40"]',
    '[]',
    'women'
);

-- Insert sample promo codes
INSERT INTO promo_codes (code, discount_percent, valid_until, usage_limit, is_active) VALUES
(
    'WELCOME10',
    10.0,
    datetime('now', '+30 days'),
    100,
    1
),
(
    'SUMMER25',
    25.0,
    datetime('now', '+60 days'),
    50,
    1
),
(
    'FIRSTORDER',
    15.0,
    datetime('now', '+90 days'),
    NULL,
    1
);

-- Verify insertion
SELECT 'Items inserted:', COUNT(*) FROM items;
SELECT 'Promo codes inserted:', COUNT(*) FROM promo_codes;

-- Display inserted items
SELECT id, sku, name, price FROM items;