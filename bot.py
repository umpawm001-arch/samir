import asyncio
import logging
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
)

# === SOZLAMALAR ===
TOKEN = "8643758285:AAFL4Cv-mpsqPTJJkWTyhv5rWh1l6N5VCL8"
ADMIN_ID = 8223721716
ADMIN_PASSWORD = "samir1234"
CARD_NUMBER = "9860 1666 5619 0666"
CARD_HOLDER = "K.U"

# === STIKERLAR ===
MAIN_STICKER_ID = "CAACAgIAAxkBAAER9fBqupiGfIbVkhas-99iIh30slYiFwAClmQAAoBKwEoF-PhllH7s0z0E"
TOPUP_STICKER_ID = "CAACAgEAAxkBAAER9fRquplZXvIClUoY0Y-Q4Fcy2eUYrgACAwMAAoOo4EQ3ZTysFteinT0E"
BUY_STICKER_ID = "CAACAgEAAxkBAAER9fZqupmLvTzj6U3nF7XD_Nd_TIdzlAACTAUAAmT_sEfz8RU-1D-ilT0E"
PROFILE_STICKER_ID = "CAACAgIAAxkBAAER9fhqupnu08NKiRCp9GUnQ-ybm7N-hwACyUoAAi7LQEvGM2FguGcKTT0E"
REF_STICKER_ID = "CAACAgIAAxkBAAER9fpquponN0buSTH4DEyhzbRSF8Z7nAACSAIAAladvQoc9XL43CkU0D0E"
ADMIN_STICKER_ID = "CAACAgIAAxkBAAER9fxquppgM0xdB3qFoeZcfXLiWcV0xwAC9wADVp29CgtyJB1I9A0wPQQ"
COOKIE_STICKER_ID = "CAACAgIAAxkBAAER9fBqupiGfIbVkhas-99iIh30slYiFwAClmQAAoBKwEoF-PhllH7s0z0E"

logging.basicConfig(level=logging.INFO)
router = Router()


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


class BuyStates(StatesGroup):
    waiting_for_custom_amount = State()
    waiting_for_receipt = State()


class BroadcastStates(StatesGroup):
    waiting_for_broadcast = State()


class UserStates(StatesGroup):
    waiting_for_activate_promo = State()


database = {
    "accounts": {},
    "cookies": {},
    "users": {},
    "promos": {},
    "klent_counter": 0
}


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


def main_menu(user_id):
    kb = [
        [InlineKeyboardButton(text="🛍 Do'konni ochish", callback_data="buy_accounts")],
        [InlineKeyboardButton(text="🍪 Cookie Accs", callback_data="cookie_list")],
        [
            InlineKeyboardButton(text="👤 Profil kabineti", callback_data="profile"),
            InlineKeyboardButton(text="💳 Balansni to'ldirish", callback_data="top_up"),
        ],
        [InlineKeyboardButton(text="🪙 Referal dasturi (Bonus)", callback_data="referral")],
    ]
    if user_id == ADMIN_ID:
        kb.append([InlineKeyboardButton(text="⚙️ Admin boshqaruv paneli", callback_data="admin_panel")])
    return kb


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
        }

    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        ref_id = int(args[1])
        if ref_id != user_id and ref_id in database["users"]:
            if database["users"][user_id]["invited_by"] is None:
                database["users"][user_id]["invited_by"] = ref_id
                database["users"][ref_id]["ref_count"] += 1
                database["users"][ref_id]["balance"] += 3000

    await message.answer_sticker(sticker=MAIN_STICKER_ID)
    caption = (
        f"✨ **SAMIR STORE - ASOSIY MENYU** 🚀\n\n"
        f"👋 Salom, **{name}**! 💎\n\n"
        f"🔥 Bu PUBG Mobile va o'yin akkauntlari rasmiy do'koni boti! Kerakli bo'limni tanlang. ⚡️"
    )
    await message.answer(caption, reply_markup=InlineKeyboardMarkup(inline_keyboard=main_menu(user_id)), parse_mode="Markdown")


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    name = callback.from_user.first_name

    caption = (
        f"✨ **SAMIR STORE - ASOSIY MENYU** 🚀\n\n"
        f"👋 Salom, **{name}**! 💎\n\n"
        f"🔥 Bu PUBG Mobile va o'yin akkauntlari rasmiy do'koni boti! Kerakli bo'limni tanlang. ⚡️"
    )
    await safe_edit(callback.message, caption, main_menu(user_id))
    await callback.answer()


