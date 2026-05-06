# 🛰️ OLXRadar

Миттєві сповіщення про нові оголошення на OLX прямо у ваш Telegram або на Email. Більше не потрібно оновлювати сторінку вручну — бот зробить це за вас!

![OLXRadar Header](https://i.imgur.com/umVlxwV.jpeg)

## ✨ Особливості

- 🚀 **Миттєвість**: Перевірка нових оголошень за розкладом.
- 📱 **Telegram**: Сповіщення в один або декілька чатів одночасно.
- 📧 **Email**: Підтримка Gmail для отримання звітів на пошту.
- 🐋 **Docker**: Легкий запуск через Docker Compose.
- 📄 **Гнучкість**: Налаштування декількох пошукових запитів одночасно.

---

## 🛠️ Швидкий запуск (Docker) — Рекомендовано

Найпростіший спосіб запустити проект — використовувати Docker.

1.  **Клонуйте репозиторій**:
    ```bash
    git clone https://github.com/yourusername/OLXRadar.git
    cd OLXRadar
    ```

2.  **Налаштуйте середовище**:
    Створіть файл `.env` та заповніть його:
    ```env
    TELEGRAM_BOT_TOKEN="ваш_токен"
    TELEGRAM_CHAT_ID="ваш_chat_id" # Основний ID (необов'язково, якщо є chat_ids.txt)
    
    # Для Email (необов'язково)
    EMAIL_SENDER="your-email@gmail.com"
    EMAIL_RECEIVER="receiver-email@example.com"
    EMAIL_APP_PASSWORD="your-app-password"
    ```

3.  **Додайте посилання для відстеження**:
    Створіть файл `target_urls.txt` (використовуйте `target_urls.txt.example` як шаблон) та додайте посилання на пошук OLX (одне на рядок).

4.  **Запустіть контейнер**:
    ```bash
    docker-compose up -d
    ```

---

## 🐍 Локальний запуск (Python)

Якщо ви не використовуєте Docker:

1.  **Встановіть залежності**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # На Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Налаштуйте конфігураційні файли**:
    - Скопіюйте приклади: `cp target_urls.txt.example target_urls.txt` та `cp chat_ids.txt.example chat_ids.txt`.
    - Заповніть `.env`.

3.  **Запустіть скрипт**:
    ```bash
    python main.py
    ```

---

## ⚙️ Налаштування

### Telegram Бот
1. Створіть бота через [@BotFather](https://t.me/BotFather) та отримайте **Token**.
2. Щоб отримати свій **Chat ID**, напишіть боту [@userinfobot](https://t.me/userinfobot).
3. Якщо потрібно надсилати сповіщення декільком людям, додайте їхні ID у файл `chat_ids.txt`.

### Gmail SMTP (для Email)
1. Увімкніть **Двофакторну автентифікацію** у вашому Google акаунті.
2. Створіть **Пароль додатка** (App Password) у розділі [Безпека](https://myaccount.google.com/security).
3. Використовуйте цей пароль у полі `EMAIL_APP_PASSWORD`.

### Як отримати URL для відстеження
1. Перейдіть на [olx.ua](https://www.olx.ua/).
2. Введіть пошуковий запит, виберіть фільтри (ціна, район, стан тощо).
3. Скопіюйте URL з адресного рядка браузера.
4. Вставте цей URL у `target_urls.txt`.

---

## 🗓️ Автоматизація (Cron / Task Scheduler)

Якщо ви запускаєте скрипт без Docker, налаштуйте виконання за розкладом:

**Linux (Cron)**:
```bash
*/15 * * * * /path/to/OLXRadar/venv/bin/python /path/to/OLXRadar/main.py
```

**Windows**:
Використовуйте "Task Scheduler" (Планувальник завдань) для запуску `python main.py` кожні 15-30 хвилин.

---

## 🔒 Безпека та Приватність

- Файли `.env`, `chat_ids.txt` та `target_urls.txt` додані до `.gitignore`, щоб ваші персональні дані та токени не потрапили в публічний доступ.
- **Ніколи** не діліться своїм `TELEGRAM_BOT_TOKEN`.

---

## 📄 Ліцензія

Цей проект розповсюджується під ліцензією MIT. Деталі у файлі [LICENSE](LICENSE).
