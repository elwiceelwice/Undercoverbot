import os
import random
import threading
import time
from collections import defaultdict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

TOKEN = os.getenv("TOKEN")

players = {}
game_state = {
    "started": False,
    "actions": {},
    "votes": defaultdict(int)
}

ROLES = {
    "president": {"team": "Ville"},
    "juge": {"team": "Ville"},
    "bouclier": {"team": "Ville"},
    "detective": {"team": "Ville"},
    "policier": {"team": "Ville"},
    "citoyen": {"team": "Ville"},
    "clochard": {"team": "Ville"},
    "dormeur": {"team": "Ville"},

    "chef_gang": {"team": "Gang"},
    "gang": {"team": "Gang"},
    "espion": {"team": "Gang"},

    "secte": {"team": "Secte"},

    "tueur": {"team": "Solo"},
    "assassin": {"team": "Solo"},
    "baron": {"team": "Solo"},

    "vexe": {"team": "Ville"}
}

# ================= JOIN ================= #

def join(update: Update, context: CallbackContext):
    user = update.message.from_user
    players[user.id] = {"name": user.first_name, "role": None, "alive": True, "points": 0}
    update.message.reply_text(f"{user.first_name} rejoint ({len(players)})")

# ================= ROLE ASSIGN ================= #

def assign_roles(bot):
    ids = list(players.keys())
    random.shuffle(ids)

    roles = list(ROLES.keys())
    while len(roles) < len(ids):
        roles.append("citoyen")

    random.shuffle(roles)

    for i, uid in enumerate(ids):
        role = roles[i]
        players[uid]["role"] = role
        bot.send_message(uid, f"🎭 Ton rôle : {role}")

# ================= NIGHT ================= #

def night_phase(bot, chat_id):
    game_state["actions"] = {}

    for uid, p in players.items():
        if not p["alive"]:
            continue

        role = p["role"]

        if role in ["chef_gang", "gang", "tueur", "assassin"]:
            send_action(bot, uid, "kill")

        elif role == "bouclier":
            send_action(bot, uid, "protect")

        elif role == "detective":
            send_action(bot, uid, "inspect")

        elif role == "espion":
            send_action(bot, uid, "spy")

        elif role == "secte":
            send_action(bot, uid, "convert")

    bot.send_message(chat_id, "🌙 Nuit en cours (45s)")
    time.sleep(45)

    resolve_night(bot, chat_id)

def send_action(bot, uid, action_type):
    buttons = []
    for target_id, p in players.items():
        if p["alive"] and target_id != uid:
            buttons.append([InlineKeyboardButton(p["name"], callback_data=f"{action_type}:{target_id}")])

    bot.send_message(uid, f"Choisis une cible ({action_type})", reply_markup=InlineKeyboardMarkup(buttons))

# ================= HANDLE ACTION ================= #

def action_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    action, target = query.data.split(":")
    user = query.from_user.id

    game_state["actions"][user] = (action, int(target))
    query.edit_message_text("✅ Action enregistrée")

# ================= RESOLUTION ================= #

def resolve_night(bot, chat_id):
    protected = set()
    deaths = set()

    for uid, (action, target) in game_state["actions"].items():
        role = players[uid]["role"]

        if action == "protect":
            protected.add(target)

    for uid, (action, target) in game_state["actions"].items():
        role = players[uid]["role"]

        if action == "kill":
            if target not in protected:
                deaths.add(target)

        elif action == "convert":
            if players[target]["role"] == "citoyen":
                players[target]["role"] = "secte"

    for d in deaths:
        players[d]["alive"] = False

    msg = "☀️ Résultat nuit:\n"
    for d in deaths:
        msg += f"💀 {players[d]['name']} est mort\n"

    bot.send_message(chat_id, msg)

# ================= DAY ================= #

def day_phase(bot, chat_id):
    bot.send_message(chat_id, "🌞 Jour (60s discussion)")
    time.sleep(60)

    vote_phase(bot, chat_id)

# ================= VOTE ================= #

def vote_phase(bot, chat_id):
    game_state["votes"].clear()

    buttons = []
    for uid, p in players.items():
        if p["alive"]:
            buttons.append([InlineKeyboardButton(p["name"], callback_data=f"vote:{uid}")])

    bot.send_message(chat_id, "⚖️ Votez :", reply_markup=InlineKeyboardMarkup(buttons))
    time.sleep(45)

    resolve_votes(bot, chat_id)