# ============ 🍪 COOKIE ACCS - FOYDALANUVCHI TOMONI ============
@router.callback_query(F.data == "cookie_list")
async def cookie_list(callback: CallbackQuery):
    available = [(cid, c) for cid, c in database["cookies"].items() if not c["sold"]]

    if not available:
        kb = [[InlineKeyboardButton(text="⬅️ Bosh menyuga qaytish", callback_data="back_to_main")]]
        await safe_edit(callback.message, "🍪 Hozircha sotuvda cookie akkauntlar mavjud emas. Tez orada qo'shiladi!", kb)
        await callback.answer()
        return

    kb = []
    for cid, c in available:
        kb.append([InlineKeyboardButton(
            text=f"🍪 {c['name']} — {c['price']} so'm",
            callback_data=f"select_cookie_{cid}"
        )])
    kb.append([InlineKeyboardButton(text="⬅️ Bosh menyuga qaytish", callback_data="back_to_main")])

    await safe_edit(
        callback.message,
        "🍪 **SAMIR STORE - SOTUVDAGI COOKIE AKKAUNTLAR:**\n\nKerakli cookie akkauntni tanlang:",
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
            "klent_code": f"klent{database['klent_counter']}", "used_promos": []
        }

    user_balance = database["users"][user_id]["balance"]
    price = int(c["price"])

    if user_balance < price:
        await callback.answer(
            f"❌ Mablag'ingiz yetarli emas!\nSizda: {user_balance:,} so'm | Narxi: {price:,} so'm",
            show_alert=True
        )
        return

    database["users"][user_id]["balance"] -= price
    c["sold"] = True

    klent_code = database["users"][user_id]["klent_code"]

    text = (
        f"🎉 **Tabriklaymiz! Cookie akkaunt muvaffaqiyatli sotib olindi!** 🍪\n\n"
        f"🏷 Nomi: {c['name']}\n"
        f"📝 Tavsif: {c.get('desc', '—')}\n\n"
        f"📨 *SAMIR STORE admini tez orada cookie faylini shu bot orqali sizga yuboradi!*"
    )
    kb = [[InlineKeyboardButton(text="⬅️ Bosh menyuga qaytish", callback_data="back_to_main")]]
    await safe_edit(callback.message, text, kb)

    admin_text = (
        f"🍪 **SAMIR STORE - YANGI COOKIE SOTIB OLINDI!** 🔔\n\n"
        f"👤 Xaridor: {user.full_name} (@{user.username})\n"
        f"🔖 KODI: `/{klent_code}` (ID: `{user.id}`)\n"
        f"🏷 Cookie nomi: {c['name']}\n"
        f"📝 Tavsif: {c.get('desc', '—')}\n"
        f"💰 Narxi: **{price:,} so'm**\n\n"
        f"⚠️ **COOKIE QANDAY YUBORILADI:**\n"
        f"Quyidagi buyruq orqali ushbu mijozga cookie yuboring:\n"
        f"`/{klent_code} [cookie matni yoki fayl]`\n"
        f"Yoki:\n"
        f"`/user {user.id} [cookie matni]`\n\n"
        f"Misol:\n"
        f"`/{klent_code} Cookie: abc123xyz...`"
    )

    await callback.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    await callback.answer()


# ============ PROFIL ============
@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0, "ref_count": 0, "invited_by": None,
            "klent_code": f"klent{database['klent_counter']}", "used_promos": []
        }

    user = database["users"][user_id]

    text = (
        f"👤 **SAMIR STORE - SHAXSIY KABINET** 💎\n\n"
        f"🆔 Telegram ID: `{user_id}`\n"
        f"🔖 Sizning maxsus kodingiz: `/{user['klent_code']}`\n"
        f"💰 Hamyon balansi: `✨ {user['balance']:,} so'm`\n"
        f"👥 Taklif qilingan do'stlar: `{user['ref_count']} ta`\n\n"
        f"⚡️ Xavfsizlik darajasi: Yuqori 🔒"
    )
    kb = [
        [InlineKeyboardButton(text="🎁 Promokod kiritish", callback_data="enter_promo")],
        [InlineKeyboardButton(text="⬅️ Bosh menyuga qaytish", callback_data="back_to_main")]
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data == "enter_promo")
async def enter_promo_handler(callback: CallbackQuery, state: FSMContext):
    kb = [[InlineKeyboardButton(text="❌ Bekor qilish", callback_data="profile")]]
    await safe_edit(callback.message, "🎁 **Promokod kiritish:**\n\nIltimos, bot uchun maxsus promokodni yuboring:", kb)
    await state.set_state(UserStates.waiting_for_activate_promo)
    await callback.answer()


