import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

TOKEN = os.getenv("BOT_TOKEN")
TIMER_SECONDS = 30

bot = Bot(token=TOKEN)
dp = Dispatcher()

QUESTIONS = [
    {"text": "1 | She ___ to school every day.", "opts": ["go", "goes", "is going", "went"], "ans": 1},
    {"text": "2 | They ___ football on weekends.", "opts": ["plays", "is playing", "play", "played"], "ans": 2},
    {"text": "3 | Yesterday, I ___ a movie.", "opts": ["watch", "watches", "watched", "am watching"], "ans": 2},
    {"text": "4 | We ___ dinner at 7 o'clock last night.", "opts": ["eat", "eats", "ate", "are eating"], "ans": 2},
    {"text": "5 | He ___ to London last year.", "opts": ["go", "goes", "is going", "went"], "ans": 3},
    {"text": "6 | Don't worry. I ___ help you.", "opts": ["am going to", "was", "will", "going to"], "ans": 2},
    {"text": "7 | It is cold. I think it ___ snow tomorrow.", "opts": ["is going to", "snowed", "goes to", "will"], "ans": 3},
    {"text": "8 | She decided right now. She ___ call him.", "opts": ["will", "is going to", "go to", "went"], "ans": 0},
    {"text": "9 | Look at the clouds! It ___ rain.", "opts": ["will", "is going to", "went", "rains"], "ans": 1},
    {"text": "10 | I have a plan. I ___ visit my grandmother this weekend.", "opts": ["will", "am going to", "go", "went"], "ans": 1},
    {"text": "11 | They ___ open a new cafe next month.", "opts": ["will", "are going to", "is going to", "go"], "ans": 1},
    {"text": "12 | We will arrive ___ London tomorrow.", "opts": ["at", "on", "in", "to"], "ans": 2},
    {"text": "13 | The train arrives ___ the station at 9.", "opts": ["in", "on", "to", "at"], "ans": 3},
    {"text": "14 | She arrived ___ Paris last week.", "opts": ["at", "on", "in", "to"], "ans": 2},
    {"text": "15 | They arrived ___ the airport very early.", "opts": ["in", "on", "to", "at"], "ans": 3},
    {"text": "16 | He arrived ___ Monday morning.", "opts": ["in", "on", "at", "to"], "ans": 1},
    {"text": "17 | We arrived ___ the hotel after dinner.", "opts": ["in", "on", "to", "at"], "ans": 3},
    {"text": "18 | ___ students are in your class?", "opts": ["How much", "How many", "How often", "How long"], "ans": 1},
    {"text": "19 | ___ milk do we need?", "opts": ["How many", "How long", "How much", "How often"], "ans": 2},
    {"text": "20 | ___ brothers and sisters do you have?", "opts": ["How much", "How many", "How long", "How old"], "ans": 1},
    {"text": "21 | ___ does this jacket cost?", "opts": ["How many", "How much", "How long", "How often"], "ans": 1},
    {"text": "22 | ___ bottles of water did you buy?", "opts": ["How much", "How many", "How long", "How often"], "ans": 1},
    {"text": "23 | ___ sugar is in your coffee?", "opts": ["How many", "How often", "How much", "How long"], "ans": 2},
    {"text": "24 | Matn: Anna wakes up at 7. She studies English and Maths. After school she reads books.\n\nWhat time does Anna wake up?", "opts": ["At 6", "At 8", "At 7", "At 9"], "ans": 2},
    {"text": "25 | (Anna matni) What does Anna study?", "opts": ["History and Science", "English and Maths", "Music and Art", "Biology and IT"], "ans": 1},
    {"text": "26 | (Anna matni) What does Anna do after school?", "opts": ["Watches TV", "Cooks dinner", "Reads books", "Goes to gym"], "ans": 2},
    {"text": "27 | Matn: Tom will fly from Tashkent to Tokyo next summer. He wants to visit temples and eat sushi.\n\nWhere is Tom going?", "opts": ["China", "Japan", "Korea", "India"], "ans": 1},
    {"text": "28 | (Tom matni) How will Tom travel?", "opts": ["By train", "By ship", "By bus", "By plane"], "ans": 3},
    {"text": "29 | (Tom matni) What does Tom want to eat?", "opts": ["Pizza", "Sushi", "Burger", "Pasta"], "ans": 1},
    {"text": "30 | Last night, she ___ a book when the phone rang.", "opts": ["read", "reads", "was reading", "will read"], "ans": 2},
    {"text": "31 | I ___ my homework yet.", "opts": ["didn't finish", "don't finish", "won't finish", "haven't finished"], "ans": 3},
    {"text": "32 | ___ time do you spend on homework?", "opts": ["How many", "How much", "How long", "How often"], "ans": 1},
    {"text": "33 | She ___ never late for class.", "opts": ["am", "is", "are", "were"], "ans": 1},
    {"text": "34 | We arrived ___ New York after a long flight.", "opts": ["at", "on", "in", "to"], "ans": 2},
    {"text": "35 | ___ people were at the concert?", "opts": ["How much", "How many", "How long", "How often"], "ans": 1},
]

