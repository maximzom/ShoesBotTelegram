# 👟 YourShoes Telegram Bot

Повнофункціональний Telegram-бот для продажу взуття з адмін-панеллю, системою замовлень та інтеграцією платежів.

## 📋 Зміст

- [Особливості](#особливості)
- [Технології](#технології)
- [Швидкий старт](#швидкий-старт)
- [Структура проекту](#структура-проекту)
- [Налаштування](#налаштування)
- [Команди бота](#команди-бота)
- [База даних](#база-даних)
- [Тестування](#тестування)
- [Розгортання](#розгортання)
- [Безпека](#безпека)

## ✨ Особливості

- 🛍️ Інтерактивний каталог з фото та описами
- 📦 Повний цикл оформлення замовлення
- 👤 Система стану користувача (збереження сесії)
- 🔐 Адмін-панель з перевіркою прав доступу
- 💳 Інтеграція з Telegram Payments (stub + ready-to-use)
- 📊 Експорт замовлень у CSV
- 🎟️ Система промокодів
- 📝 Збір відгуків користувачів
- 🌐 Мультимовна підтримка (скелет)
- 🔒 Rate limiting захист
- 📈 Логування всіх дій
- ✅ Валідація даних (ціни, телефони, розміри)
- 💾 Persistent storage (відновлення після перезапуску)

## 🛠 Технології

- **Python 3.10+**
- **pyTelegramBotAPI** (Telebot) - основний фреймворк
- **SQLAlchemy** - ORM для роботи з БД
- **SQLite** - база даних за замовчуванням
- **pytest** - тестування
- **python-dotenv** - керування env змінними

## 🚀 Швидкий старт

### 1. Клонування та встановлення

```bash
# Клонуйте репозиторій
git clone <your-repo-url>
cd shoe_bot

# Створіть віртуальне середовище
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate  # Windows

# Встановіть залежності
pip install -r requirements.txt
```

### 2. Налаштування змінних середовища

```bash
# Скопіюйте приклад конфігурації
cp .env.example .env

# Відредагуйте .env файл
nano .env
```

Приклад `.env`:
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789,987654321
DB_URL=sqlite:///data/shop.db
PAYMENT_PROVIDER_TOKEN=
LOG_LEVEL=INFO
RATE_LIMIT_MESSAGES=20
RATE_LIMIT_WINDOW=60
```

### 3. Ініціалізація бази даних

```bash
# Створіть директорію для БД
mkdir -p data

# Ініціалізуйте схему
python -c "from models.db import init_db; init_db()"

# Або використайте міграційний скрипт
python scripts/migrate.py
```

### 4. Додайте тестові товари

```bash
# Через SQL
sqlite3 data/shop.db < scripts/seed_data.sql

# Або через адмін-команди бота після запуску
```

### 5. Запуск бота

```bash
python bot.py
```

## 📁 Структура проекту

```
shoe_bot/
├── README.md                    # Ця документація
├── requirements.txt             # Python залежності
├── .env.example                 # Приклад конфігурації
├── bot.py                       # Точка входу
├── config.py                    # Конфігурація
│
├── models/                      # Моделі даних
│   ├── __init__.py
│   ├── db.py                   # Підключення до БД
│   └── schemas.py              # SQLAlchemy моделі
│
├── handlers/                    # Обробники команд
│   ├── __init__.py
│   ├── start.py                # /start, /help, /info
│   ├── catalog.py              # /catalog, перегляд товарів
│   ├── orders.py               # /order, оформлення замовлення
│   ├── admin.py                # /admin, керування
│   └── feedback.py             # /feedback
│
├── services/                    # Бізнес-логіка
│   ├── __init__.py
│   ├── product_service.py      # Робота з товарами
│   ├── order_service.py        # Обробка замовлень
│   ├── user_service.py         # Користувачі
│   ├── payment_service.py      # Платежі
│   └── promo_service.py        # Промокоди
│
├── utils/                       # Допоміжні утиліти
│   ├── __init__.py
│   ├── validators.py           # Валідація даних
│   ├── keyboards.py            # Клавіатури
│   ├── helpers.py              # Загальні функції
│   ├── rate_limiter.py         # Rate limiting
│   └── locales.py              # Мовні ресурси
│
├── data/                        # Дані
│   └── shop.db                 # SQLite база даних
│
├── logs/                        # Логи
│   └── bot.log
│
├── tests/                       # Тести
│   ├── __init__.py
│   ├── test_validators.py
│   ├── test_order_service.py
│   └── test_handlers.py
│
├── scripts/                     # Скрипти
│   ├── migrate.py              # Міграції
│   ├── seed_data.sql           # Тестові дані
│   ├── backup_orders.py        # Бекап замовлень
│   └── export_csv.py           # Експорт у CSV
│
└── deploy/                      # Розгортання
    ├── deploy_railway.md
    ├── deploy_render.md
    ├── deploy_pythonanywhere.md
    ├── deploy_hetzner.md
    └── systemd/
        └── shoe_bot.service
```

## ⚙️ Налаштування

### Отримання Bot Token

1. Знайдіть [@BotFather](https://t.me/botfather) у Telegram
2. Відправте `/newbot`
3. Дайте ім'я вашому боту
4. Скопіюйте токен у `.env` файл

### Налаштування адміністраторів

Дізнайтесь свій Telegram ID:
- Напишіть [@userinfobot](https://t.me/userinfobot)
- Скопіюйте ID у `ADMIN_IDS` через кому

### База даних

**SQLite (за замовчуванням):**
```env
DB_URL=sqlite:///data/shop.db
```

**PostgreSQL (опціонально):**
```env
DB_URL=postgresql://user:password@localhost:5432/shoebot
```

Для PostgreSQL встановіть додатково:
```bash
pip install psycopg2-binary
```

## 🤖 Команди бота

### Користувацькі команди

| Команда | Опис |
|---------|------|
| `/start` | Початкове привітання та головне меню |
| `/help` | Список команд та їх опис |
| `/info` | Інформація про магазин |
| `/catalog` | Каталог товарів |
| `/order` | Почати нове замовлення |
| `/feedback` | Залишити відгук |
| `/hello` | Дружнє привітання |

### Адмін-команди

| Команда | Опис |
|---------|------|
| `/admin` | Відкрити адмін-панель |
| `/add_item` | Додати новий товар |
| `/remove_item` | Видалити товар |
| `/orders` | Переглянути замовлення |
| `/promo_add` | Додати промокод |
| `/export_orders` | Експортувати замовлення в CSV |

## 🗄️ База даних

### Схема

```sql
-- Користувачі
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    language TEXT DEFAULT 'uk',
    state TEXT,
    state_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Товари
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    sizes TEXT NOT NULL,  -- JSON: ["38", "39", "40"]
    images TEXT,          -- JSON: ["file_id_1", "file_id_2"]
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Кошики
CREATE TABLE carts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Позиції в кошику
CREATE TABLE cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    size TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (cart_id) REFERENCES carts(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

-- Замовлення
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    total REAL NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending/confirmed/paid/shipped/cancelled
    delivery_method TEXT,
    address TEXT,
    phone TEXT,
    promo_code TEXT,
    discount REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Позиції замовлення
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    size TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

-- Відгуки
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Промокоди
CREATE TABLE promo_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    discount_percent REAL NOT NULL,
    valid_until TIMESTAMP,
    usage_limit INTEGER,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Міграція SQLite → PostgreSQL

```bash
# 1. Експортуйте дані
python scripts/export_sqlite_to_sql.py

# 2. Створіть PostgreSQL базу
createdb shoebot

# 3. Імпортуйте схему
psql shoebot < scripts/postgres_schema.sql

# 4. Імпортуйте дані
psql shoebot < scripts/exported_data.sql
```

## 🧪 Тестування

```bash
# Запустити всі тести
pytest

# З покриттям коду
pytest --cov=. --cov-report=html

# Конкретний тест
pytest tests/test_validators.py -v

# З виводом print
pytest -s
```

### Приклад тестів

```python
# Тест валідації
def test_phone_validation():
    assert validate_phone("+380501234567") == True
    assert validate_phone("invalid") == False

# Тест розрахунку суми замовлення
def test_order_total_calculation():
    items = [{"price": 1000, "quantity": 2}]
    assert calculate_total(items) == 2000

# Інтеграційний тест
def test_catalog_handler(mock_bot):
    message = create_mock_message("/catalog")
    catalog_handler(message)
    assert mock_bot.send_message.called
```

## 🚢 Розгортання

### Опція 1: Railway (Рекомендовано для швидкого тестування)

**Переваги:** Безкоштовний тир, автоматичне розгортання з Git, прості env змінні

```bash
# 1. Зареєструйтесь на Railway.app
# 2. Створіть новий проект
# 3. Підключіть GitHub репозиторій
# 4. Додайте змінні середовища (Settings → Variables):
#    - BOT_TOKEN
#    - ADMIN_IDS
#    - DB_URL=sqlite:///data/shop.db
# 5. Railway автоматично розгорне бота

# Для персистентного SQLite додайте Volume:
# Settings → Volumes → Add Volume → /app/data
```

Детальна інструкція: [deploy/deploy_railway.md](deploy/deploy_railway.md)

### Опція 2: Render (Безкоштовний Postgres)

**Переваги:** Безкоштовна PostgreSQL база, web dashboard

```bash
# 1. Зареєструйтесь на Render.com
# 2. Створіть PostgreSQL базу (Database → New PostgreSQL)
# 3. Створіть Background Worker (New → Background Worker)
# 4. Підключіть GitHub
# 5. Встановіть Build Command: pip install -r requirements.txt
# 6. Встановіть Start Command: python bot.py
# 7. Додайте env змінні включно з Postgres connection string
```

Детальна інструкція: [deploy/deploy_render.md](deploy/deploy_render.md)

### Опція 3: PythonAnywhere (Найпростіше для початківців)

**Переваги:** Проста настройка, веб-консоль

```bash
# 1. Зареєструйтесь на PythonAnywhere.com
# 2. Відкрийте Bash консоль
# 3. Клонуйте проект
git clone <your-repo>
cd shoe_bot

# 4. Створіть virtualenv
mkvirtualenv --python=/usr/bin/python3.10 shoebot
pip install -r requirements.txt

# 5. Налаштуйте .env файл
nano .env

# 6. Запустіть бота
python bot.py

# 7. Налаштуйте always-on task (платна опція)
# або використайте cron для перезапуску
```

Детальна інструкція: [deploy/deploy_pythonanywhere.md](deploy/deploy_pythonanywhere.md)

### Опція 4: Hetzner Cloud VPS (Найкраще для продакшну)

**Переваги:** Найдешевший стабільний VPS (~€4/міс), повний контроль

```bash
# 1. Створіть VPS на Hetzner Cloud
# 2. Підключіться через SSH
ssh root@your-server-ip

# 3. Встановіть Python та залежності
apt update && apt upgrade -y
apt install python3.10 python3.10-venv python3-pip git sqlite3 -y

# 4. Створіть користувача
adduser shoebot
su - shoebot

# 5. Клонуйте проект
git clone <your-repo>
cd shoe_bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Налаштуйте .env
nano .env

# 7. Створіть systemd service (як root)
exit
cp /home/shoebot/shoe_bot/deploy/systemd/shoe_bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable shoe_bot
systemctl start shoe_bot

# 8. Перевірте статус
systemctl status shoe_bot

# 9. Логи
journalctl -u shoe_bot -f
```

Детальна інструкція: [deploy/deploy_hetzner.md](deploy/deploy_hetzner.md)

### Webhook (опціонально, замість polling)

Для використання webhook потрібен HTTPS endpoint:

```python
# В bot.py
if config.USE_WEBHOOK:
    bot.remove_webhook()
    bot.set_webhook(
        url=f"{config.WEBHOOK_URL}/{config.BOT_TOKEN}",
        certificate=open('webhook_cert.pem', 'r')  # Для self-signed
    )
```

Отримати безкоштовний SSL:
- Cloudflare Tunnel
- ngrok (для тестування)
- Let's Encrypt (для VPS з доменом)

## 🔒 Безпека

### Обов'язкові заходи

1. **Ніколи не комітьте `.env` файл**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Приховуйте токени в логах**
   ```python
   # Фільтруйте чутливі дані
   logger.info(f"User {user_id} ordered")  # ✅
   logger.info(f"Token: {token}")  # ❌
   ```

3. **Валідуйте всі вхідні дані**
   ```python
   if not validate_phone(phone):
       bot.reply_to(message, "Неправильний формат телефону")
       return
   ```

4. **Перевіряйте права адміністратора**
   ```python
   def is_admin(user_id):
       return user_id in config.ADMIN_IDS
   ```

5. **Rate limiting**
   ```python
   @rate_limit(max_calls=20, period=60)
   def handle_message(message):
       ...
   ```

6. **SQL Injection захист**
   - Використовуйте ORM (SQLAlchemy)
   - Ніколи не вставляйте user input напряму в SQL

7. **Маскуйте PII в логах**
   ```python
   phone_masked = phone[:3] + "****" + phone[-2:]
   ```

### Рекомендації

- Регулярно оновлюйте залежності: `pip install --upgrade -r requirements.txt`
- Використовуйте HTTPS для webhook
- Налаштуйте backup бази даних: `scripts/backup_orders.py`
- Моніторинг: інтеграція з Sentry для tracking помилок

## 📊 Моніторинг та логування

### Логування

Бот логує всі важливі події:

```python
# logs/bot.log
2024-01-15 10:30:45 INFO User 123456 started bot
2024-01-15 10:31:12 INFO User 123456 viewed catalog
2024-01-15 10:32:05 INFO Order #ORD-20240115-001 created by user 123456
2024-01-15 10:32:06 INFO Admin 987654 notified about order #ORD-20240115-001
```

### Експорт даних

```bash
# Експорт всіх замовлень
python scripts/export_csv.py --output orders.csv

# Бекап бази даних
python scripts/backup_orders.py --date 2024-01-15
```

## 🎯 Швидка перевірка функціоналу (для екзаменаторів)

### Чек-ліст тестування

- [ ] **Базові команди**
  - [ ] `/start` - показує привітання українською
  - [ ] `/help` - список команд
  - [ ] `/info` - інформація про магазин

- [ ] **Каталог**
  - [ ] `/catalog` - показує товари з інлайн-кнопками
  - [ ] Натискання на товар показує деталі
  - [ ] Фото товару відображається

- [ ] **Замовлення**
  - [ ] Вибір розміру через кнопки
  - [ ] Вибір кількості
  - [ ] Вибір способу доставки
  - [ ] Введення адреси (валідується)
  - [ ] Введення телефону (валідується формат)
  - [ ] Підтвердження замовлення
  - [ ] Адміну приходить повідомлення

- [ ] **Адмін-функції**
  - [ ] `/admin` доступний тільки адмінам
  - [ ] `/add_item` додає товар з валідацією ціни
  - [ ] `/remove_item` видаляє товар
  - [ ] `/orders` показує список замовлень
  - [ ] Можна змінити статус замовлення

- [ ] **Додаткові функції**
  - [ ] `/feedback` зберігає відгук та пересилає адміну
  - [ ] Промокод застосовується до замовлення
  - [ ] Експорт замовлень у CSV працює
  - [ ] Логи записуються у файл

- [ ] **Персистентність**
  - [ ] Перезапуск бота зберігає стан користувача
  - [ ] База даних зберігає всі дані

## 🐛 Troubleshooting

### Проблема: Бот не відповідає

```bash
# Перевірте токен
python -c "from config import BOT_TOKEN; print('Token OK' if BOT_TOKEN else 'Token missing')"

# Перевірте з'єднання
python -c "import telebot; bot = telebot.TeleBot('YOUR_TOKEN'); print(bot.get_me())"
```

### Проблема: База даних не створюється

```bash
# Створіть директорію вручну
mkdir -p data

# Ініціалізуйте БД
python -c "from models.db import init_db; init_db()"
```

### Проблема: Адмін-команди не працюють

```bash
# Перевірте ADMIN_IDS
echo $ADMIN_IDS

# Дізнайтесь свій ID через @userinfobot
```

### Проблема: Помилки при встановленні залежностей

```bash
# Оновіть pip
pip install --upgrade pip

# Встановіть по одній
pip install pyTelegramBotAPI
pip install SQLAlchemy
pip install python-dotenv
```

## 📝 TODO для продакшн використання

- [ ] Інтеграція справжнього payment provider (Stripe/LiqPay)
- [ ] Додати webhook замість polling для кращої продуктивності
- [ ] Налаштувати Sentry для моніторингу помилок
- [ ] Додати Redis для кешування та rate limiting
- [ ] Реалізувати повну мультимовність
- [ ] Додати analytics dashboard
- [ ] Налаштувати CI/CD pipeline
- [ ] Додати більше тестів (покриття >80%)
- [ ] Оптимізувати запити до БД (індекси)
- [ ] Додати backup автоматизацію

## 📞 Підтримка

Питання? Проблеми? Створіть Issue у GitHub репозиторії.

## 📄 Ліцензія

MIT License - використовуйте вільно для навчальних та комерційних цілей.

---

**Зроблено з ❤️ для курсу Python розробки**