@router.message(UserStates.waiting_for_activate_promo)
async def activate_promo_process(message: Message, state: FSMContext):
    user_id = message.from_user.id
    code = message.text.strip().upper()
    await state.clear()

    if code not in database["promos"]:
        await message.answer("❌ Bunday promokod mavjud emas yoki eskirgan!",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                 InlineKeyboardButton(text="👤 Profilga qaytish", callback_data="profile")
                             ]]))
        return

    if user_id not in database["users"]:
        database["klent_counter"] += 1
        database["users"][user_id] = {
            "balance": 0, "ref_count": 0, "invited_by": None,
            "klent_code": f"klent{database['klent_counter']}", "used_promos": []
        }

    user = database["users"][user_id]

    if code in user["used_promos"]:
        await message.answer("⚠️ Siz bu promokoddan allaqachon foylangansiz!",
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                 InlineKeyboardButton(text="👤 Profilga qaytish", callback_data="profile")
                             ]]))
        return

    promo_amount = database["promos"][code]
    user["balance"] += promo_amount
    user["used_promos"].append(code)

    await message.answer(
        f"🎉 **Tabriklaymiz!** Promokod muvaffaqiyatli faollashtirildi.\nBalansingizga **{promo_amount:,} so'm** qo'shildi! 💎",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="👤 Profilga qaytish", callback_data="profile")
        ]])
    )


@router.callback_query(F.data == "referral")
async def show_referral(callback: CallbackQuery):
    user_id = callback.from_user.id
    bot_info = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"

    text = (
        f"🪙 **REFERAL DASTURI** 🎁\n\n"
        f"Do'stlaringizni taklif qiling va har bir do'stingiz uchun **3,000 so'm** kafolatlangan bonus oling! 🚀\n\n"
        f"🔗 **Sizning shaxsiy taklif havolangiz:**\n`{ref_link}`"
    )
    kb = [[InlineKeyboardButton(text="⬅️ Bosh menyuga qaytish", callback_data="back_to_main")]]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data == "top_up")