TOTAL = len(QUESTIONS)
user_state = {}
leaderboard = {}


def make_keyboard(q_index):
    q = QUESTIONS[q_index]
    buttons = [
        [InlineKeyboardButton(text=opt, callback_data=f"ans:{q_index}:{i}")]
        for i, opt in enumerate(q["opts"])
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def result_msg(name, correct):
    pct = round(correct / TOTAL * 100)
    if pct >= 90: emoji, msg = "🏆", "Ajoyib natija!"
    elif pct >= 70: emoji, msg = "😊", "Yaxshi! Davom eting!"
    elif pct >= 50: emoji, msg = "📚", "Ko'proq mashq qiling."
    else: emoji, msg = "💪", "Yana o'qing va qayta urining!"
    return (
        f"{emoji} <b>{name}</b>, test yakunlandi!\n\n"
        f"✅ To'g'ri: {correct}/{TOTAL}\n"
        f"❌ Noto'g'ri: {TOTAL-correct}/{TOTAL}\n"
        f"📊 Ball: {pct}%\n\n{msg}\n\n"
        f"Qayta boshlash: /start\nReyting: /top"
    )


async def send_question(uid, q_index):
    state = user_state.get(uid)
    if not state:
        return
    q = QUESTIONS[q_index]
    text = f"⏱ <b>{TIMER_SECONDS} soniya</b>\n\n{q['text']}"
    msg = await bot.send_message(uid, text, reply_markup=make_keyboard(q_index), parse_mode="HTML")
    state["msg_id"] = msg.message_id
    if state.get("timer_task"):
        state["timer_task"].cancel()
    state["timer_task"] = asyncio.create_task(timer_expire(uid, q_index, msg.message_id))


async def timer_expire(uid, q_index, msg_id):
    await asyncio.sleep(TIMER_SECONDS)
    state = user_state.get(uid)
    if not state or state["q"] != q_index:
        return
    state["wrong"] += 1
    state["q"] = q_index + 1
    q = QUESTIONS[q_index]
    try:
        await bot.edit_message_reply_markup(chat_id=uid, message_id=msg_id, reply_markup=None)
    except Exception:
        pass
    await bot.send_message(uid, f"⌛ Vaqt tugadi! To'g'ri javob: <b>{q['opts'][q['ans']]}</b>", parse_mode="HTML")
    if state["q"] >= TOTAL:
        await finish_test(uid)
    else:
        await send_question(uid, state["q"])


async def finish_test(uid):
    state = user_state.get(uid)
    if not state:
        return
    correct = state["correct"]
    name = state["name"]
    pct = round(correct / TOTAL * 100)
    leaderboard[uid] = {"name": name, "score": correct, "total": TOTAL, "pct": pct}
    await bot.send_message(uid, result_msg(name, correct), parse_mode="HTML")
    del user_state[uid]


@dp.message(CommandStart())
async def cmd_start(message: Message):
    uid = message.from_user.id
    name = message.from_user.first_name or "O'quvchi"
    old = user_state.get(uid)
    if old and old.get("timer_task"):
        old["timer_task"].cancel()
    user_state[uid] = {"q": 0, "correct": 0, "wrong": 0, "name": name, "timer_task": None, "msg_id": None}
    await message.answer(
        f"👋 Salom, <b>{name}</b>!\n\n"
        f"📝 {TOTAL} ta savol | ⏱ Har savolga {TIMER_SECONDS} soniya\n\n"
        f"Birinchi savol keladi!",
        parse_mode="HTML"
    )
    await asyncio.sleep(1)
    await send_question(uid, 0)


@dp.message(Command("top"))
async def cmd_top(message: Message):
    if not leaderboard:
        await message.answer("Hali hech kim test yechmagan. /start bilan boshlang!")
        return
    sorted_lb = sorted(leaderboard.values(), key=lambda x: x["pct"], reverse=True)
    medals = ["🥇", "🥈", "🥉"]
    lines = ["🏆 <b>Top natijalar:</b>\n"]
    for i, e in enumerate(sorted_lb[:10]):
        m = medals[i] if i < 3 else f"{i+1}."
        lines.append(f"{m} <b>{e['name']}</b> — {e['score']}/{e['total']} ({e['pct']}%)")
    await message.answer("\n".join(lines), parse_mode="HTML")


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
    if q_index != state["q"]:
        await call.answer("Bu savol o'tilgan.", show_alert=True)
        return
    if state.get("timer_task"):
        state["timer_task"].cancel()
        state["timer_task"] = None
    q = QUESTIONS[q_index]
    is_correct = chosen == q["ans"]
    if is_correct:
        state["correct"] += 1
        feedback = "✅ To'g'ri!"
    else:
        state["wrong"] += 1
        feedback = f"❌ Noto'g'ri. To'g'ri javob: <b>{q['opts'][q['ans']]}</b>"
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await call.message.answer(feedback, parse_mode="HTML")
    await call.answer()
    state["q"] = q_index + 1
    if state["q"] >= TOTAL:
        await finish_test(uid)
    else:
        await send_question(uid, state["q"])


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
