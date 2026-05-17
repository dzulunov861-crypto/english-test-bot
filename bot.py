import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

QUESTIONS = [
    {"text": "1/30 | She ___ to school every day.", "opts": ["go", "goes", "is going", "went"], "ans": 1},
    {"text": "2/30 | They ___ football on weekends.", "opts": ["plays", "is playing", "play", "played"], "ans": 2},
    {"text": "3/30 | Yesterday, I ___ a movie.", "opts": ["watch", "watches", "watched", "am watching"], "ans": 2},
    {"text": "4/30 | We ___ dinner at 7 o'clock last night.", "opts": ["eat", "eats", "ate", "are eating"], "ans": 2},
    {"text": "5/30 | He ___ to London last year.", "opts": ["go", "goes", "is going", "went"], "ans": 3},
    {"text": "6/30 | Don't worry. I ___ help you.", "opts": ["am going to", "was", "will", "going to"], "ans": 2},
    {"text": "7/30 | It is cold. I think it ___ snow tomorrow.", "opts": ["is going to", "snowed", "goes to", "will"], "ans": 3},
    {"text": "8/30 | She decided right now. She ___ call him.", "opts": ["will", "is going to", "go to", "went"], "ans": 0},
    {"text": "9/30 | Look at the clouds! It ___ rain.", "opts": ["will", "is going to", "went", "rains"], "ans": 1},
    {"text": "10/30 | I have a plan. I ___ visit my grandmother this weekend.", "opts": ["will", "am going to", "go", "went"], "ans": 1},
    {"text": "11/30 | They ___ open a new café next month.", "opts": ["will", "are going to", "is going to", "go"], "ans": 1},
    {"text": "12/30 | We will arrive ___ London tomorrow.", "opts": ["at", "on", "in", "to"], "ans": 2},
    {"text": "13/30 | The train arrives ___ the station at 9 o'clock.", "opts": ["in", "on", "to", "at"], "ans": 3},
    {"text": "14/30 | She arrived ___ Paris last week.", "opts": ["at", "on", "in", "to"], "ans": 2},
    {"text": "15/30 | They arrived ___ the airport very early.", "opts": ["in", "on", "to", "at"], "ans": 3},
    {"text": "16/30 | He arrived ___ Monday morning.", "opts": ["in", "on", "at", "to"], "ans": 1},
    {"text": "17/30 | We arrived ___ the hotel after dinner.", "opts": ["in", "on", "to", "at"], "ans": 3},
    {"text": "18/30 | ___ students are in your class?", "opts": ["How much", "How many", "How often", "How long"], "ans": 1},
    {"text": "19/30 | ___ milk do we need for the recipe?", "opts": ["How many", "How long", "How much", "How often"], "ans": 2},
    {"text": "20/30 | ___ brothers and sisters do you have?", "opts": ["How much", "How many", "How long", "How old"], "ans": 1},
    {"text": "21/30 | ___ does this jacket cost?", "opts": ["How many", "How much", "How long", "How often"], "ans": 1},
    {"text": "22/30 | ___ bottles of water did you buy?", "opts": ["How much", "How many", "How long", "How often"], "ans": 1},
    {"text": "23/30 | ___ sugar is in your coffee?", "opts": ["How many", "How often", "How much", "How long"], "ans": 2},
    {
        "text": (
            "24/30 | 📖 Matnni o'qing:\n\n"
            "«Anna is a student. She wakes up at 7 every morning. "
            "She eats breakfast and goes to university. She studies English and Maths. "
            "After school, she usually reads books or listens to music.»\n\n"
            "What time does Anna wake up?"
        ),
        "opts": ["At 6 o'clock", "At 8 o'clock", "At 7 o'clock", "At 9 o'clock"],
        "ans": 2,
    },
    {"text": "25/30 | (Yuqoridagi matn) What subjects does Anna study?", "opts": ["History and Science", "English and Maths", "Music and Art", "Biology and IT"], "ans": 1},
    {"text": "26/30 | (Yuqoridagi matn) What does Anna do after school?", "opts": ["She watches TV", "She cooks dinner", "She reads books or listens to music", "She goes to the gym"], "ans": 2},
    {
        "text": (
            "27/30 | 📖 Matnni o'qing:\n\n"
            "«Tom is going to travel to Japan next summer. He will fly from Tashkent to Tokyo. "
            "He wants to visit temples, eat sushi, and learn some Japanese words. "
            "He is very excited about the trip.»\n\n"
            "Where is Tom going to travel?"
        ),
        "opts": ["To China", "To Japan", "To Korea", "To India"],
        "ans": 1,
    },
    {"text": "28/30 | (Yuqoridagi matn) How is Tom going to travel?", "opts": ["By train", "By ship", "By bus", "By plane"], "ans": 3},
    {"text": "29/30 | (Yuqoridagi matn) What does Tom want to eat there?", "opts": ["Pizza", "Sushi", "Burger", "Pasta"], "ans": 1},
    {"text": "30/30 | Last night, she ___ a book when the phone rang.", "opts": ["read", "reads", "was reading", "will read"], "ans": 2},
]

