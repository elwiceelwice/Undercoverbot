# bot.py
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import random
import datetime

# =========================
# CONFIGURATION
# =========================
TOKEN = "TON_TOKEN_ICI"  # Remplace par ton vrai token
LANGS = ["fr", "en"]
DEFAULT_LANG = "fr"

# Stockage simple en RAM
GAME = {
    "players": {},       # player_id: {"name": str, "role": str, "alive": bool, "points": int}
    "roles": {},         # role_name: {"team": str, "emoji": str, "description": str, "action": callable}
    "phase": "waiting",  # waiting, day, defense, lynch
    "day_number": 0,
    "language": DEFAULT_LANG,
    "join_timer": None
}

# =========================
# DEFINITION DES ROLES
# =========================
# Les civils
GAME["roles"] = {
    "Président": {
        "team": "ville", "emoji": "🏛️", 
        "description": "Dirige la ville, peut coordonner le comité exécutif.", "action": None
    },
    "Bouclier administratif": {
        "team": "ville", "emoji": "🛡️",
        "description": "Protège un membre du comité exécutif.", "action": None
    },
    "Citoyen": {
        "team": "ville", "emoji": "👨‍👩‍👧", 
        "description": "Civil simple, aucun pouvoir particulier.", "action": None
    },
    "Clochard": {
        "team": "ville", "emoji": "🪤", 
        "description": "Civil simple sans action.", "action": None
    },
    "Enquêteur": {
        "team": "ville", "emoji": "🕵️", 
        "description": "Peut enquêter sur une personne chaque nuit.", "action": None
    },
    "Détective": {
        "team": "ville", "emoji": "🕵️‍♂️", 
        "description": "Peut découvrir des membres du gang ou la secte.", "action": None
    },
    # Gangs et criminels
    "Chef de gang": {
        "team": "bad", "emoji": "💀",
        "description": "Dirige le gang, peut convertir des civils à 35%.", "action": None
    },
    "Gang premier rang": {
        "team": "bad", "emoji": "🔪",
        "description": "Membre du gang.", "action": None
    },
    "Passeur": {
        "team": "bad", "emoji": "📡",
        "description": "Collecte des indices sur le comité exécutif.", "action": None
    },
    "Baron de drogue": {
        "team": "bad", "emoji": "💊",
        "description": "Travaille seul, distribue de la drogue et risque de se faire repérer par le juge.", "action": None
    },
    # Secte
    "Secte Mashiil": {
        "team": "bad", "emoji": "🕉️",
        "description": "Peut convertir des civils, apparaît seulement si >=15 joueurs.", "action": None
    },
    "Prêtre": {
        "team": "bad", "emoji": "⛪",
        "description": "Risque 50% de mourir lorsqu'il visite un mauvais rôle.", "action": None
    },
    "Croyant de premier rang": {
        "team": "bad", "emoji": "🙏",
        "description": "Peut convertir un membre du comité exécutif avec 25-30% de chance.", "action": None
    },
    # Tueurs solitaires
    "Tueur en série": {
        "team": "bad", "emoji": "🔪",
        "description": "Gagne seul, solitaire.", "action": None
    },
    "Assassin": {
        "team": "bad", "emoji": "🗡️",
        "description": "Tue pendant le jour, nécessite >=35 joueurs.", "action": None
    },
    "Espion": {
        "team": "bad", "emoji": "🕵️‍♂️",
        "description": "Peut découvrir les membres du comité exécutif uniquement.", "action": None
    },
    # Vexe
    "Vexe": {
        "team": "ville", "emoji": "⚡",
        "description": "Lorsqu'il lynche, le lynchage est automatique, gagne avec la ville.", "action": None
    }
}

# =========================
# COMMANDES DE BASE
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bienvenue! Tapez /joingame pour rejoindre la partie.")

async def joingame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in GAME["players"]:
        GAME["players"][user_id] = {
            "name": update.message.from_user.first_name,
            "role": None,
            "alive": True,
            "points": 0
        }
        await update.message.reply_text(f"{update.message.from_user.first_name} a rejoint la partie.")
    else:
        await update.message.reply_text("Vous êtes déjà dans la partie.")

