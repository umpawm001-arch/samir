import asyncio
import logging
import time
from datetime import datetime
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    BotCommand,
)

# === SOZLAMALAR ===
TOKEN = "8643758285:AAFL4Cv-mpsqPTJJkWTyhv5rWh1l6N5VCL8"
ADMIN_ID = 8878519140
ADMIN_PASSWORD = "samir1234"
CARD_NUMBER = "9860 1666 5619 0666"
CARD_HOLDER = "K.U"
REF_BONUS = 3000

# === STIKERLAR ===
STICKERS = {
    "main": "CAACAgIAAxkBAAER9fBqupiGfIbVkhas-99iIh30slYiFwAClmQAAoBKwEoF-PhllH7s0z0E",
    "topup": "CAACAgEAAxkBAAER9fRquplZXvIClUoY0Y-Q4Fcy2eUYrgACAwMAAoOo4EQ3ZTysFteinT0E",
    "buy": "CAACAgEAAxkBAAER9fZqupmLvTzj6U3nF7XD_Nd_TIdzlAACTAUAAmT_sEfz8RU-1D-ilT0E",
    "profile": "CAACAgIAAxkBAAER9fhqupnu08NKiRCp9GUnQ-ybm7N-hwACyUoAAi7LQEvGM2FguGcKTT0E",
    "ref": "CAACAgIAAxkBAAER9fpquponN0buSTH4DEyhzbRSF8Z7nAACSAIAAladvQoc9XL43CkU0D0E",
    "admin": "CAACAgIAAxkBAAER9fxquppgM0xdB3qFoeZcfXLiWcV0xwAC9wADVp29CgtyJB1I9A0wPQQ",
    "cookie": "CAACAgIAAxkBAAER9fBqupiGfIbVkhas-99iIh30slYiFwAClmQAAoBKwEoF-PhllH7s0z0E",
}

logging.basicConfig(level=logging.INFO)
router = Router()
bot_start_time = time.time()


# ==================== FSM HOLATLARI ====================
class AdminStates(StatesGroup):
    waiting_for_password = State()
    adding_account_game = State()
    adding_account_name = State()
    adding_account_price = State()
    adding_cookie_name = State()
    adding_cookie_price = State()
    adding_cookie_desc = State()
    waiting_for_promo_code = State()
    waiting_for_promo_amount = State()
    waiting_for_promo_limit = State()
    waiting_for_broadcast = State()
    waiting_for_user_message = State()
    waiting_for_user_id = State()


class BuyStates(StatesGroup):
    waiting_for_custom_amount = State()
    waiting_for_receipt = State()


class UserStates(StatesGroup):
    waiting_for_activate_promo = State()


# ==================== MA'LUMOTLAR BAZASI ====================
database = {
    "accounts": {},
    "cookies": {},
    "users": {},
    "promos": {},
    "klent_counter": 0,
    "total_topups": 0,
    "total_sales": 0,
}


# ==================== YORDAMCHI FUNKSIYALAR ====================
async def safe_edit(message, text, kb=None, parse_mode="Markdown"):
    """Xabarni tahrirlash, agar iloji bo'lmasa yangi yuborish"""
    markup = InlineKeyboardMarkup(inline_keyboard=kb) if kb else None
    try:
        if message.photo:
            await message.edit_caption(caption=text, reply_markup=markup, parse_mode=parse_mode)
        elif message.text:
            await message.edit_text(text=text, reply_markup=markup, parse_mode=parse_mode)
        else:
            await message.edit_reply_markup(reply_markup=markup)
    except Exception:
        try:
            await message.answer(text, reply_markup=markup, parse_mode=parse_mode)
        except Exception:
            pass


def format_money(amount):
    return f"{amount:,}".replace(",", " ")


def main_menu(user_id):
    kb = [
        [InlineKeyboardButton(text="🛍 Do'konni ochish", callback_data="buy_accounts")],
        [InlineKeyboardButton(text="🍪 Cookie Accs", callback_data="cookie_list")],
        [
            InlineKeyboardButton(text="👤 Profil kabineti", callback_data="profile"),
            InlineKeyboardButton(text="💳 Balansni to'ldirish", callback_data="top_up"),
        ],
        [InlineKeyboardButton(text="🪙 Referal dasturi (Bonus)", callback_data="referral")],
        [InlineKeyboardButton(text="ℹ️ Bot haqida", callback_data="about_bot")],
    ]
    if user_id == ADMIN_ID:
        kb.append([InlineKeyboardButton(text="⚙️ Admin boshqaruv paneli", callback_data="admin_panel")])
    return kb


def back_button(callback_data="back_to_main"):
    return [[InlineKeyboardButton(text="⬅️ Orqaga", callback_data=callback_data)]]


def cancel_button(callback_data="back_to_main"):
    return [[InlineKeyboardButton(text="❌ Bekor qilish", callback_data=callback_data)]]