async def top_up_balance(callback: CallbackQuery, state: FSMContext):
    text = (
        f"💳 **HISOBNI TO'LDIRISH** ⚡️\n\n"
        f"Iltimos, hisobingizga qancha miqdorda pul o'tkazmoqchiligingizni quyidagilardan tanlang:"
    )
    kb = [
        [
            InlineKeyboardButton(text="💵 10,000 so'm", callback_data="amount_10000"),
            InlineKeyboardButton(text="💵 20,000 so'm", callback_data="amount_20000"),
        ],
        [
            InlineKeyboardButton(text="💵 30,000 so'm", callback_data="amount_30000"),
            InlineKeyboardButton(text="💵 40,000 so'm", callback_data="amount_40000"),
        ],
        [
            InlineKeyboardButton(text="💵 50,000 so'm", callback_data="amount_50000"),
            InlineKeyboardButton(text="✍️ Boshqa summa", callback_data="amount_custom"),
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_to_main")]
    ]
    await safe_edit(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data.startswith("amount_"))
async def process_amount_selection(callback: CallbackQuery, state: FSMContext):
    data_value = callback.data.split("_")[1]

    if data_value == "custom":
        kb = [[InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_to_main")]]
        await safe_edit(callback.message, "✍️ O'zingiz xohlagan summani raqamlarda kiriting (masalan: `25000`):", kb)
        await state.set_state(BuyStates.waiting_for_custom_amount)
        await callback.answer()
        return

    amount = int(data_value)
    await state.update_data(selected_amount=amount)

    await send_card_details_edit(callback, amount)
    await state.set_state(BuyStates.waiting_for_receipt)
    await callback.answer()


async def send_card_details_edit(callback: CallbackQuery, amount: int):
    text = (
        f"💳 **TO'LOV KARTASI VA OGOHLANTIRISH** ⚠️\n\n"
        f"Tanlangan summa: **{amount:,} so'm** 💎\n\n"
        f"Quyidagi karta raqamiga pul o'tkazing:\n"
        f"💳 **Karta:** `{CARD_NUMBER}`\n"
        f"👤 **Karta egasi:** `{CARD_HOLDER}`\n\n"
        f"🚨 **QAT'IY OGOHLANTIRISH!**\n"
        f"Agar tanlagan summadan **kam pul** tashlagan bo'lsangiz, **pulingizga kuyasiz**!\n\n"
        f"📸 To'lovni amalga oshirib bo'lgach, **to'lov chekini (skrinshot)** shu botga yuboring! 📥"
    )
    kb = [[InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_to_main")]]
    await safe_edit(callback.message, text, kb)


@router.message(BuyStates.waiting_for_custom_amount)
async def process_custom_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting! Qaytadan urinib ko'ring:")
        return

    amount = int(message.text)
    await state.update_data(selected_amount=amount)

    text = (
        f"💳 **TO'LOV KARTASI VA OGOHLANTIRISH** ⚠️\n\n"
        f"Tanlangan summa: **{amount:,} so'm** 💎\n\n"
        f"Quyidagi karta raqamiga pul o'tkazing:\n"
        f"💳 **Karta:** `{CARD_NUMBER}`\n"
        f"👤 **Karta egasi:** `{CARD_HOLDER}`\n\n"
        f"🚨 **QAT'IY OGOHLANTIRISH!**\n"
        f"Agar tanlagan summadan **kam pul** tashlagan bo'lsangiz, **pulingizga kuyasiz**!\n\n"
        f"📸 To'lovni amalga oshirib bo'lgach, **to'lov chekini (skrinshot)** shu botga yuboring! 📥"
    )
    kb = [[InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_to_main")]]
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")
    await state.set_state(BuyStates.waiting_for_receipt)


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
            "klent_code": f"klent{database['klent_counter']}", "used_promos": []
        }

    klent_code = database["users"][user.id]["klent_code"]

    text = (
        f"📥 **SAMIR STORE - YANGI TO'LOV CHEKI!** 🔔\n\n"
        f"👤 Xaridor: {user.full_name} (@{user.username})\n"
        f"🔖 KODI: `/{klent_code}` (ID: `{user.id}`)\n"
        f"💰 Tanlagan summasi: **{selected_amount:,} so'm**"
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
    await message.answer(f"✅ **Chekingiz adminga yuborildi!** Sizning kodingiz: `/{klent_code}`. Tez orada tekshiriladi. 🚀")
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
            caption=(callback.message.caption or "") + f"\n\n**STATUS: ✅ TASDIQLANDI (+{added_amount:,} so'm)** 🎉",
            parse_mode="Markdown",
        )
    except Exception:
        pass

    if user_id in database["users"]:
        database["users"][user_id]["balance"] += added_amount

    await callback.bot.send_message(
        chat_id=user_id,
        text=f"✅ **Tabriklaymiz!** SAMIR STORE admini to'lov chekingizni tasdiqladi va balansingizga `{added_amount:,} so'm` qo'shildi! 🎉",
        parse_mode="Markdown",
    )
    await callback.answer("To'lov tasdiqlandi!")


@router.callback_query(F.data.startswith("topup_no_"))
async def topup_reject(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    user_id = int(callback.data.split("_")[2])

    try:
        await callback.message.edit_caption(
            caption=(callback.message.caption or "") + "\n\n**STATUS: ❌ RAD ETILDI**",
            parse_mode="Markdown",
        )
    except Exception:
        pass

    await callback.bot.send_message(
        chat_id=user_id,
        text="❌ Chekingiz rad etildi. Sabab: Soxta chek yoki miqdor tanlangan summadan kam.",
    )
    await callback.answer("Rad etildi!")


# ============ DO'KON ============
@router.callback_query(F.data == "buy_accounts")
async def list_accounts(callback: CallbackQuery):
    available_accs = [(acc_id, acc) for acc_id, acc in database["accounts"].items() if not acc["sold"]]

    if not available_accs:
        kb = [[InlineKeyboardButton(text="⬅️ Bosh menyuga qaytish", callback_data="back_to_main")]]
        await safe_edit(callback.message, "😔 Hozircha sotuvda akkauntlar mavjud emas. Tez orada yangilari qo'shiladi! 🔥", kb)
        await callback.answer()
        return

    kb = []
    for acc_id, acc in available_accs:
        kb.append([InlineKeyboardButton(text=f"🎮 {acc['game']} — {acc['name']} ({acc['price']} so'm)", callback_data=f"select_acc_{acc_id}")])
    kb.append([InlineKeyboardButton(text="⬅️ Bosh menyuga qaytish", callback_data="back_to_main")])

    await safe_edit(callback.message, "🛍 **SAMIR STORE - SOTUVDAGI AKKAUNTLAR:** ⚡️", kb)
    await callback.answer()


@router.callback_query(F.data.startswith("select_acc_"))
async def buy_account_process(callback: CallbackQuery):
    acc_id = int(callback.data.split("_")[2])
    acc = database["accounts"].get(acc_id)
    user = callback.from_user
    user_id = user.id

    if not acc or acc["sold"]:
        await callback.answer("⚠️ Bu akkaunt allaqachon sotilgan!", show_alert=True)
        return

    user_balance = database["users"][user_id]["balance"]
    price = int(acc["price"])

    if user_balance < price:
        await callback.answer(f"❌ Mablag'ingiz yetarli emas!\nSizda: {user_balance:,} so'm | Narxi: {price:,} so'm", show_alert=True)
        return

    database["users"][user_id]["balance"] -= price
    acc["sold"] = True

    klent_code = database["users"][user_id]["klent_code"]

    text = (
        f"🎉 **Tabriklaymiz! Akkaunt muvaffaqiyatli sotib olindi!** 👑\n\n"
        f"🎮 O'yin: {acc['game']}\n"
        f"🏷 Nomi: {acc['name']}\n\n"
        f"📨 *SAMIR STORE admini tez orada tekshirib, login va parolni shu bot orqali sizga yuboradi!*"
    )
    kb = [[InlineKeyboardButton(text="⬅️ Bosh menyuga qaytish", callback_data="back_to_main")]]
    await safe_edit(callback.message, text, kb)

    admin_text = (
        f"🛒 **SAMIR STORE - YANGI AKKAUNT SOTIB OLINDI!** 🔔\n\n"
        f"👤 Xaridor: {user.full_name} (@{user.username})\n"
        f"🔖 KODI: `/{klent_code}` (ID: `{user.id}`)\n"
        f"🎮 O'yin: {acc['game']}\n"
        f"🏷 Nomi: {acc['name']}\n"
        f"💰 Narxi: **{price:,} so'm**\n\n"
        f"⚠️ *Iltimos, ushbu mijozga akkaunt login va parolini yuboring!*\n"
        f"Misol uchun:\n`/{klent_code} Login: ... Parol: ...` yoki `/user {user.id} Login: ... Parol: ...`"
    )

    await callback.bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
    await callback.answer()


# ============ ADMIN PANEL ============
@router.callback_query(F.data == "admin_panel")
async def admin_panel_handler(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    kb = [[InlineKeyboardButton(text="❌ Chiqish", callback_data="back_to_main")]]
    await safe_edit(callback.message, "🔐 **Admin panel xavfsizlik tizimi** 🛡\n\nIltimos, maxfiy parolni kiriting:", kb)
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
    sold_accounts = sum(1 for acc in database["accounts"].values() if acc["sold"])
    total_accounts = len(database["accounts"])
    sold_cookies = sum(1 for c in database["cookies"].values() if c["sold"])
    total_cookies = len(database["cookies"])
    total_balance_all = sum(udata["balance"] for udata in database["users"].values())

    stats_str = (
        f"📊 **SAMIR STORE STATISTIKASI:**\n"
        f"👥 Jami foydalanuvchilar: `{total_users} ta`\n"
        f"🛒 Sotilgan akkauntlar: `{sold_accounts}/{total_accounts} ta`\n"
        f"🍪 Sotilgan cookie: `{sold_cookies}/{total_cookies} ta`\n"
        f"💰 Foydalanuvchilar umumiy balansi: `{total_balance_all:,} so'm`\n\n"
    )

    klent_list_str = "📋 **Mijozlar ro'yxati va balanslari:**\n"
    if database["users"]:
        for uid, udata in database["users"].items():
            klent_list_str += f"• ID: `{uid}` (Kodi: `/{udata['klent_code']}`) — Balans: **{udata['balance']:,} so'm**\n"
    else:
        klent_list_str += "Hozircha mijozlar yo'q.\n"

    klent_list_str += (
        "\n💡 **Admin buyruqlari:**\n"
        "• Balansni o'zgartirish: `/[klent_kodi] +[summa]` (masalan: `/klent1 +40000`)\n"
        "• Xabar yuborish: `/[klent_kodi] Salom` yoki `/user [ID] Salom`"
    )

    kb = [
        [InlineKeyboardButton(text="➕ Akkaunt qo'shish", callback_data="admin_add_acc")],
        [InlineKeyboardButton(text="🗑 Akkauntni o'chirish", callback_data="admin_manage_accs")],
        [InlineKeyboardButton(text="🍪 Cookie qo'shish", callback_data="admin_add_cookie")],
        [InlineKeyboardButton(text="🗑 Cookie o'chirish", callback_data="admin_manage_cookies")],
        [InlineKeyboardButton(text="🎁 Promokod yaratish", callback_data="admin_create_promo")],
        [InlineKeyboardButton(text="📢 Xabar tarqatish (Rassilka)", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="back_to_main")],
    ]

    text = f"🔒 **Parol muvaffaqiyatli tasdiqlandi!** Xush kelibsiz, Samir. 👑\n\n{stats_str}\n{klent_list_str}"

    if is_callback:
        await safe_edit(message_or_callback.message, text, kb)
    else:
        await message_or_callback.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")


# ============ PROMOKOD YARATISH ============
@router.callback_query(F.data == "admin_create_promo")
async def admin_create_promo_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    kb = [[InlineKeyboardButton(text="⬅️ Bekor qilish", callback_data="admin_panel_back")]]
    await safe_edit(callback.message, "🎁 Yangi promokod nomini kiriting (masalan: `SAMIR2026`):", kb)
    await state.set_state(AdminStates.waiting_for_promo_code)
    await callback.answer()


@router.message(AdminStates.waiting_for_promo_code)
async def admin_get_promo_code(message: Message, state: FSMContext):
    promo_code = message.text.strip().upper()
    await state.update_data(promo_code=promo_code)
    await message.answer("💰 Promokod qiymatini so'mda kiriting (faqat raqam, masalan: `5000`):")
    await state.set_state(AdminStates.waiting_for_promo_amount)


@router.message(AdminStates.waiting_for_promo_amount)
async def admin_get_promo_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return

    amount = int(message.text)
    data = await state.get_data()
    promo_code = data["promo_code"]

    database["promos"][promo_code] = amount
    await state.clear()

    kb = [[InlineKeyboardButton(text="⚙️ Admin Panelga qaytish", callback_data="admin_panel_back")]]
    await message.answer(
        f"✅ **Muvaffaqiyatli yaratildi!**\n\n🎁 Promokod: `{promo_code}`\n💵 Qiymati: **{amount:,} so'm**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown"
    )


# ============ AKKAUNTLARNI BOSHQARISH ============
@router.callback_query(F.data == "admin_manage_accs")
async def admin_manage_accounts(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    if not database["accounts"]:
        kb = [[InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_panel_back")]]
        await safe_edit(callback.message, "⚠️ Hozircha bazada hech qanday akkaunt mavjud emas.", kb)
        await callback.answer()
        return

    kb = []
    for acc_id, acc in database["accounts"].items():
        kb.append([InlineKeyboardButton(text=f"🗑 #{acc_id} {acc['name']} — o'chirish", callback_data=f"delete_acc_{acc_id}")])

    kb.append([InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_panel_back")])

    await safe_edit(callback.message, "🗑 **Akkauntlarni boshqarish va o'chirish:**\nO'chirmoqchi bo'lgan akkauntni tanlang:", kb)
    await callback.answer()


@router.callback_query(F.data.startswith("delete_acc_"))
async def admin_delete_account(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    acc_id = int(callback.data.split("_")[2])
    if acc_id in database["accounts"]:
        del database["accounts"][acc_id]
        await callback.answer("✅ Akkaunt muvaffaqiyatli o'chirildi!", show_alert=True)
    else:
        await callback.answer("⚠️ Bu akkaunt topilmadi.", show_alert=True)

    await admin_manage_accounts(callback)


@router.callback_query(F.data == "admin_panel_back")
async def admin_panel_back_handler(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await show_admin_dashboard(callback, is_callback=True)
    await callback.answer()


# ============ 🍪 COOKIE QO'SHISH (ADMIN) ============
@router.callback_query(F.data == "admin_add_cookie")
async def admin_add_cookie(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    kb = [[InlineKeyboardButton(text="⬅️ Bekor qilish", callback_data="admin_panel_back")]]
    await safe_edit(callback.message, "🍪 Cookie akkaunt nomini kiriting (masalan: PUBG Cookie #1):", kb)
    await state.set_state(AdminStates.adding_cookie_name)
    await callback.answer()


@router.message(AdminStates.adding_cookie_name)
async def admin_get_cookie_name(message: Message, state: FSMContext):
    await state.update_data(cookie_name=message.text)
    await message.answer("💰 Cookie narxini raqamlarda kiriting (masalan: 30000):")
    await state.set_state(AdminStates.adding_cookie_price)


@router.message(AdminStates.adding_cookie_price)
async def admin_get_cookie_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Faqat raqam kiriting!")
        return
    await state.update_data(cookie_price=message.text)
    await message.answer("📝 Cookie tavsifini kiriting (yoki `-` yozing, tavsif kerak bo'lmasa):")
    await state.set_state(AdminStates.adding_cookie_desc)


@router.message(AdminStates.adding_cookie_desc)
async def admin_get_cookie_desc(message: Message, state: FSMContext):
    desc = message.text if message.text != "-" else "—"
    data = await state.get_data()

    cookie_id = len(database["cookies"]) + 1
    while cookie_id in database["cookies"]:
        cookie_id += 1

    database["cookies"][cookie_id] = {
        "name": data["cookie_name"],
        "price": data["cookie_price"],
        "desc": desc,
        "sold": False,
    }

    await state.clear()
    kb = [[InlineKeyboardButton(text="⚙️ Admin Panelga qaytish", callback_data="admin_panel_back")]]
    await message.answer(
        f"✅ **Cookie akkaunt qo'shildi!** 🍪\n\n"
        f"🏷 Nomi: {data['cookie_name']}\n"
        f"💰 Narxi: {int(data['cookie_price']):,} so'm\n"
        f"📝 Tavsif: {desc}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown",
    )


# ============ 🍪 COOKIE O'CHIRISH (ADMIN) ============
@router.callback_query(F.data == "admin_manage_cookies")
async def admin_manage_cookies(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    if not database["cookies"]:
        kb = [[InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_panel_back")]]
        await safe_edit(callback.message, "⚠️ Hozircha bazada hech qanday cookie mavjud emas.", kb)
        await callback.answer()
        return

    kb = []
    for cid, c in database["cookies"].items():
        status = "✅ sotilgan" if c["sold"] else "🟢 mavjud"
        kb.append([InlineKeyboardButton(
            text=f"🗑 #{cid} {c['name']} ({status}) — o'chirish",
            callback_data=f"delete_cookie_{cid}"
        )])

    kb.append([InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin_panel_back")])

    await safe_edit(callback.message, "🗑 **Cookie akkauntlarni boshqarish va o'chirish:**\nO'chirmoqchi bo'lgan cookie ni tanlang:", kb)
    await callback.answer()


@router.callback_query(F.data.startswith("delete_cookie_"))
async def admin_delete_cookie(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    cid = int(callback.data.split("_")[2])
    if cid in database["cookies"]:
        del database["cookies"][cid]
        await callback.answer("✅ Cookie muvaffaqiyatli o'chirildi!", show_alert=True)
    else:
        await callback.answer("⚠️ Bu cookie topilmadi.", show_alert=True)

    await admin_manage_cookies(callback)


# ============ AKKAUNT QO'SHISH (ADMIN) ============
@router.callback_query(F.data == "admin_add_acc")
async def admin_add_acc(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    kb = [[InlineKeyboardButton(text="⬅️ Bekor qilish", callback_data="admin_panel_back")]]
    await safe_edit(callback.message, "🎮 O'yin nomini kiriting (masalan: PUBG Mobile):", kb)
    await state.set_state(AdminStates.adding_account_game)
    await callback.answer()


@router.message(AdminStates.adding_account_game)
async def admin_get_game(message: Message, state: FSMContext):
    await state.update_data(game=message.text)
    await message.answer("🏷 Akkaunt sarlavhasi yoki nomini kiriting (masalan: M416 Glacier):")
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
        "✅ **Ajoyib! Akkaunt SAMIR STORE do'koniga qo'shildi.** 🚀\n*(Foydalanuvchi uni sotib olgandagina sizga xabar keladi)*",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown",
    )


# ============ RASILKA ============
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    kb = [[InlineKeyboardButton(text="⬅️ Bekor qilish", callback_data="admin_panel_back")]]
    await safe_edit(callback.message, "📢 Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni kiriting:", kb)
    await state.set_state(BroadcastStates.waiting_for_broadcast)
    await callback.answer()


@router.message(BroadcastStates.waiting_for_broadcast)
async def admin_broadcast_send(message: Message, state: FSMContext):
    await state.clear()
    count = 0
    for user_id in database["users"].keys():
        try:
            await message.send_copy(chat_id=user_id)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    kb = [[InlineKeyboardButton(text="⚙️ Admin Panelga qaytish", callback_data="admin_panel_back")]]
    await message.answer(
        f"✅ Xabar muvaffaqiyatli **{count} ta** foydalanuvchiga yetkazildi! 🚀",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
        parse_mode="Markdown",
    )


# ============ KLENT KODI ORQALI XABAR / BALANS ============
@router.message(F.text.startswith("/klent"))
async def admin_manage_klent(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("⚠ Xatolik! Format:\n• Xabar yuborish: `/klent1 Salom`\n• Balans qo'shish: `/klent1 +40000`", parse_mode="Markdown")
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
                f"✅ `/{klent_code_input}` (ID: `{target_user_id}`) balansiga **{amount:+,} so'm** qo'shildi!\n"
                f"💰 Yangi balans: **{new_balance:,} so'm**",
                parse_mode="Markdown"
            )
            try:
                await message.bot.send_message(
                    chat_id=target_user_id,
                    text=f"🎁 **SAMIR STORE admini balansingizni o'zgartirdi!**\n\n"
                         f"O'zgarish: **{amount:+,} so'm**\n"
                         f"💰 Joriy balansingiz: **{new_balance:,} so'm** 🎉",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            return
        except ValueError:
            pass

    try:
        await message.bot.send_message(chat_id=target_user_id, text=f"📦 **SAMIR STORE Adminidan xabar:** 🔔\n\n`{command_body}`", parse_mode="Markdown")
        await message.reply(f"✅ Xabar `/{klent_code_input}` ga yuborildi! 🚀")
    except Exception as e:
        await message.reply(f"❌ Xatolik yuz berdi: {e}")


@router.message(F.text.startswith("/user"))
async def admin_manage_user_id(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.reply("⚠ Xatolik! Format: `/user 123456789 +40000` yoki `/user 123456789 Salom`", parse_mode="Markdown")
        return

    if not parts[1].isdigit():
        await message.reply("❌ ID faqat raqamlardan iborat bo'lishi kerak!")
        return

    target_user_id = int(parts[1])
    command_body = parts[2].strip()

    if target_user_id not in database["users"]:
        await message.reply("❌ Bu ID egasi botda ro'yxatdan o'tmagan!")
        return

    target_user_data = database["users"][target_user_id]
    cleaned_body = command_body.replace(" ", "")

    if cleaned_body.startswith("+") or cleaned_body.startswith("-") or cleaned_body.isdigit():
        try:
            amount = int(cleaned_body)
            target_user_data["balance"] += amount
            new_balance = target_user_data["balance"]

            await message.reply(
                f"✅ ID: `{target_user_id}` balansiga **{amount:+,} so'm** qo'shildi!\n"
                f"💰 Yangi balans: **{new_balance:,} so'm**",
                parse_mode="Markdown"
            )
            try:
                await message.bot.send_message(
                    chat_id=target_user_id,
                    text=f"🎁 **SAMIR STORE admini balansingizni o'zgartirdi!**\n\n"
                         f"O'zgarish: **{amount:+,} so'm**\n"
                         f"💰 Joriy balansingiz: **{new_balance:,} so'm** 🎉",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            return
        except ValueError:
            pass

    try:
        await message.bot.send_message(chat_id=target_user_id, text=f"📦 **SAMIR STORE Adminidan xabar:** 🔔\n\n`{command_body}`", parse_mode="Markdown")
        await message.reply(f"✅ Xabar `{target_user_id}` ID egasiga yuborildi! 🚀")
    except Exception as e:
        await message.reply(f"❌ Xatolik yuz berdi: {e}")


# ============ BOTNI ISHGA TUSHIRISH ============
async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    print("🤖 SAMIR STORE boti muvaffaqiyatli ishga tushdi!")
    print(f"👑 Admin ID: {ADMIN_ID}")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())