async def rolelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ""
    keyboard = []
    for role, info in GAME["roles"].items():
        text += f"{info['emoji']} {role}\n"
        keyboard.append([InlineKeyboardButton("Info", callback_data=f"info_{role}")])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def setlanguage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0] in LANGS:
        GAME["language"] = context.args[0]
        await update.message.reply_text(f"Langue définie sur {context.args[0]}")
    else:
        await update.message.reply_text("Langue non supportée.")

async def info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    role_name = query.data.replace("info_", "")
    info = GAME["roles"].get(role_name, None)
    if info:
        await query.message.reply_text(f"{info['emoji']} {role_name}\nTeam: {info['team']}\n{info['description']}")

# =========================
# LANCER LE BOT
# =========================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("joingame", joingame))
    app.add_handler(CommandHandler("rolelist", rolelist))
    app.add_handler(CommandHandler("setlanguage", setlanguage))
    app.add_handler(CallbackQueryHandler(info_callback, pattern="^info_"))

    print("Bot lancé...")
    app.run_polling()        await update.message.reply_text("Usage: /setlanguage <code_langue>")

async def rolelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton(f"{r['emoji']} {role}", callback_data=f"about_{role}")] for role,r in ROLES.items()]
    await update.message.reply_text("Liste des rôles:", reply_markup=InlineKeyboardMarkup(buttons))

async def about_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    role_name = query.data.replace("about_", "")
    role_info = ROLES.get(role_name)
    if role_info:
        await query.edit_message_text(f"{role_info['emoji']} {role_name}\nDescription: {role_info['desc']}")

# ----------------------------
# Attribution automatique
# ----------------------------
def assign_roles():
    players = list(game_state["players"].keys())
    roles_keys = list(ROLES.keys())
    random.shuffle(players)
    for i,p in enumerate(players):
        role = roles_keys[i % len(roles_keys)]
        game_state["players"][p]["role"] = role
        game_state["players"][p]["team"] = ROLES[role]["team"]

# ----------------------------
# Calcul des points
# ----------------------------
def calculate_points():
    for p in game_state["players"].values():
        if not p["alive"]:
            p["points"] -= 5
        else:
            # Points selon l'efficacité et rôle
            if p["team"]=="ville":
                if p["role"]=="Citoyen":
                    p["points"] += random.randint(5,10)
                else:
                    p["points"] += random.randint(15,35)
            elif p["team"]=="bad":
                p["points"] += random.randint(10,35)
            elif p["team"]=="secte":
                p["points"] += random.randint(5,30)
            # Clamp max
            if p["points"]>MAX_POINTS:
                p["points"]=MAX_POINTS
            if p["points"]<0:
                p["points"]=0

# ----------------------------
# Boucle de jeu
# ----------------------------
async def game_loop(context: ContextTypes.DEFAULT_TYPE):
    while True:
        if len(game_state["players"])>=6:
            game_state["phase"]="day"
            await context.bot.send_message(chat_id=context.job.chat_id,text=f"Phase du jour {game_state['day']} - 60s pour agir")
            await asyncio.sleep(60)

            game_state["phase"]="night"
            await context.bot.send_message(chat_id=context.job.chat_id,text="Veille & défense - 45s")
            await asyncio.sleep(45)

            game_state["phase"]="lynch"
            await context.bot.send_message(chat_id=context.job.chat_id,text="Lynchage - 45s")
            await asyncio.sleep(45)

            # Calcul points après jour/nuit
            calculate_points()
            game_state["day"] += 1
        else:
            await asyncio.sleep(10)

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(game_state["players"])<6:
        await update.message.reply_text("Au moins 6 joueurs nécessaires pour commencer!")
        return
    assign_roles()
    await update.message.reply_text("La partie commence!")
    context.application.create_task(game_loop(context))

# ----------------------------
# Application Telegram
# ----------------------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("join",join))
app.add_handler(CommandHandler("setlanguage",set_language))
app.add_handler(CommandHandler("rolelist",rolelist))
app.add_handler(CommandHandler("startgame",start_game))
app.add_handler(CallbackQueryHandler(about_role,pattern="^about_"))

# Lancer le bot
if __name__=="__main__":
    print("Bot lancé...")
    app.run_polling()            await update.message.reply_text("Langue non supportée.")
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