def vote_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    target = int(query.data.split(":")[1])
    game_state["votes"][target] += 1

def resolve_votes(bot, chat_id):
    if not game_state["votes"]:
        bot.send_message(chat_id, "❌ Aucun vote")
        return

    victim = max(game_state["votes"], key=game_state["votes"].get)
    players[victim]["alive"] = False

    bot.send_message(chat_id, f"☠️ {players[victim]['name']} a été lynché")

# ================= GAME LOOP ================= #

def game_loop(bot, chat_id):
    while True:
        night_phase(bot, chat_id)
        day_phase(bot, chat_id)

# ================= START ================= #

def startgame(update: Update, context: CallbackContext):
    if len(players) < 6:
        update.message.reply_text("Minimum 6 joueurs")
        return

    assign_roles(context.bot)
    threading.Thread(target=game_loop, args=(context.bot, update.effective_chat.id)).start()

# ================= MAIN ================= #

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("join", join))
    dp.add_handler(CommandHandler("startgame", startgame))
    dp.add_handler(CallbackQueryHandler(action_handler, pattern="^(kill|protect|inspect|spy|convert):"))
    dp.add_handler(CallbackQueryHandler(vote_handler, pattern="^vote:"))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()        update.message.reply_text("Tu n'as pas encore rejoint la partie.")

# ---------------- FONCTIONS DE GESTION DE PARTIE ---------------- #

def assign_roles():
    import random
    roles_list = list(ROLES.keys())
    random.shuffle(roles_list)
    player_ids = list(players.keys())
    for i, pid in enumerate(player_ids):
        role = roles_list[i % len(roles_list)]
        players[pid]["role"] = role

def join_timer(bot, chat_id):
    global join_timer_active
    join_timer_active = True
    remaining = JOIN_PHASE_TIME
    while remaining > 0:
        time.sleep(5)
        remaining -= 5
        if len(players) >= 6:
            bot.send_message(chat_id, f"6 joueurs ont rejoint ! Utilisez /startgame pour commencer ou attendre {remaining}s.")
    join_timer_active = False
    bot.send_message(chat_id, "Temps de rejoins terminé ! Attribution des rôles...")
    assign_roles()
    start_day_phase(bot, chat_id)

def start_join_phase(update: Update, context: CallbackContext):
    global join_timer_thread
    chat_id = update.effective_chat.id
    if join_timer_thread and join_timer_thread.is_alive():
        update.message.reply_text("Le timer de rejoindre est déjà en cours.")
    else:
        update.message.reply_text("Le timer de rejoindre a commencé : 2 minutes !")
        join_timer_thread = threading.Thread(target=join_timer, args=(context.bot, chat_id))
        join_timer_thread.start()

# ---------------- PHASES DE JOUR ---------------- #

def start_day_phase(bot, chat_id):
    bot.send_message(chat_id, "🌞 Phase du jour : Vous avez 60 secondes pour agir!")
    threading.Timer(DAY_PHASE_TIME, start_defense_phase, args=(bot, chat_id)).start()

def start_defense_phase(bot, chat_id):
    bot.send_message(chat_id, "🛡️ Phase de défense : chacun se défend pour ne pas être lynché (45s) !")
    threading.Timer(DEFENSE_PHASE_TIME, start_lynch_phase, args=(bot, chat_id)).start()

def start_lynch_phase(bot, chat_id):
    bot.send_message(chat_id, "⚖️ Phase de lynchage : votez maintenant (45s) !")
    threading.Timer(LYNCH_PHASE_TIME, end_turn, args=(bot, chat_id)).start()

def end_turn(bot, chat_id):
    bot.send_message(chat_id, "✅ La journée est terminée. Préparez-vous pour le prochain tour!")

# ---------------- SETUP BOT ---------------- #

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("join", join))
    dp.add_handler(CommandHandler("rolelist", rolelist))
    dp.add_handler(CommandHandler("setlanguage", setlanguage, pass_args=True))
    dp.add_handler(CommandHandler("myrole", myrole))
    dp.add_handler(CommandHandler("points", points))
    dp.add_handler(CommandHandler("startjoin", start_join_phase))  # démarre le timer 2 min

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