# ==================== START ====================
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    name = message.from_user.first_name

    if user_id not in database["users"]:
        database["klent_counter"] += 1
        klent_code = f"klent{database['klent_counter']}"
        database["users"][user_id] = {
            "balance": 0,
            "ref_count": 0,
            "invited_by": None,
            "klent_code": klent_code,
            "used_promos": [],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0,
        }

    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id != user_id and ref_id in database["users"]:
            if database["users"][user_id]["invited_by"] is None:
                database["users"][user_id]["invited_by"] = ref_id
                database["users"][ref_id]["ref_count"] += 1
                database["users"][ref_id]["balance"] += REF_BONUS

    await message.answer_sticker(sticker=STICKERS["main"])
    caption = (
        f"✨ **SAMIR STORE — PREMIUM** ✨\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 Salom, **{name}**! 💎\n\n"
        f"🔥 **PUBG Mobile** va boshqa o'yin akkauntlari hamda **Cookie Accs** rasmiy do'koni.\n\n"
        f"⚡️ Kerakli bo'limni tanlang va xarid qilishni boshlang!"
    )
    await message.answer(
        caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=main_menu(user_id)),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    name = callback.from_user.first_name

    caption = (
        f"✨ **SAMIR STORE — PREMIUM** ✨\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 Salom, **{name}**! 💎\n\n"
        f"🔥 **PUBG Mobile** va boshqa o'yin akkauntlari hamda **Cookie Accs** rasmiy do'koni.\n\n"
        f"⚡️ Kerakli bo'limni tanlang va xarid qilishni boshlang!"
    )
    await safe_edit(callback.message, caption, main_menu(user_id))
    await callback.answer()


@router.callback_query(F.data == "about_bot")
async def about_bot(callback: CallbackQuery):
    text = (
        f"ℹ️ **SAMIR STORE — BOT HAQIDA**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🛒 **Xizmatlar:**\n"
        f"• 🎮 PUBG Mobile akkauntlari\n"
        f"• 🍪 Cookie Accs\n"
        f"• 🎁 Promokodlar va bonuslar\n\n"
        f"👑 **Ishonchli do'kon:**\n"
        f"• ✅ Tez yetkazib berish\n"
        f"• ✅ Xavfsiz to'lov\n"
        f"• ✅ 24/7 qo'llab-quvvatlash\n\n"
        f"📞 **Admin bilan bog'lanish:** @samir_admin"
    )
    await safe_edit(callback.message, text, back_button())
    await callback.answer()


# ==================== 🍪 COOKIE ACCS ====================
@router.callback_query(F.data == "cookie_list")
async def cookie_list(callback: CallbackQuery):
    available = [(cid, c) for cid, c in database["cookies"].items() if not c["sold"]]

    if not available:
        await safe_edit(
            callback.message,
            "🍪 **COOKIE ACCS**\n\n"
            "Hozircha sotuvda cookie akkauntlar mavjud emas.\n"
            "Tez orada yangi cookie lar qo'shiladi! 🔥",
            back_button()
        )
        await callback.answer()
        return

    kb = []
    for cid, c in available:
        kb.append([InlineKeyboardButton(
            text=f"🍪 {c['name']} — {format_money(int(c['price']))} so'm",
            callback_data=f"select_cookie_{cid}"
        )])
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main")])

    await safe_edit(
        callback.message,
        f"🍪 **COOKIE ACCS**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🟢 Mavjud cookie lar: **{len(available)} ta**\n\n"
        f"Kerakli cookie akkauntni tanlang:",
        kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("select_cookie_"))
async def buy_cookie_process(callback: CallbackQuery):
    cid = int(callback.data.split("_")[2])
    c = database["cookies"].get(cid)
    user = callback.from_user
    user_id = user.id

    if not c or c["sold"]:
        await callback.answer("⚠️ Bu cookie allaqachon sotilgan!", show_alert=True)
        return

    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0, "ref_count": 0, "invited_by": None,
            "klent_code": f"klent{database['klent_counter']}", "used_promos": [],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0,
        }

    user_balance = database["users"][user_id]["balance"]
    price = int(c["price"])

    if user_balance < price:
        await callback.answer(
            f"❌ Mablag' yetarli emas!\nSizda: {format_money(user_balance)} so'm\nNarxi: {format_money(price)} so'm",
            show_alert=True
        )
        return

    database["users"][user_id]["balance"] -= price
    database["users"][user_id]["total_spent"] += price
    c["sold"] = True
    database["total_sales"] += price

    klent_code = database["users"][user_id]["klent_code"]

    text = (
        f"🎉 **COOKIE SOTIB OLINDI!** 🍪\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏷 Nomi: **{c['name']}**\n"
        f"📝 Tavsif: {c.get('desc', '—')}\n"
        f"💰 Narxi: **{format_money(price)} so'm**\n\n"
        f"📨 *Admin tez orada cookie faylini shu bot orqali yuboradi!*\n"
        f"🔖 Sizning kodingiz: `/{klent_code}`"
    )
    await safe_edit(callback.message, text, back_button())

    admin_text = (
        f"🍪 **YANGI COOKIE SOTIB OLINDI!** 🔔\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 Xaridor: **{user.full_name}**\n"
        f"🔗 Username: @{user.username}\n"
        f"🆔 ID: `{user.id}`\n"
        f"🔖 KODI: `/{klent_code}`\n\n"
        f"🏷 Cookie: **{c['name']}**\n"
        f"📝 Tavsif: {c.get('desc', '—')}\n"
        f"💰 Narxi: **{format_money(price)} so'm**\n\n"
        f"⚠️ **COOKIE YUBORISH:**\n"
        f"`/{klent_code} [cookie matni]`\n"
        f"yoki\n"
        f"`/user {user.id} [cookie matni]`\n\n"
        f"📌 Misol:\n"
        f"`/{klent_code} Cookie: abc123xyz...`"
    )

    await callback.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    await callback.answer("✅ Cookie sotib olindi!")


