import telebot
from telebot import types
import logging
import time
import requests
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("cpu_bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация бота
try:
    BOT_TOKEN = "7801996415:AAGz-51WgTInD7kzdknKAgeOvU1YSut8CUE"  # Замените на реальный токен
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
        raise ValueError("Токен бота не установлен!")
    bot = telebot.TeleBot(BOT_TOKEN)
except Exception as e:
    logger.critical(f"Ошибка инициализации бота: {e}")
    sys.exit(1)

# База данных процессоров
processors = {
    "office": [
        {"name": "Intel Core i3-12100", "price": "~15 000 ₽", "desc": "Идеален для офисных задач и веб-серфинга"},
        {"name": "AMD Ryzen 3 4100", "price": "~12 000 ₽", "desc": "Энергоэффективный 4-ядерный процессор"},
        {"name": "Intel Pentium Gold G7400", "price": "~8 000 ₽", "desc": "Бюджетное решение для базовых задач"}
    ],
    "gaming": [
        {"name": "Intel Core i5-13600KF", "price": "~35 000 ₽", "desc": "14 ядер (6P+8E) для игр в 1440p"},
        {"name": "AMD Ryzen 5 7600X", "price": "~32 000 ₽", "desc": "5 нм архитектура, отличная игровая производительность"},
        {"name": "Intel Core i7-13700K", "price": "~45 000 ₽", "desc": "Для 4К-гейминга и стриминга"},
        {"name": "AMD Ryzen 7 7800X3D", "price": "~50 000 ₽", "desc": "3D V-Cache для максимального FPS"}
    ],
    "professional": [
        {"name": "Intel Core i9-14900K", "price": "~75 000 ₽", "desc": "24 ядра (8P+16E), турбо-частота до 6.0 ГГц"},
        {"name": "AMD Ryzen 9 7950X", "price": "~70 000 ₽", "desc": "16 ядер/32 потока, 5.7 ГГц"},
        {"name": "Intel Xeon W5-3435X", "price": "~250 000 ₽", "desc": "Для рабочих станций (16 ядер)"},
        {"name": "AMD Threadripper PRO 5975WX", "price": "~300 000 ₽", "desc": "32 ядра, 64 потока"}
    ],
    "budget": [
        {"name": "Intel Celeron G6900", "price": "~5 000 ₽", "desc": "Самый доступный вариант для простых задач"},
        {"name": "AMD Athlon 3000G", "price": "~6 000 ₽", "desc": "Встроенная графика Radeon Vega 3"},
        {"name": "Intel Core i3-10100F", "price": "~9 000 ₽", "desc": "4 ядра/8 потоков без встроенной графики"}
    ],
    "home_server": [
        {"name": "Intel Core i5-13400", "price": "~25 000 ₽", "desc": "Эффективный 10-ядерный процессор для NAS"},
        {"name": "AMD Ryzen 5 5600G", "price": "~18 000 ₽", "desc": "С встроенной графикой для медиасервера"},
        {"name": "Intel Xeon E-2336", "price": "~40 000 ₽", "desc": "Надежное решение для 24/7 работы"}
    ],
    "content_creation": [
        {"name": "AMD Ryzen 9 7900X", "price": "~55 000 ₽", "desc": "12 ядер для монтажа видео"},
        {"name": "Intel Core i7-13700KF", "price": "~42 000 ₽", "desc": "16 потоков для 3D-рендеринга"},
        {"name": "AMD Threadripper 3960X", "price": "~120 000 ₽", "desc": "24 ядра для профессионального монтажа"}
    ]
}

def check_telegram_api():
    try:
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка подключения к Telegram API: {e}")
        return False

def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("Офисные задачи 📄"),
        types.KeyboardButton("Игры 🎮"),
        types.KeyboardButton("Профессиональные задачи 🖥️"),
        types.KeyboardButton("Бюджетные ПК 💰"),
        types.KeyboardButton("Домашний сервер 🖥️"),
        types.KeyboardButton("Контент-креатив 🎬"),
        types.KeyboardButton("Главное меню 🔙")
    ]
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        bot.send_message(
            message.chat.id,"🔍 <b>CPU Selector Bot</b> поможет подобрать оптимальный процессор!\n"
            "Выберите категорию задач:",
            parse_mode="HTML",
            reply_markup=create_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в send_welcome: {e}")
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка. Попробуйте позже.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        categories = {
            "Офисные задачи 📄": "office",
            "Игры 🎮": "gaming",
            "Профессиональные задачи 🖥️": "professional",
            "Бюджетные ПК 💰": "budget",
            "Домашний сервер 🖥️": "home_server",
            "Контент-креатив 🎬": "content_creation",
            "Главное меню 🔙": "start"
        }
        
        if message.text in categories:
            if categories[message.text] == "start":
                send_welcome(message)
            else:
                send_processors(message.chat.id, categories[message.text])
        else:
            bot.send_message(message.chat.id, "Пожалуйста, используйте кнопки для выбора.", reply_markup=create_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка. Попробуйте еще раз.", reply_markup=create_main_keyboard())

def send_processors(chat_id, category):
    try:
        procs = processors.get(category, [])
        if not procs:
            bot.send_message(chat_id, "Процессоры не найдены.", reply_markup=create_main_keyboard())
            return
        
        response = f"<b>Рекомендуемые процессоры ({category.replace('_', ' ')}):</b>\n\n"
        for proc in procs:
            response += f"▪️ <b>{proc['name']}</b> {proc['price']}\n{proc['desc']}\n\n"
        
        bot.send_message(chat_id, response, parse_mode="HTML", reply_markup=create_main_keyboard())
    except Exception as e:
        logger.error(f"Ошибка в send_processors: {e}")
        bot.send_message(chat_id, "⚠️ Не удалось загрузить данные о процессорах.", reply_markup=create_main_keyboard())

def run_bot():
    logger.info("Запуск бота...")
    while True:
        try:
            if check_telegram_api():
                logger.info("Telegram API доступен. Запускаем бота...")
                bot.infinity_polling(timeout=15, long_polling_timeout=10)
            else:
                logger.warning("Telegram API недоступен. Повторная попытка через 60 секунд...")
                time.sleep(60)
        except Exception as e:
            logger.critical(f"Критическая ошибка: {str(e)}. Перезапуск через 30 секунд...")
            time.sleep(30)

if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {str(e)}")
        sys.exit(1)









