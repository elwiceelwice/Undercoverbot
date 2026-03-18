# bot.py
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, ConversationHandler

# === CONFIG ===
TOKEN = "8638849486:AAHvSkkd1Gt4oy_PbQb7Q_0wD-JyWoHD3MA"  # Remplace par ton token Telegram
MAX_POINTS = 20

# === LOGGING ===
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# === ROLES ===
roles_ville = [
    {"name": "Président d’État", "type": "ville", "action": "élimine la secte", "price": 10},
    {"name": "Juge suprême", "type": "ville", "action": "bloque une action", "price": 6},
    {"name": "Ministre de la défense", "type": "ville", "action": "protège un joueur", "price": 5},
    {"name": "Chef de la police", "type": "ville", "action": "coordonne les enquêtes", "price": 5},
    {"name": "Médecin en chef", "type": "ville", "action": "sauve un rôle clé", "price": 5},
    {"name": "Détective", "type": "ville", "action": "observe un joueur", "price": 4},
    {"name": "Enquêteur", "type": "ville", "action": "découvre un rôle", "price": 4},
    {"name": "Homme blindé", "type": "ville", "action": "protège un joueur", "price": 3},
    {"name": "Citoyen vigilant", "type": "ville", "action": "observe la journée", "price": 2},
    {"name": "Simple civil", "type": "ville", "action": None, "price": 0},
    {"name": "Clochard", "type": "ville", "action": None, "price": 0},
    {"name": "Secte Mashiil", "type": "ville", "action": "convertit les civils", "price": 4}
]

roles_bads = [
    {"name": "Chef de gang", "type": "bad", "action": "attaque ou convertit 35%", "price": 8},
    {"name": "Tueur en série", "type": "bad", "action": "tue un joueur", "price": 6},
    {"name": "Assassin", "type": "bad", "action": "bloque et tue", "price": 6},
    {"name": "Criminel", "type": "bad", "action": "soutient les attaques", "price": 5},
    {"name": "Pyromane", "type": "bad", "action": "attaque aléatoire", "price": 5},
    {"name": "Espion criminel", "type": "bad", "action": "connaît la cible", "price": 4},
    {"name": "Voleur", "type": "bad", "action": "échange de rôle", "price": 4},
    {"name": "Corrompu", "type": "bad", "action": "influence vote", "price": 3},
    {"name": "Maître du temps", "type": "bad", "action": "avantage de temps", "price": 4},
    {"name": "Saboteur", "type": "bad", "action": "empêche actions civiques", "price": 3},
    {"name": "Vexé", "type": "bad", "action": "lynchage automatique", "price": 5}
]

# === JOUEURS ===
players = {}  # player_id : {name, role, points, tickets, alive}
game_started = False
day_count = 0

# === COMMANDES DE BASE ===
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Bienvenue dans Undercover ! Tapez /join_game pour rejoindre la partie.")

def join_game(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        players[user_id] = {"name": update.message.from_user.first_name, "role": None, "points": 0, "tickets": 0, "alive": True}
        update.message.reply_text(f"{update.message.from_user.first_name} a rejoint la partie !")
    else:
        update.message.reply_text("Vous êtes déjà dans la partie.")

# === ATTRIBUTION DES RÔLES ===
def assign_roles():
    all_roles = roles_ville + roles_bads
    player_ids = list(players.keys())
    random.shuffle(player_ids)
    random.shuffle(all_roles)
    for i, pid in enumerate(player_ids):
        players[pid]["role"] = all_roles[i % len(all_roles)]["name"]

# === START GAME ===
def start_game(update: Update, context: CallbackContext):
    global game_started, day_count
    if game_started:
        update.message.reply_text("La partie est déjà en cours.")
        return
    if len(players) < 5:
        update.message.reply_text("Au moins 5 joueurs sont nécessaires pour commencer.")
        return
    assign_roles()
    game_started = True
    day_count = 1
    update.message.reply_text("La partie commence ! Attribution des rôles terminée.")
    next_day(update, context)

# === PHASES ===
def next_day(update: Update, context: CallbackContext):
    global day_count
    chat_id = update.effective_chat.id
    update.message.reply_text(f"Jour {day_count}: Bienvenue dans la ville d'Undercover !")
    day_phase(context, chat_id)

def day_phase(context: CallbackContext, chat_id):
    context.bot.send_message(chat_id=chat_id, text="Phase du jour: vous avez 60 secondes pour faire vos actions.")
    context.job_queue.run_once(defense_phase, 60, context=chat_id)

def defense_phase(context: CallbackContext):
    chat_id = context.job.context
    context.bot.send_message(chat_id=chat_id, text="Phase de veille/defense: 45 secondes pour se défendre ou protéger quelqu’un.")
    context.job_queue.run_once(lynch_phase, 45, context=chat_id)

def lynch_phase(context: CallbackContext):
    chat_id = context.job.context
    context.bot.send_message(chat_id=chat_id, text="Phase de lynchage: 45 secondes. Le Vexé et les votes sont maintenant résolus.")
    # Ici, on résout les actions, conversions, Vexé etc.
    global day_count
    day_count += 1

# === ROLE LIST ===
def role_list(update: Update, context: CallbackContext):
    keyboard = []
    for role in roles_ville + roles_bads:
        keyboard.append([InlineKeyboardButton(role["name"], callback_data=f'role_{role["name"]}')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Liste des rôles :", reply_markup=reply_markup)

def role_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    role_name = query.data.replace("role_", "")
    all_roles = {r["name"]: r for r in roles_ville + roles_bads}
    if role_name in all_roles:
        role = all_roles[role_name]
        desc = f"{role['name']} ({role['type']}) - Action: {role['action']}"
        query.edit_message_text(text=desc)

# === SET LANGUAGE ===
def set_language(update: Update, context: CallbackContext):
    update.message.reply_text("Fonctionnalité langue à venir.")

# === MAIN ===
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("join_game", join_game))
    dp.add_handler(CommandHandler("start_game", start_game))
    dp.add_handler(CommandHandler("role_list", role_list))
    dp.add_handler(CommandHandler("set_language", set_language))
    dp.add_handler(CallbackQueryHandler(role_callback, pattern=r'^role_'))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
