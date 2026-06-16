        import telebot
import json
import random
import time
import os

TOKEN = "8969615907:AAGsc6mue_Xo567cyOpPkhiZN3Af1EYdtWQ"
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users.json"
COOLDOWN = 1200

cards = [
    {"name":"Нита","eng":"Nita","rarity":"Редкий","emoji":"🟩","class":"Урон","female":True},
    {"name":"Кольт","eng":"Colt","rarity":"Редкий","emoji":"🟩","class":"Урон","female":False},
    {"name":"Джесси","eng":"Jessie","rarity":"Сверхредкий","emoji":"🟦","class":"Контроль","female":True},
    {"name":"Динамайк","eng":"Dynamike","rarity":"Сверхредкий","emoji":"🟦","class":"Артиллерия","female":False},
    {"name":"Бо","eng":"Bo","rarity":"Эпический","emoji":"🟪","class":"Контроль","female":False},
    {"name":"Эмз","eng":"Emz","rarity":"Эпический","emoji":"🟪","class":"Контроль","female":True},
    {"name":"Мортис","eng":"Mortis","rarity":"Мифический","emoji":"🟥","class":"Убийца","female":False},
    {"name":"Тара","eng":"Tara","rarity":"Мифический","emoji":"🟥","class":"Урон","female":True},
    {"name":"Спайк","eng":"Spike","rarity":"Легендарный","emoji":"🟨","class":"Урон","female":False},
    {"name":"Ворон","eng":"Crow","rarity":"Легендарный","emoji":"🟨","class":"Убийца","female":False}
]

# ---------- LOAD / SAVE ----------

def load():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ---------- USER ----------

def get_user(data, uid, message):
    user = message.from_user

    name = "@" + user.username if user.username else user.first_name

    if uid not in data:
        data[uid] = {
            "inventory": [],
            "last_open": 0,
            "name": name
        }

    data[uid]["name"] = name
    return data[uid]

# ---------- OPEN CARD ----------

def give_card(message):
    data = load()
    uid = str(message.from_user.id)
    user = get_user(data, uid, message)

    now = time.time()

    if now - user["last_open"] < COOLDOWN:
        left = int(COOLDOWN - (now - user["last_open"]))
        bot.reply_to(message, f"⏳ Подожди {left//60} мин {left%60} сек")
        return

    available = [c for c in cards if c["name"] not in user["inventory"]]

    if not available:
        bot.reply_to(message, "🏆 Ты собрал все карточки!")
        return

    card = random.choice(available)

    user["inventory"].append(card["name"])
    user["last_open"] = now

    save(data)

    word = "выпала" if card["female"] else "выпал"
    prefix = "🎉 Поздравляем! Вам" if card["rarity"] == "Легендарный" else "🎉 Вам"

    bot.reply_to(message,
        f"{prefix} {word} {card['name']} - {card['eng']}\n\n"
        f"{card['emoji']} Редкость: {card['rarity']}\n"
        f"⚔️ Класс бравлера: {card['class']}"
    )

# ---------- INVENTORY ----------

def inventory(message):
    data = load()
    uid = str(message.from_user.id)

    if uid not in data or not data[uid]["inventory"]:
        bot.reply_to(message, "🃏 Твои карточки:\n\n📦 Пусто")
        return

    text = "🃏 Твои карточки:\n\n"

    for name in data[uid]["inventory"]:
        card = next((c for c in cards if c["name"] == name), None)
        if card:
            text += f"{card['emoji']} {card['name']} ({card['rarity']})\n"

    text += f"\n📊 {len(data[uid]['inventory'])}/{len(cards)}"

    bot.reply_to(message, text)

# ---------- TOP ----------

def show_top(message):
    data = load()

    if not data:
        bot.reply_to(message, "🏆 СПИСКИ ЛИДЕРОВ:\n\nПока нет игроков")
        return

    players = []

    for uid, info in data.items():
        name = info.get("name", "Без имени")
        count = len(info.get("inventory", []))
        players.append((name, count))

    players.sort(key=lambda x: x[1], reverse=True)

    text = "🏆 СПИСКИ ЛИДЕРОВ:\n\n"

    for i, (name, count) in enumerate(players[:10], 1):
        text += f"{i}. {name} - {count} карточек 🃏\n"

    bot.reply_to(message, text)

# ---------- COMMANDS ----------

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message,
        "🎴 БОТ КАРТОЧЕК BRAWL STARS\n\n"
        "🃏 Brawlers Cards — открыть карточку\n"
        "📦 Мои карточки — посмотреть коллекцию\n"
        "🏆 Списки лидеров — рейтинг игроков"
    )

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "brawlers cards")
def open_cmd(message):
    give_card(message)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "мои карточки")
def inv_cmd(message):
    inventory(message)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "списки лидеров")
def top_cmd(message):
    show_top(message)

print("Bot started!")
bot.infinity_polling()
