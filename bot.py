from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import asyncio
import random

# ===== CONFIG =====
TOKEN = "TON_TOKEN_ICI"  # <-- Mets ton vrai token
JOIN_TIMER = 120  # secondes pour rejoindre la partie
MIN_PLAYERS = 6
MAX_POINTS = 35

# ===== LANGUES =====
LANGUAGES = {"en": "English", "fr": "Français"}

# ===== STOCKAGE RAM =====
players = {}  # user_id: {username, role, points, alive}
game_started = False
language = "fr"

# ===== RÔLES =====
roles = {
    "Président": {"emoji": "👑", "team": "Ville", "action": None, "desc": "Dirige la ville, contrôle le comité exécutif"},
    "Bouclier administratif": {"emoji": "🛡️", "team": "Ville", "action": "protéger", "desc": "Protège un membre du comité exécutif la nuit"},
    "Citoyen": {"emoji": "🧑", "team": "Ville", "action": None, "desc": "Civil sans action spéciale"},
    "Clochard": {"emoji": "🪦", "team": "Ville", "action": None, "desc": "Civil sans action"},
    "Secte Mashiil": {"emoji": "🔮", "team": "Secte", "action": "convertir", "desc": "Peut convertir certains civils la nuit"},
    "Chef de gang": {"emoji": "💀", "team": "Gang", "action": "tuer/convertir", "desc": "Peut attaquer ou convertir des civils, 35% chance de conversion"},
    "Passeur": {"emoji": "🕵️‍♂️", "team": "Gang", "action": "espionner", "desc": "Récupère des indices sur le comité exécutif"},
    "Baron de drogue": {"emoji": "💊", "team": "Gang", "action": "distribuer", "desc": "Travaille seul, interactions limitées avec le juge"},
    "Tueur en série": {"emoji": "🔪", "team": "Solo Bad", "action": "tuer", "desc": "Travaille seul, attaque la nuit"},
    "Assassin": {"emoji": "🗡️", "team": "Solo Bad", "action": "tuer_jour", "desc": "Tue le jour, solo"},
    "Espion": {"emoji": "🕶️", "team": "Bads", "action": "infiltrer", "desc": "Peut découvrir le comité exécutif uniquement"},
    "Vexe": {"emoji": "⚡", "team": "Ville", "action": "lynch_auto", "desc": "Peut lyncher automatiquement une cible, attention aux erreurs"},
}

# ===== COMMANDES =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenue au jeu Undercover!\nRejoignez avec /join"
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global game_started
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    if game_started:
        await update.message.reply_text("La partie a déjà commencé.")
        return
    if user_id not in players:
        players[user_id] = {"username": username, "role": None, "points": 0, "alive": True}
        await update.message.reply_text(f"{username} a rejoint la partie!")
    else:
        await update.message.reply_text("Vous avez déjà rejoint.")

async def rolelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for r, v in roles.items():
        keyboard.append([InlineKeyboardButton(f"{v['emoji']} {r}", callback_data=f"about_{r}")])
    await update.message.reply_text(
        "Liste des rôles:", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def setlanguage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global language
    if context.args:
        lang = context.args[0].lower()
        if lang in LANGUAGES:
            language = lang
            await update.message.reply_text(f"Langue définie sur {LANGUAGES[lang]}")
        else:
            await update.message.reply_text("Langue non supportée.")
    else:
        await update.message.reply_text("Usage: /setlanguage <en/fr>")

# ===== CALLBACK POUR INFO RÔLE =====
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("about_"):
        role = query.data.replace("about_", "")
        info = roles[role]["desc"]
        await query.edit_message_text(f"{roles[role]['emoji']} {role}:\n{info}")

# ===== LANCER LA PARTIE =====
async def launch_game():
    global game_started
    game_started = True
    # Attribution aléatoire des rôles
    assigned_roles = random.sample(list(roles.keys()), len(players))
    for i, uid in enumerate(players.keys()):
        players[uid]["role"] = assigned_roles[i % len(assigned_roles)]
        # Message personnel
        # (en vrai bot: envoyer message privé, ici simplifié)
        print(f"{players[uid]['username']} -> {players[uid]['role']}")
    # Timer de la phase du jour
    await asyncio.sleep(60)  # Phase du jour
    print("Phase du jour terminée")
    await asyncio.sleep(45)  # Veille et défense
    print("Veille terminée")
    await asyncio.sleep(45)  # Lynchage
    print("Lynchage terminé")

# ===== MAIN =====
async def join_timer(context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(JOIN_TIMER)
    if len(players) >= MIN_PLAYERS:
        await launch_game()

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("rolelist", rolelist))
    app.add_handler(CommandHandler("setlanguage", setlanguage))
    app.add_handler(CallbackQueryHandler(button))
    # Démarrer le timer pour rejoindre la partie
    asyncio.create_task(join_timer(None))
    print("Bot prêt et polling...")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())    role = next((r for r in roles if r["name"] == role_name), None)
    if role:
        await query.message.reply_text(f"{role['emoji']} {role['name']}\nCamp: {role['camp']}\nDescription: {role['description']}\nAction: {role.get('action','Aucune')}")

async def setlanguage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0] in LANGUAGES:
        context.user_data["lang"] = context.args[0]
        await update.message.reply_text(f"Langue définie sur {context.args[0]}")
    else:
        await update.message.reply_text("Langues disponibles: fr, en")

# ====== FONCTIONS DE JEU ======
def assign_roles():
    player_ids = list(players.keys())
    random.shuffle(player_ids)
    for i, pid in enumerate(player_ids):
        if len(player_ids) >= 15 and i == 0:
            players[pid]["role"] = next(r for r in roles if r["name"] == "Secte")
        else:
            players[pid]["role"] = random.choice(roles)

async def start_game(context: ContextTypes.DEFAULT_TYPE):
    global game_phase
    if len(players) < MIN_PLAYERS:
        return
    assign_roles()
    game_phase = "night"
    await broadcast("Le jeu commence! Phase de nuit pour 2 minutes.")
    await asyncio.sleep(JOIN_TIMER)
    await night_phase()

async def broadcast(message):
    for pid in players:
        try:
            await context.bot.send_message(chat_id=pid, text=message)
        except:
            pass

async def night_phase():
    global game_phase
    game_phase = "night"
    await broadcast("Phase de nuit: tout le monde agit...")
    await asyncio.sleep(60)
    await day_phase()

async def day_phase():
    global game_phase
    game_phase = "day"
    await broadcast("Phase de jour: lynchage possible!")
    await asyncio.sleep(60)
    await night_phase()

# ====== APPLICATION ======
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("join", join))
app.add_handler(CommandHandler("rolelist", rolelist))
app.add_handler(CommandHandler("setlanguage", setlanguage))
app.add_handler(CallbackQueryHandler(about_role, pattern=r"^info_"))

print("Bot prêt à démarrer...")
app.run_polling()        if not p["alive"]:
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
