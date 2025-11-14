start
import telebot
from telebot import types
import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default = {
            "admin_id": 993343024,
            "options": ["התחלה", "אמצע", "סוף"],
            "welcome_image": "welcome.jpg",
            "channel_link": "https://t.me/+huHn8bQYZ8QxMWZk"
        }
        save_config(default)
        return default

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=4)

config = load_config()

# ---- שימי כאן את הטוקן שלך במקום YOUR_BOT_TOKEN ----
bot = telebot.TeleBot("8425803272:AAHGw4VADmfqMOo3kCGY2rod7E8dYk_Dhbo")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    cfg = load_config()

    if os.path.exists(cfg["welcome_image"]):
        photo = open(cfg["welcome_image"], "rb")
        bot.send_photo(message.chat.id, photo,
            caption="ברוכה הבאה לבוט 🌿\nבחרי אחת מהאפשרויות:")
    else:
        bot.send_message(message.chat.id, "ברוכה הבאה לבוט 🌿\nבחרי אפשרות:")

    keyboard = types.InlineKeyboardMarkup()
    for opt in cfg["options"]:
        keyboard.add(types.InlineKeyboardButton(opt, callback_data=f"option:{opt}"))

    bot.send_message(message.chat.id, "מה את בוחרת?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("option:"))
def option_selected(call):
    cfg = load_config()
    selection = call.data.split("option:")[1]

    admin = cfg["admin_id"]
    approve_btn = types.InlineKeyboardMarkup()
    approve_btn.add(
        types.InlineKeyboardButton("✔ אשר", callback_data=f"approve:{call.from_user.id}:{selection}"),
        types.InlineKeyboardButton("✖ דחה", callback_data=f"deny:{call.from_user.id}")
    )

    bot.send_message(admin,
        f"📨 בקשה חדשה!\n"
        f"משתמש: @{call.from_user.username}\n"
        f"ID: {call.from_user.id}\n"
        f"אפשרות: {selection}",
        reply_markup=approve_btn)

    bot.answer_callback_query(call.id, "הבקשה נשלחה למנהל ✔")
    bot.send_message(call.message.chat.id, "הבקשה נשלחה למנהל.\nנא להמתין לאישור.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("approve:"))
def approve(call):
    cfg = load_config()
    admin = cfg["admin_id"]

    if call.from_user.id != admin:
        bot.answer_callback_query(call.id, "אין לך הרשאה", show_alert=True)
        return

    _, user_id, option = call.data.split(":")

    bot.send_message(user_id,
        f"אושר! 🎉\n"
        f"נכנסת לפי האפשרות: {option}\n"
        f"הנה הלינק לערוץ:\n{cfg['channel_link']}")

    bot.answer_callback_query(call.id, "אושר ✔")
    bot.send_message(admin, "✔ המשתמש אושר ונשלח לו לינק.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("deny:"))
def deny(call):
    cfg = load_config()
    admin = cfg["admin_id"]

    if call.from_user.id != admin:
        bot.answer_callback_query(call.id, "אין לך הרשאה", show_alert=True)
        return

    _, user_id = call.data.split(":")

    bot.send_message(user_id,
        "❌ בקשתך נדחתה על ידי המנהל.\n"
        "אם את חושבת שזו טעות — פני למנהל.")

    bot.answer_callback_query(call.id, "נדחה ✖")
    bot.send_message(admin, "✖ המשתמש נדחה.")


@bot.message_handler(commands=['admin'])
def admin_panel(message):
    cfg = load_config()

    if message.from_user.id != cfg["admin_id"]:
        bot.send_message(message.chat.id, "גישה למנהלים בלבד ❌")
        return

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("✏ שינוי אופציות", callback_data="edit_options"),
        types.InlineKeyboardButton("🖼 שינוי תמונה", callback_data="edit_image"),
    )
    keyboard.add(types.InlineKeyboardButton("🔗 שינוי לינק לערוץ", callback_data="edit_link"))

    bot.send_message(message.chat.id, "פאנל מנהלים:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "edit_options")
def edit_options(call):
    cfg = load_config()
    if call.from_user.id != cfg["admin_id"]:
        return

    bot.send_message(call.message.chat.id,
        "כתבי את שלושת האופציות החדשות בשורה אחת, מופרדות בפסיקים.\n"
        "לדוגמה:\n"
        "התחלה חדשה, שלב ביניים, סיום מיוחד")

    bot.register_next_step_handler(call.message, save_new_options)


def save_new_options(message):
    parts = [p.strip() for p in message.text.split(",")]

    if len(parts) != 3:
        bot.send_message(message.chat.id, "❌ חייבות להיות בדיוק 3 אופציות.")
        return

    cfg = load_config()
    cfg["options"] = parts
    save_config(cfg)

    bot.send_message(message.chat.id, "✔ האופציות עודכנו בהצלחה.")


@bot.callback_query_handler(func=lambda call: call.data == "edit_link")
def edit_link(call):
    cfg = load_config()

    if call.from_user.id != cfg["admin_id"]:
        return

    bot.send_message(call.message.chat.id, "שלחי את הלינק החדש לערוץ:")
    bot.register_next_step_handler(call.message, save_new_link)


def save_new_link(message):
    cfg = load_config()
    cfg["channel_link"] = message.text.strip()
    save_config(cfg)

    bot.send_message(message.chat.id, "✔ הלינק עודכן.")


@bot.callback_query_handler(func=lambda call: call.data == "edit_image")
def edit_image(call):
    cfg = load_config()

    if call.from_user.id != cfg["admin_id"]:
        return

    bot.send_message(call.message.chat.id, "שלחי תמונה חדשה לשימוש במסך הפתיחה:")
    bot.register_next_step_handler(call.message, save_new_image)


def save_new_image(message):
    if not message.photo:
        bot.send_message(message.chat.id, "❌ לא התקבלה תמונה.")
        return

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded = bot.download_file(file_info.file_path)

    with open("welcome.jpg", "wb") as f:
        f.write(downloaded)

    cfg = load_config()
    cfg["welcome_image"] = "welcome.jpg"
    save_config(cfg)

    bot.send_message(message.chat.id, "✔ התמונה התעדכנה בהצלחה!")


bot.polling(none_stop=True)