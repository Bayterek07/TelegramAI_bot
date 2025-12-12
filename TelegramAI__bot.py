import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
from openai import OpenAI  # Требует установки: pip install openai

# =========================================================
# КОНФИГУРАЦИЯ
# =========================================================

# !!! ВАЖНО: ЗАМЕНИТЕ ЭТО НА ВАШ РЕАЛЬНЫЙ ТОКЕН БОТА !!!
TOKEN = '8252000125:AAGy_Odrt7lFE3DXg2VU-5dWxvjcJhU7XnU' 

# !!! ВАЖНО: ЗАМЕНИТЕ ЭТОТ API КЛЮЧ НА ВАШ, ЕСЛИ ОН ИЗМЕНИТСЯ !!!
AI_API_KEY = "sk-7kndSEEJCeyq34QELNsEZnRNL0s9VfV9ou4QMSruv-GwW9PSYL45Cg1w5FdPBLZvhvjlBiz2ALQ9SfYY0Ij3bA"
AI_BASE_URL = "https://api.langdock.com/openai/eu/v1"
# ИЗМЕНЕНИЕ: Пробуем более мощную модель, чтобы исключить проблему с gpt-4o-mini
AI_MODEL_NAME = "gpt-4o" 


logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher()
# Инициализация клиента OpenAI вне обработчика для эффективности
client = OpenAI(
    base_url = AI_BASE_URL,
    api_key = AI_API_KEY
)


# =========================================================
# ОБРАБОТЧИК КОМАНДЫ СТАРТ
# =========================================================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('👋 Привет! Я бот с подключенной нейросетью, отправь свой запрос.', parse_mode = 'HTML')


# =========================================================
# ОБРАБОТЧИК ЛЮБОГО ТЕКСТОВОГО СООБЩЕНИЯ
# =========================================================
@dp.message(lambda message: message.text)
async def filter_messages(message: Message):
    # Добавляем сообщение о загрузке
    processing_msg = await message.answer("🧠 Думаю над ответом... Пожалуйста, подождите.")
    
    try:
        completion = client.chat.completions.create(
            # ИСПОЛЬЗУЕМ НОВУЮ МОДЕЛЬ:
            model=AI_MODEL_NAME, 
            messages=[
                {"role": "user", "content": message.text}
            ]
        )
        text = completion.choices[0].message.content

        # Отправляем ответ, используя HTML для надежности форматирования
        await message.answer(text, parse_mode="HTML")
        
    except Exception as e:
        # Выводим подробную ошибку в терминал
        logging.error(f"Ошибка при обращении к ИИ: {e}")
        # Отправляем пользователю общее сообщение об ошибке
        await message.answer(f"⚠ Произошла ошибка при обращении к ИИ. Пожалуйста, попробуйте позже.")
    finally:
        # Удаляем сообщение о загрузке
        await processing_msg.delete()


# =========================================================
# ЗАПУСК
# =========================================================
async def main():
    print("Бот GPT запущен...")
    # Удаляем вебхуки и запускаем долгий опрос
    await bot(DeleteWebhook(drop_pending_updates=True)) 
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())
