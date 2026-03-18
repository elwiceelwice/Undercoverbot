import os
import threading
import time
from telegram import ParseMode, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Token du bot (mettre en variable d'environnement)
TOKEN = os.environ.get("TOKEN").strip()

# Durées en secondes
JOIN_PHASE_TIME = 120  # 2 minutes pour rejoindre
DAY_PHASE_TIME = 60
DEFENSE_PHASE_TIME = 45
LYNCH_PHASE_TIME = 45

# Exemple de rôles
ROLES = {
    "Président": "Dirige la ville et peut protéger certains civils.",
    "Détective": "Peut enquêter sur un joueur chaque nuit.",
    "Chef de gang": "Peut convertir un civil à son camp (35% chance).",
    "Simple Civil": "Pas d’action, juste survivre.",
    "Secte": "Peut recruter des civils, meurt si va chez un bad."
}

# Stockage des joueurs et de leurs rôles
players = {}  # user_id -> {"name": str, "role": str, "points": int}
join_timer_active = False
join_timer_thread = None

# ---------------- COMMANDES ---------------- #

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Bienvenue dans Undercover! Utilise /join pour rejoindre la partie.\n"
        "Le timer pour rejoindre est de 2 minutes. Une fois 6 joueurs minimum, on peut forcer le début."
    )

def join(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    name = update.message.from_user.first_name
    if user_id in players:
        update.message.reply_text("Tu as déjà rejoint la partie!")
    else:
        players[user_id] = {"name": name, "role": None, "points": 0}
        update.message.reply_text(f"{name} a rejoint la partie! Joueurs totaux: {len(players)}")

def rolelist(update: Update, context: CallbackContext):
    msg = "*Liste des rôles :*\n"
    for role, desc in ROLES.items():
        msg += f"• *{role}* : {desc}\n"
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

def setlanguage(update: Update, context: CallbackContext):
    if context.args:
        lang = context.args[0].lower()
        update.message.reply_text(f"Langue changée en {lang}")
    else:
        update.message.reply_text("Usage: /setlanguage <fr/en>")

def myrole(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in players and players[user_id]["role"]:
        update.message.reply_text(f"Ton rôle est : {players[user_id]['role']}")
    else:
        update.message.reply_text("Tu n'as pas encore reçu de rôle.")

def points(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in players:
        update.message.reply_text(f"Tu as {players[user_id]['points']} points.")
    else:
        update.message.reply_text("Tu n'as pas encore rejoint la partie.")

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
