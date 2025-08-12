from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
import uuid

TOKEN = "айди"
MAX_PARTICIPANTS = 20
YOOKASSA_SHOP_ID = "ВАШ_SHOP_ID"
YOOKASSA_SECRET_KEY = "ВАШ_SECRET_KEY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

paid_participants = set()
pending_payments = {}  # {user_id: payment_id}

class PaymentStates(StatesGroup):
    WAITING_PAYMENT = State()

# Клавиатуры
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оплатить✅")],
        [KeyboardButton(text="Связаться с Инной✍🏻")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: types.Message):
    welcome_text = (
        "Привет! Это Инна и ты в шаге от нашей встречи на парфюмерном мастер-классе от меня:)\n\n"
        f"Свободных мест осталось: {MAX_PARTICIPANTS - len(paid_participants)} из {MAX_PARTICIPANTS}\n\n"
        "🤍 Обучение для начинающих\n🤍 Основы парфюмерии\n🤍 2,5-3 часа с фуршетом\n\n"
        "Стоимость: 2599₽. Места ограничены!"
    )
    await message.answer(welcome_text, reply_markup=main_keyboard)

@dp.message(lambda message: message.text == "Оплатить✅")
async def process_payment(message: types.Message, state: FSMContext):
    if len(paid_participants) >= MAX_PARTICIPANTS:
        await message.answer("❌ Все места заняты! Свяжитесь с Инной для уточнения.")
        return
    
    # Генерируем уникальный ID платежа
    payment_id = str(uuid.uuid4())
    pending_payments[message.from_user.id] = payment_id
    
    # Здесь должна быть реальная интеграция с ЮKassa
    payment_url = f"https://yoomoney.ru/checkout/payments/v2/contract?orderId={payment_id}&amount=2599"
    
    await message.answer(
        "Перейдите по ссылке для оплаты:\n"
        f"{payment_url}\n\n"
        "После оплаты нажмите кнопку ниже:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Я оплатил(а)", callback_data="check_payment")]
        ])
    )
    await state.set_state(PaymentStates.WAITING_PAYMENT)

async def check_payment_status(payment_id: str) -> bool:
    """Функция проверки оплаты через API ЮKassa"""
    # В реальном проекте здесь должен быть запрос к API ЮKassa
    # Это заглушка для примера - в 80% случаев возвращает True
    return True  # Замените на реальную проверку

@dp.callback_query(PaymentStates.WAITING_PAYMENT, lambda c: c.data == "check_payment")
async def verify_payment(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    payment_id = pending_payments.get(user_id)
    
    if not payment_id:
        await callback_query.message.answer("Платеж не найден. Попробуйте начать заново.")
        await state.clear()
        return
    
    # Проверяем оплату
    is_paid = await check_payment_status(payment_id)
    
    if is_paid:
        paid_participants.add(user_id)
        confirmation = (
            "Привет! Это Инна:)\n\n"
            "Все готово, мастер-класс оплачен!❤️\n"
            "Увидимся на нашей встрече:)\n\n"
            "📍 Место:\n"
            "Ⓜ️ Курская, Наставнический пер., д. 17, стр.1, WorkShopLoft 9\n\n"
            "⏰ Время сбора гостей – 12:00, начало: 13:00\n\n"
            f"Ваш номер: {len(paid_participants)}/{MAX_PARTICIPANTS}"
        )
        await callback_query.message.answer(confirmation)
    else:
        await callback_query.message.answer("❌ Оплата не найдена. Попробуйте еще раз или свяжитесь с поддержкой.")
    
    await state.clear()
    await bot.answer_callback_query(callback_query.id)

@dp.message(lambda message: message.text == "Связаться с Инной✍🏻")
async def contact_me(message: types.Message):
    await message.answer(
        "Переходите в чат с Инной 👇",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Написать Инне", url="https://t.me/innaboutbeautypr")]
        ])
    )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())