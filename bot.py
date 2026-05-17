import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

from questions import QUESTIONS  # <-- savollar shu yerdan keladi

TOKEN = os.getenv("BOT_TOKEN")
TIMER_SECONDS = 30  # har savol uchun vaqt (soniyada)

bot = Bot(token=TOKEN)
dp = Dispatcher()

TOTAL = len(QUESTIONS)

# { user_id: {q, correct, wrong, name, timer_task, msg_id} }
user_state = {}

# { user_id: {name, score, total, pct} }
leaderboard = {}


def make_keyboard(q_index: int) -> InlineKeyboardMarkup:
    q = QUESTIONS[q_index]
    buttons = [
        [InlineKeyboardButton(text=opt, callback_data=f"ans:{q_index}:{i}")]
        for i, opt in enumerate(q["opts"])
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def result_message(name: str, correct: int) -> str:
    pct = round(correct / TOTAL * 100)
    if pct >= 90:
        emoji, msg = "🏆", "Ajoyib natija!"
    elif pct >= 70:
        emoji, msg = "😊", "Yaxshi! Davom eting!"
    elif pct >= 50:
        emoji, msg = "📚", "Yaxshi harakat! Ko'proq mashq qiling."
    else:
        emoji, msg = "💪", "Qo'rqmang, yana o'qing va qayta urinib ko'ring!"

    return (
        f"{emoji} <b>{name}</b>, test yakunlandi!\n\n"
        f"✅ To'g'ri: {correct}/{TOTAL}\n"
        f"❌ Noto'g'ri: {TOTAL - correct}/{TOTAL}\n"
        f"📊 Ball: {pct}%\n\n"
        f"{msg}\n\n"
        f"Qayta boshlash: /start\n"
        f"Reyting ko'rish: /top"
    )


async def send_question(uid: int, q_index: int):
    state = user_state.get(uid)
    if not state:
        return
    q = QUESTIONS[q_index]
    text = f"⏱ <b>{TIMER_SECONDS} soniya</b>\n\n{q['text']}"
    msg = await bot.send_message(uid, text, reply_markup=make_keyboard(q_index), parse_mode="HTML")
    state["msg_id"] = msg.message_id

    if state.get("timer_task"):
        state["timer_task"].cancel()

    task = asyncio.create_task(timer_expire(uid, q_index, msg.message_id))
    state["timer_task"] = task


async def timer_expire(uid: int, q_index: int, msg_id: int):
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

    correct_opt = q["opts"][q["ans"]]
    await bot.send_message(uid, f"⌛ Vaqt tugadi! To'g'ri javob: <b>{correct_opt}</b>", parse_mode="HTML")

    if state["q"] >= TOTAL:
        await finish_test(uid)
    else:
        await send_question(uid, state["q"])


async def finish_test(uid: int):
    state = user_state.get(uid)
    if not state:
        return
    correct = state["correct"]
    name = state["name"]
    pct = round(correct / TOTAL * 100)

    leaderboard[uid] = {"name": name, "score": correct, "total": TOTAL, "pct": pct}

    await bot.send_message(uid, result_message(name, correct), parse_mode="HTML")
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
        f"Tayyor bo'lsangiz, birinchi savol keladi!",
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
    for i, entry in enumerate(sorted_lb[:10]):
        medal = medals[i] if i < 3 else f"{i+1}."
        lines.append(f"{medal} <b>{entry['name']}</b> — {entry['score']}/{entry['total']} ({entry['pct']}%)")

    await message.answer("\n".join(lines), parse_mode="HTML")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