# user_id -> {q: int, correct: int, wrong: int}
user_state = {}


def make_keyboard(q_index: int) -> InlineKeyboardMarkup:
    q = QUESTIONS[q_index]
    buttons = [
        [InlineKeyboardButton(text=opt, callback_data=f"ans:{q_index}:{i}")]
        for i, opt in enumerate(q["opts"])
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def result_message(correct: int) -> str:
    pct = round(correct / 30 * 100)
    if pct >= 90:
        emoji = "🏆"
        msg = "Ajoyib natija! Siz juda yaxshi bilasiz!"
    elif pct >= 70:
        emoji = "😊"
        msg = "Yaxshi! Davom eting!"
    elif pct >= 50:
        emoji = "📚"
        msg = "Yaxshi harakat! Ko'proq mashq qiling."
    else:
        emoji = "💪"
        msg = "Qo'rqmang, yana o'qing va qayta urinib ko'ring!"

    return (
        f"{emoji} Test yakunlandi!\n\n"
        f"✅ To'g'ri: {correct}/30\n"
        f"❌ Noto'g'ri: {30 - correct}/30\n"
        f"📊 Ball: {pct}%\n\n"
        f"{msg}\n\n"
        f"Qayta boshlash uchun /start yozing."
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_state[message.from_user.id] = {"q": 0, "correct": 0, "wrong": 0}
    q = QUESTIONS[0]
    await message.answer(
        "👋 Salom! Elementary English Test boshlanyapti.\n"
        "30 ta savol. Har bir savolga to'g'ri javobni tanlang.\n\n"
        + q["text"],
        reply_markup=make_keyboard(0),
    )


@dp.callback_query(F.data.startswith("ans:"))
async def handle_answer(call: CallbackQuery):
    uid = call.from_user.id
    state = user_state.get(uid)

    if state is None:
        await call.answer("Testni boshlash uchun /start yozing.", show_alert=True)
        return

    _, q_str, i_str = call.data.split(":")
    q_index = int(q_str)
    chosen = int(i_str)

    # Eski savolga qayta bosilmasin
    if q_index != state["q"]:
        await call.answer("Bu savol allaqachon o'tilgan.", show_alert=True)
        return

    q = QUESTIONS[q_index]
    correct_opt = q["opts"][q["ans"]]
    chosen_opt = q["opts"][chosen]
    is_correct = chosen == q["ans"]

    if is_correct:
        state["correct"] += 1
        feedback = f"✅ To'g'ri!"
    else:
        state["wrong"] += 1
        feedback = f"❌ Noto'g'ri. To'g'ri javob: <b>{correct_opt}</b>"

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(feedback, parse_mode="HTML")
    await call.answer()

    next_index = q_index + 1
    state["q"] = next_index

    if next_index >= len(QUESTIONS):
        await call.message.answer(result_message(state["correct"]))
        del user_state[uid]
    else:
        next_q = QUESTIONS[next_index]
        await call.message.answer(next_q["text"], reply_markup=make_keyboard(next_index))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