# ==================== PROFIL ====================
@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0, "ref_count": 0, "invited_by": None,
            "klent_code": f"klent{database['klent_counter']}", "used_promos": [],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0,
        }

    user = database["users"][user_id]

    text = (
        f"👤 **SHAXSIY KABINET** 💎\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 Telegram ID: `{user_id}`\n"
        f"🔖 Sizning kodingiz: `/{user['klent_code']}`\n"
        f"📅 Ro'yxatdan o'tgan: `{user.get('registered_at', '—')}`\n\n"
        f"💰 **Balans:** `{format_money(user['balance'])} so'm`\n"
        f"💸 **Sarflangan:** `{format_money(user.get('total_spent', 0))} so'm`\n"
        f"👥 **Taklif qilganlar:** `{user['ref_count']} ta`\n\n"
        f"⚡️ Xavfsizlik: Yuqori 🔒"
    )
    kb = [
        [InlineKeyboardButton(text="🎁 Promokod kiritish", callback_data="enter_promo")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main")]
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data == "enter_promo")
async def enter_promo_handler(callback: CallbackQuery, state: FSMContext):
    await safe_edit(
        callback.message,
        "🎁 **PROMOKOD KIRITISH**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Iltimos, promokodni yuboring:\n\n"
        "📌 *Promokod katta-kichik harflarga sezgir emas*",
        cancel_button("profile")
    )
    await state.set_state(UserStates.waiting_for_activate_promo)
    await callback.answer()


@router.message(UserStates.waiting_for_activate_promo)
async def activate_promo_process(message: Message, state: FSMContext):
    user_id = message.from_user.id
    code = message.text.strip().upper()
    await state.clear()

    if code not in database["promos"]:
        await message.answer(
            "❌ **Promokod topilmadi!**\n\n"
            "Bunday promokod mavjud emas yoki eskirgan.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="👤 Profilga qaytish", callback_data="profile")
            ]])
        )
        return

    promo = database["promos"][code]
    promo_amount = promo["amount"]
    promo_limit = promo.get("limit", 0)
    promo_used = promo.get("used_count", 0)

    if promo_limit > 0 and promo_used >= promo_limit:
        await message.answer(
            "⚠️ **Promokod limiti tugagan!**\n\n"
            "Bu promokod allaqachon o'z limitiga yetgan.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="👤 Profilga qaytish", callback_data="profile")
            ]])
        )
        return

    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0, "ref_count": 0, "invited_by": None,
            "klent_code": f"klent{database['klent_counter']}", "used_promos": [],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0,
        }

    user = database["users"][user_id]

    if code in user["used_promos"]:
        await message.answer(
            "⚠️ **Siz bu promokoddan allaqachon foydalangansiz!**",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="👤 Profilga qaytish", callback_data="profile")
            ]])
        )
        return

    user["balance"] += promo_amount
    user["used_promos"].append(code)
    database["promos"][code]["used_count"] = promo_used + 1

    await message.answer(
        f"🎉 **PROMOKOD FAOLLASHTIRILDI!**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎁 Promokod: `{code}`\n"
        f"💰 Bonus: **{format_money(promo_amount)} so'm**\n\n"
        f"💎 Yangi balansingiz: **{format_money(user['balance'])} so'm**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="👤 Profilga qaytish", callback_data="profile")
        ]])
    )


# ==================== REFERAL ====================
@router.callback_query(F.data == "referral")
async def show_referral(callback: CallbackQuery):
    user_id = callback.from_user.id
    bot_info = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"

    user = database["users"].get(user_id, {})
    ref_count = user.get("ref_count", 0)
    earned = ref_count * REF_BONUS

    text = (
        f"🪙 **REFERAL DASTURI** 🎁\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Do'stlaringizni taklif qiling va har bir do'stingiz uchun\n"
        f"**{format_money(REF_BONUS)} so'm** bonus oling! 🚀\n\n"
        f"📊 **Sizning statistikangiz:**\n"
        f"👥 Taklif qilinganlar: `{ref_count} ta`\n"
        f"💰 Ishlangan bonus: `{format_money(earned)} so'm`\n\n"
        f"🔗 **Sizning havolangiz:**\n"
        f"`{ref_link}`"
    )
    kb = [
        [InlineKeyboardButton(text="📤 Ulashish", switch_inline_query=f"https://t.me/{bot_info.username}?start={user_id}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main")]
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


# ==================== BALANS TO'LDIRISH ====================
@router.callback_query(F.data == "top_up")
async def top_up_balance(callback: CallbackQuery, state: FSMContext):
    text = (
        f"💳 **HISOBNI TO'LDIRISH** ⚡️\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"To'ldirmoqchi bo'lgan summani tanlang:\n\n"
        f"💡 *Minimal: 10 000 so'm*"
    )
    kb = [
        [
            InlineKeyboardButton(text="💵 10 000", callback_data="amount_10000"),
            InlineKeyboardButton(text="💵 20 000", callback_data="amount_20000"),
        ],
        [
            InlineKeyboardButton(text="💵 30 000", callback_data="amount_30000"),
            InlineKeyboardButton(text="💵 50 000", callback_data="amount_50000"),
        ],
        [
            InlineKeyboardButton(text="💵 100 000", callback_data="amount_100000"),
            InlineKeyboardButton(text="✍️ Boshqa summa", callback_data="amount_custom"),
        ],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main")]
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data.startswith("amount_"))
async def process_amount_selection(callback: CallbackQuery, state: FSMContext):
    data_value = callback.data.split("_")[1]

    if data_value == "custom":
        await safe_edit(
            callback.message,
            "✍️ **SUMMANI KIRITING**\n\n"
            "O'zingiz xohlagan summani raqamlarda kiriting:\n"
            "📌 *Misol: 25000*",
            cancel_button()
        )
        await state.set_state(BuyStates.waiting_for_custom_amount)
        await callback.answer()
        return

    amount = int(data_value)
    await state.update_data(selected_amount=amount)

    await send_card_details(callback.message, amount)
    await state.set_state(BuyStates.waiting_for_receipt)
    await callback.answer()


@router.message(BuyStates.waiting_for_custom_amount)
async def process_custom_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting! Qaytadan urinib ko'ring:")
        return

    amount = int(message.text)
    if amount < 10000:
        await message.answer("❌ Minimal summa: **10 000 so'm**. Qaytadan kiriting:")
        return

    await state.update_data(selected_amount=amount)
    await send_card_details(message, amount)
    await state.set_state(BuyStates.waiting_for_receipt)


async def send_card_details(message, amount: int):
    text = (
        f"💳 **TO'LOV MA'LUMOTLARI** ⚠️\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Tanlangan summa: **{format_money(amount)} so'm**\n\n"
        f"📌 Quyidagi kartaga to'lov qiling:\n"
        f"💳 Karta: `{CARD_NUMBER}`\n"
        f"👤 Egasi: `{CARD_HOLDER}`\n\n"
        f"🚨 **DIQQAT!**\n"
        f"• To'lovni **aniq** tanlangan summada qiling\n"
        f"• Kam to'lov qilsangiz — pul qaytarilmaydi!\n\n"
        f"📸 To'lovdan so'ng **chek (skrinshot)** ni shu botga yuboring!"
    )
    kb = [[InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_to_main")]]
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")


@router.message(BuyStates.waiting_for_receipt, F.photo)
async def receive_receipt(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    user = message.from_user
    state_data = await state.get_data()
    selected_amount = state_data.get("selected_amount", 0)

    if user.id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user.id] = {
            "balance": 0, "ref_count": 0, "invited_by": None,
            "klent_code": f"klent{database['klent_counter']}", "used_promos": [],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0,
        }

    klent_code = database["users"][user.id]["klent_code"]

    text = (
        f"📥 **YANGI TO'LOV CHEKI!** 🔔\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 Xaridor: **{user.full_name}**\n"
        f"🔗 @{user.username}\n"
        f"🆔 ID: `{user.id}`\n"
        f"🔖 KODI: `/{klent_code}`\n\n"
        f"💰 Summa: **{format_money(selected_amount)} so'm**"
    )

    kb = [
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"topup_yes_{user.id}_{selected_amount}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"topup_no_{user.id}"),
        ]
    ]

    await message.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown",
    )
    await message.answer(
        f"✅ **CHEKINGIZ YUBORILDI!**\n\n"
        f"🔖 Sizning kodingiz: `/{klent_code}`\n"
        f"⏳ Admin tez orada tekshiradi va balansingizni to'ldiradi."
    )
    await state.clear()


@router.callback_query(F.data.startswith("topup_yes_"))
async def topup_approve(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    parts = callback.data.split("_")
    user_id = int(parts[2])
    added_amount = int(parts[3])

    try:
        await callback.message.edit_caption(
            caption=(callback.message.caption or "") + f"\n\n✅ **TASDIQLANDI** (+{format_money(added_amount)} so'm)",
            parse_mode="Markdown",
        )
    except Exception:
        pass

    if user_id in database["users"]:
        database["users"][user_id]["balance"] += added_amount
        database["total_topups"] += added_amount

    await callback.bot.send_message(
        chat_id=user_id,
        text=f"✅ **BALANS TO'LDIRILDI!** 🎉\n"
             f"━━━━━━━━━━━━━━━━━━━━\n\n"
             f"💰 Qo'shildi: **{format_money(added_amount)} so'm**\n"
             f"💎 Yangi balans: **{format_money(database['users'][user_id]['balance'])} so'm**",
        parse_mode="Markdown",
    )
    await callback.answer("✅ Tasdiqlandi!")


@router.callback_query(F.data.startswith("topup_no_"))
async def topup_reject(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    user_id = int(callback.data.split("_")[2])

    try:
        await callback.message.edit_caption(
            caption=(callback.message.caption or "") + "\n\n❌ **RAD ETILDI**",
            parse_mode="Markdown",
        )
    except Exception:
        pass

    await callback.bot.send_message(
        chat_id=user_id,
        text="❌ **To'lov rad etildi!**\n\n"
             "Sabab: Soxta chek yoki summa noto'g'ri.\n"
             "Savollar uchun adminga murojaat qiling.",
    )
    await callback.answer("❌ Rad etildi!")


# ==================== DO'KON ====================
@router.callback_query(F.data == "buy_accounts")
async def list_accounts(callback: CallbackQuery):
    available_accs = [(aid, a) for aid, a in database["accounts"].items() if not a["sold"]]

    if not available_accs:
        await safe_edit(
            callback.message,
            "🛍 **DO'KON**\n\n"
            "😔 Hozircha sotuvda akkauntlar mavjud emas.\n"
            "Tez orada yangilari qo'shiladi! 🔥",
            back_button()
        )
        await callback.answer()
        return

    kb = []
    for aid, a in available_accs:
        kb.append([InlineKeyboardButton(
            text=f"🎮 {a['game']} — {a['name']} ({format_money(int(a['price']))} so'm)",
            callback_data=f"select_acc_{aid}"
        )])
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main")])

    await safe_edit(
        callback.message,
        f"🛍 **DO'KON** ⚡️\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🟢 Mavjud akkauntlar: **{len(available_accs)} ta**\n\n"
        f"Kerakli akkauntni tanlang:",
        kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("select_acc_"))
async def buy_account_process(callback: CallbackQuery):
    aid = int(callback.data.split("_")[2])
    acc = database["accounts"].get(aid)
    user = callback.from_user
    user_id = user.id

    if not acc or acc["sold"]:
        await callback.answer("⚠️ Bu akkaunt allaqachon sotilgan!", show_alert=True)
        return

    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0, "ref_count": 0, "invited_by": None,
            "klent_code": f"klent{database['klent_counter']}", "used_promos": [],
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_spent": 0,
        }

    user_balance = database["users"][user_id]["balance"]
    price = int(acc["price"])

    if user_balance < price:
        await callback.answer(
            f"❌ Mablag' yetarli emas!\nSizda: {format_money(user_balance)} so'm\nNarxi: {format_money(price)} so'm",
            show_alert=True
        )
        return

    database["users"][user_id]["balance"] -= price
    database["users"][user_id]["total_spent"] += price
    acc["sold"] = True
    database["total_sales"] += price

    klent_code = database["users"][user_id]["klent_code"]

    text = (
        f"🎉 **AKKAUNT SOTIB OLINDI!** 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎮 O'yin: **{acc['game']}**\n"
        f"🏷 Nomi: **{acc['name']}**\n"
        f"💰 Narxi: **{format_money(price)} so'm**\n\n"
        f"📨 *Admin tez orada login va parolni yuboradi!*\n"
        f"🔖 Sizning kodingiz: `/{klent_code}`"
    )
    await safe_edit(callback.message, text, back_button())

    admin_text = (
        f"🛒 **YANGI AKKAUNT SOTIB OLINDI!** 🔔\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 Xaridor: **{user.full_name}**\n"
        f"🔗 @{user.username}\n"
        f"🆔 ID: `{user.id}`\n"
        f"🔖 KODI: `/{klent_code}`\n\n"
        f"🎮 O'yin: **{acc['game']}**\n"
        f"🏷 Nomi: **{acc['name']}**\n"
        f"💰 Narxi: **{format_money(price)} so'm**\n\n"
        f"⚠️ **LOGIN VA PAROLNI YUBORING:**\n"
        f"`/{klent_code} Login: xxx Parol: yyy`\n"
        f"yoki\n"
        f"`/user {user.id} Login: xxx Parol: yyy`"
    )

    await callback.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    await callback.answer("✅ Xarid muvaffaqiyatli!")


# ==================== ADMIN PANEL ====================
@router.callback_query(F.data == "admin_panel")
async def admin_panel_handler(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔️ Siz admin emassiz!", show_alert=True)
        return

    await safe_edit(
        callback.message,
        "🔐 **ADMIN PANEL** 🛡\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Xavfsizlik uchun maxfiy parolni kiriting:\n\n"
        "🔒 *Parol maxfiy saqlanadi*",
        cancel_button()
    )
    await state.set_state(AdminStates.waiting_for_password)
    await callback.answer()


@router.message(AdminStates.waiting_for_password)
async def check_admin_password(message: Message, state: FSMContext):
    entered_password = message.text

    try:
        await message.delete()
    except Exception:
        pass

    if entered_password == ADMIN_PASSWORD:
        await state.clear()
        await show_admin_dashboard(message)
    else:
        err_msg = await message.answer("❌ **Xato parol!** Qaytadan urinib ko'ring.")
        await asyncio.sleep(3)
        try:
            await err_msg.delete()
        except Exception:
            pass


async def show_admin_dashboard(message_or_callback, is_callback=False):
    total_users = len(database["users"])
    sold_accounts = sum(1 for a in database["accounts"].values() if a["sold"])
    total_accounts = len(database["accounts"])
    sold_cookies = sum(1 for c in database["cookies"].values() if c["sold"])
    total_cookies = len(database["cookies"])
    total_balance_all = sum(u["balance"] for u in database["users"].values())
    uptime_seconds = int(time.time() - bot_start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60

    stats_str = (
        f"📊 **STATISTIKA**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Foydalanuvchilar: **{total_users} ta**\n"
        f"🛒 Akkauntlar: **{sold_accounts}/{total_accounts}**\n"
        f"🍪 Cookie lar: **{sold_cookies}/{total_cookies}**\n"
        f"💰 Umumiy balans: **{format_money(total_balance_all)} so'm**\n"
        f"💵 Umumiy sotuv: **{format_money(database['total_sales'])} so'm**\n"
        f"💳 To'ldirishlar: **{format_money(database['total_topups'])} so'm**\n"
        f"⏱ Uptime: **{hours}s {minutes}d**\n"
    )

    kb = [
        [InlineKeyboardButton(text="📊 To'liq statistika", callback_data="admin_full_stats")],
        [
            InlineKeyboardButton(text="➕ Akkaunt qo'shish", callback_data="admin_add_acc"),
            InlineKeyboardButton(text="🗑 Akkauntlar", callback_data="admin_manage_accs"),
        ],
        [
            InlineKeyboardButton(text="🍪 Cookie qo'shish", callback_data="admin_add_cookie"),
            InlineKeyboardButton(text="🗑 Cookie lar", callback_data="admin_manage_cookies"),
        ],
        [InlineKeyboardButton(text="🎁 Promokod yaratish", callback_data="admin_create_promo")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users_list")],
        [InlineKeyboardButton(text="📢 Rassilka", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="back_to_main")],
    ]

    text = f"🔒 **PAROL TASDIQLANDI** ✅\n\nXush kelibsiz, **Samir**! 👑\n\n{stats_str}"

    if is_callback:
        await safe_edit(message_or_callback.message, text, kb)
    else:
        await message_or_callback.answer(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "admin_panel_back")
async def admin_panel_back(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await show_admin_dashboard(callback, is_callback=True)
    await callback.answer()


@router.callback_query(F.data == "admin_full_stats")
async def admin_full_stats(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    total_users = len(database["users"])
    total_balance = sum(u["balance"] for u in database["users"].values())
    total_spent = sum(u.get("total_spent", 0) for u in database["users"].values())
    top_users = sorted(
        database["users"].items(),
        key=lambda x: x[1].get("total_spent", 0),
        reverse=True
    )[:5]

    top_str = "🏆 **TOP 5 XARIDORLAR:**\n"
    if top_users:
        for i, (uid, u) in enumerate(top_users, 1):
            top_str += f"{i}. `{uid}` — {format_money(u.get('total_spent', 0))} so'm\n"
    else:
        top_str += "Hozircha yo'q\n"

    text = (
        f"📊 **TO'LIQ STATISTIKA**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Foydalanuvchilar: **{total_users}**\n"
        f"💰 Umumiy balans: **{format_money(total_balance)} so'm**\n"
        f"💸 Umumiy sarflangan: **{format_money(total_spent)} so'm**\n"
        f"💵 Sotuvlar: **{format_money(database['total_sales'])} so'm**\n"
        f"💳 To'ldirishlar: **{format_money(database['total_topups'])} so'm**\n\n"
        f"{top_str}"
    )
    kb = [[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel_back")]]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


# ==================== FOYDALANUVCHILAR RO'YXATI ====================
@router.callback_query(F.data == "admin_users_list")
async def admin_users_list(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    if not database["users"]:
        await safe_edit(callback.message, "👥 Hozircha foydalanuvchilar yo'q.", back_button("admin_panel_back"))
        await callback.answer()
        return

    text = f"👥 **FOYDALANUVCHILAR** ({len(database['users'])} ta)\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for uid, u in list(database["users"].items())[:50]:
        text += (
            f"🆔 `{uid}`\n"
            f"🔖 `/{u['klent_code']}`\n"
            f"💰 {format_money(u['balance'])} so'm\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
        )

    if len(database["users"]) > 50:
        text += f"\n*... va yana {len(database['users']) - 50} ta*"

    kb = [[InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel_back")]]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


# ==================== AKKAUNT QO'SHISH ====================
@router.callback_query(F.data == "admin_add_acc")
async def admin_add_acc(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await safe_edit(callback.message, "🎮 **AKKAUNT QO'SHISH**\n\nO'yin nomini kiriting (masalan: PUBG Mobile):", cancel_button("admin_panel_back"))
    await state.set_state(AdminStates.adding_account_game)
    await callback.answer()


@router.message(AdminStates.adding_account_game)
async def admin_get_game(message: Message, state: FSMContext):
    await state.update_data(game=message.text)
    await message.answer("🏷 Akkaunt sarlavhasini kiriting (masalan: M416 Glacier):")
    await state.set_state(AdminStates.adding_account_name)


@router.message(AdminStates.adding_account_name)
async def admin_get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("💰 Narxini raqamlarda kiriting (masalan: 50000):")
    await state.set_state(AdminStates.adding_account_price)


@router.message(AdminStates.adding_account_price)
async def admin_get_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return

    data = await state.get_data()
    acc_id = len(database["accounts"]) + 1
    while acc_id in database["accounts"]:
        acc_id += 1

    database["accounts"][acc_id] = {
        "game": data["game"],
        "name": data["name"],
        "price": message.text,
        "sold": False,
    }

    await state.clear()
    kb = [[InlineKeyboardButton(text="⚙️ Admin Panelga qaytish", callback_data="admin_panel_back")]]
    await message.answer(
        f"✅ **AKKAUNT QO'SHILDI!**\n\n"
        f"🎮 {data['game']}\n"
        f"🏷 {data['name']}\n"
        f"💰 {format_money(int(message.text))} so'm",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown",
    )


# ==================== AKKAUNTLARNI O'CHIRISH ====================
@router.callback_query(F.data == "admin_manage_accs")
async def admin_manage_accounts(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    if not database["accounts"]:
        await safe_edit(callback.message, "⚠️ Akkauntlar yo'q.", back_button("admin_panel_back"))
        await callback.answer()
        return

    kb = []
    for aid, a in database["accounts"].items():
        status = "✅" if a["sold"] else "🟢"
        kb.append([InlineKeyboardButton(
            text=f"{status} #{aid} {a['name']} — o'chirish",
            callback_data=f"delete_acc_{aid}"
        )])
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel_back")])

    await safe_edit(callback.message, "🗑 **AKKAUNTLARNI O'CHIRISH:**", kb)
    await callback.answer()


@router.callback_query(F.data.startswith("delete_acc_"))
async def admin_delete_account(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    aid = int(callback.data.split("_")[2])
    if aid in database["accounts"]:
        del database["accounts"][aid]
        await callback.answer("✅ O'chirildi!", show_alert=True)
    else:
        await callback.answer("⚠️ Topilmadi!", show_alert=True)
    await admin_manage_accounts(callback)


# ==================== COOKIE QO'SHISH ====================
@router.callback_query(F.data == "admin_add_cookie")
async def admin_add_cookie(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await safe_edit(callback.message, "🍪 **COOKIE QO'SHISH**\n\nCookie nomini kiriting:", cancel_button("admin_panel_back"))
    await state.set_state(AdminStates.adding_cookie_name)
    await callback.answer()


@router.message(AdminStates.adding_cookie_name)
async def admin_get_cookie_name(message: Message, state: FSMContext):
    await state.update_data(cookie_name=message.text)
    await message.answer("💰 Cookie narxini kiriting (raqamda):")
    await state.set_state(AdminStates.adding_cookie_price)


@router.message(AdminStates.adding_cookie_price)
async def admin_get_cookie_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam!")
        return
    await state.update_data(cookie_price=message.text)
    await message.answer("📝 Cookie tavsifini kiriting (yoki `-` yozing):")
    await state.set_state(AdminStates.adding_cookie_desc)


@router.message(AdminStates.adding_cookie_desc)
async def admin_get_cookie_desc(message: Message, state: FSMContext):
    desc = message.text if message.text != "-" else "—"
    data = await state.get_data()

    cid = len(database["cookies"]) + 1
    while cid in database["cookies"]:
        cid += 1

    database["cookies"][cid] = {
        "name": data["cookie_name"],
        "price": data["cookie_price"],
        "desc": desc,
        "sold": False,
    }

    await state.clear()
    kb = [[InlineKeyboardButton(text="⚙️ Admin Panelga qaytish", callback_data="admin_panel_back")]]
    await message.answer(
        f"✅ **COOKIE QO'SHILDI!** 🍪\n\n"
        f"🏷 {data['cookie_name']}\n"
        f"💰 {format_money(int(data['cookie_price']))} so'm\n"
        f"📝 {desc}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown",
    )


# ==================== COOKIE O'CHIRISH ====================
@router.callback_query(F.data == "admin_manage_cookies")
async def admin_manage_cookies(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    if not database["cookies"]:
        await safe_edit(callback.message, "⚠️ Cookie lar yo'q.", back_button("admin_panel_back"))
        await callback.answer()
        return

    kb = []
    for cid, c in database["cookies"].items():
        status = "✅" if c["sold"] else "🟢"
        kb.append([InlineKeyboardButton(
            text=f"{status} #{cid} {c['name']} — o'chirish",
            callback_data=f"delete_cookie_{cid}"
        )])
    kb.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel_back")])

    await safe_edit(callback.message, "🗑 **COOKIE LARNI O'CHIRISH:**", kb)
    await callback.answer()


@router.callback_query(F.data.startswith("delete_cookie_"))
async def admin_delete_cookie(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    cid = int(callback.data.split("_")[2])
    if cid in database["cookies"]:
        del database["cookies"][cid]
        await callback.answer("✅ O'chirildi!", show_alert=True)
    else:
        await callback.answer("⚠️ Topilmadi!", show_alert=True)
    await admin_manage_cookies(callback)


# ==================== PROMOKOD YARATISH ====================
@router.callback_query(F.data == "admin_create_promo")
async def admin_create_promo(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await safe_edit(callback.message, "🎁 **PROMOKOD YARATISH**\n\nPromokod nomini kiriting (masalan: SAMIR2026):", cancel_button("admin_panel_back"))
    await state.set_state(AdminStates.waiting_for_promo_code)
    await callback.answer()


@router.message(AdminStates.waiting_for_promo_code)
async def admin_get_promo_code(message: Message, state: FSMContext):
    promo_code = message.text.strip().upper()
    await state.update_data(promo_code=promo_code)
    await message.answer("💰 Promokod qiymatini kiriting (so'mda):")
    await state.set_state(AdminStates.waiting_for_promo_amount)


@router.message(AdminStates.waiting_for_promo_amount)
async def admin_get_promo_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam!")
        return
    await state.update_data(promo_amount=int(message.text))
    await message.answer("🔢 Limitni kiriting (necha kishi ishlatishi mumkin, 0 = cheksiz):")
    await state.set_state(AdminStates.waiting_for_promo_limit)


@router.message(AdminStates.waiting_for_promo_limit)
async def admin_get_promo_limit(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam!")
        return

    data = await state.get_data()
    promo_code = data["promo_code"]
    amount = data["promo_amount"]
    limit = int(message.text)

    database["promos"][promo_code] = {
        "amount": amount,
        "limit": limit,
        "used_count": 0,
    }

    await state.clear()
    kb = [[InlineKeyboardButton(text="⚙️ Admin Panelga qaytish", callback_data="admin_panel_back")]]
    limit_text = "cheksiz" if limit == 0 else f"{limit} ta"
    await message.answer(
        f"✅ **PROMOKOD YARATILDI!**\n\n"
        f"🎁 Kod: `{promo_code}`\n"
        f"💰 Qiymat: **{format_money(amount)} so'm**\n"
        f"🔢 Limit: **{limit_text}**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown",
    )


# ==================== RASILKA ====================
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await safe_edit(
        callback.message,
        "📢 **RASSILKA**\n\nBarcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni kiriting:\n\n"
        "📌 *Rasm, video yoki matn yuborishingiz mumkin*",
        cancel_button("admin_panel_back")
    )
    await state.set_state(AdminStates.waiting_for_broadcast)
    await callback.answer()


@router.message(AdminStates.waiting_for_broadcast)
async def admin_broadcast_send(message: Message, state: FSMContext):
    await state.clear()
    count = 0
    failed = 0
    for user_id in database["users"].keys():
        try:
            await message.send_copy(chat_id=user_id)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    kb = [[InlineKeyboardButton(text="⚙️ Admin Panelga qaytish", callback_data="admin_panel_back")]]
    await message.answer(
        f"✅ **RASSILKA TUGADI!**\n\n"
        f"✔️ Yuborildi: **{count}**\n"
        f"❌ Xato: **{failed}**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown",
    )


# ==================== /klent VA /user BUYRUQLARI ====================
@router.message(F.text.startswith("/klent"))
async def admin_manage_klent(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("⚠ Format:\n`/klent1 Salom`\n`/klent1 +40000`", parse_mode="Markdown")
        return

    klent_code_input = parts[0][1:]
    command_body = parts[1].strip()

    target_user_id = None
    target_user_data = None
    for uid, udata in database["users"].items():
        if udata["klent_code"] == klent_code_input:
            target_user_id = uid
            target_user_data = udata
            break

    if not target_user_id:
        await message.reply(f"❌ Topilmadi: `/{klent_code_input}`", parse_mode="Markdown")
        return

    cleaned_body = command_body.replace(" ", "")
    if cleaned_body.startswith("+") or cleaned_body.startswith("-") or cleaned_body.isdigit():
        try:
            amount = int(cleaned_body)
            target_user_data["balance"] += amount
            new_balance = target_user_data["balance"]

            await message.reply(
                f"✅ `/{klent_code_input}` balansi o'zgardi: **{amount:+,} so'm**\n"
                f"💰 Yangi balans: **{format_money(new_balance)} so'm**",
                parse_mode="Markdown"
            )
            try:
                await message.bot.send_message(
                    chat_id=target_user_id,
                    text=f"🎁 **BALANS O'ZGARDI!**\n\n"
                         f"O'zgarish: **{amount:+,} so'm**\n"
                         f"💰 Joriy balans: **{format_money(new_balance)} so'm**",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            return
        except ValueError:
            pass

    try:
        await message.bot.send_message(
            chat_id=target_user_id,
            text=f"📦 **SAMIR STORE Adminidan xabar:** 🔔\n\n{command_body}",
            parse_mode="Markdown"
        )
        await message.reply(f"✅ Xabar `/{klent_code_input}` ga yuborildi!")
    except Exception as e:
        await message.reply(f"❌ Xatolik: {e}")


@router.message(F.text.startswith("/user"))
async def admin_manage_user_id(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.reply("⚠ Format: `/user 123456789 +40000`", parse_mode="Markdown")
        return

    if not parts[1].isdigit():
        await message.reply("❌ ID faqat raqam!")
        return

    target_user_id = int(parts[1])
    command_body = parts[2].strip()

    if target_user_id not in database["users"]:
        await message.reply("❌ Bu ID ro'yxatdan o'tmagan!")
        return

    target_user_data = database["users"][target_user_id]
    cleaned_body = command_body.replace(" ", "")

    if cleaned_body.startswith("+") or cleaned_body.startswith("-") or cleaned_body.isdigit():
        try:
            amount = int(cleaned_body)
            target_user_data["balance"] += amount
            new_balance = target_user_data["balance"]

            await message.reply(
                f"✅ ID `{target_user_id}` balansi: **{amount:+,} so'm**\n"
                f"💰 Yangi: **{format_money(new_balance)} so'm**",
                parse_mode="Markdown"
            )
            try:
                await message.bot.send_message(
                    chat_id=target_user_id,
                    text=f"🎁 **BALANS O'ZGARDI!**\n\n"
                         f"O'zgarish: **{amount:+,} so'm**\n"
                         f"💰 Joriy balans: **{format_money(new_balance)} so'm**",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            return
        except ValueError:
            pass

    try:
        await message.bot.send_message(
            chat_id=target_user_id,
            text=f"📦 **SAMIR STORE Adminidan xabar:** 🔔\n\n{command_body}",
            parse_mode="Markdown"
        )
        await message.reply(f"✅ Xabar `{target_user_id}` ga yuborildi!")
    except Exception as e:
        await message.reply(f"❌ Xatolik: {e}")


# ==================== BOTNI ISHGA TUSHIRISH ====================
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🏠 Asosiy menyu"),
        BotCommand(command="help", description="ℹ️ Yordam"),
    ]
    await bot.set_my_commands(commands)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ **YORDAM**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "• `/start` — Asosiy menyu\n"
        "• `/help` — Yordam\n\n"
        "📞 **Qo'llab-quvvatlash:** @samir_admin",
        parse_mode="Markdown"
    )


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await set_bot_commands(bot)

    print("╔══════════════════════════════════╗")
    print("║   🚀 SAMIR STORE PREMIUM BOT      ║")
    print("║   ✅ Bot muvaffaqiyatli ishga     ║")
    print("║      tushdi!                     ║")
    print(f"║   👑 Admin: {ADMIN_ID}         ║")
    print("╚══════════════════════════════════╝")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
