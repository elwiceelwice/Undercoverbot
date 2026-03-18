import os
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = os.getenv("TOKEN")

# --- Données ---
joueurs = {}
phase = "jour"

roles_ville = [
    "Civil", "Policier", "Juge", "Avocat",
    "Maire", "Détective", "Garde rapproché",
    "Escorte", "Héros"
]

roles_bads = [
    "Criminel", "Assassin", "Tueur en série", "Maître du temps"
]

roles = roles_ville + roles_bads

# --- Commandes ---
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🎮 Bienvenue dans Crime & Société\n"
        "/join pour rejoindre\n"
        "/startgame pour lancer"
    )

def join(update: Update, context: CallbackContext):
    user = update.message.from_user

    if user.id in joueurs:
        update.message.reply_text("Tu es déjà dans la partie.")
        return

    role = random.choice(roles)
    joueurs[user.id] = {
        "nom": user.first_name,
        "role": role,
        "pv": 100,
        "alive": True,
        "protect": False,
        "bonus": 0
    }

    context.bot.send_message(
        chat_id=user.id,
        text=f"🎭 Ton rôle est : {role}"
    )

    update.message.reply_text(f"{user.first_name} a rejoint la partie.")

def startgame(update: Update, context: CallbackContext):
    update.message.reply_text("🚀 La partie commence ! Phase JOUR")

def statut(update: Update, context: CallbackContext):
    user = update.message.from_user

    if user.id not in joueurs:
        update.message.reply_text("Tu n'es pas dans la partie.")
        return

    j = joueurs[user.id]
    update.message.reply_text(
        f"👤 {j['nom']}\n"
        f"🎭 {j['role']}\n"
        f"❤️ PV: {j['pv']}\n"
        f"💀 Vivant: {j['alive']}"
    )

# --- Phase ---
def phase_cmd(update: Update, context: CallbackContext):
    global phase

    phase = "nuit" if phase == "jour" else "jour"

    update.message.reply_text(f"🌗 Nouvelle phase : {phase.upper()}")

    if phase == "jour":
        lynch(update)
        check_win(update)

# --- Actions ---
def attaquer(update: Update, context: CallbackContext):
    user = update.message.from_user

    if user.id not in joueurs or not joueurs[user.id]["alive"]:
        return

    if joueurs[user.id]["role"] not in roles_bads:
        update.message.reply_text("❌ Tu ne peux pas attaquer.")
        return

    try:
        cible_id = int(context.args[0])
    except:
        update.message.reply_text("Usage: /attaquer ID")
        return

    if cible_id not in joueurs or not joueurs[cible_id]["alive"]:
        update.message.reply_text("❌ Cible invalide.")
        return

    if joueurs[cible_id]["protect"]:
        joueurs[cible_id]["protect"] = False
        update.message.reply_text("🛡️ Attaque bloquée !")
        return

    dmg = random.randint(20, 50)
    joueurs[cible_id]["pv"] -= dmg

    msg = f"⚔️ {joueurs[user.id]['nom']} attaque {joueurs[cible_id]['nom']} ({dmg} dégâts)"

    if joueurs[cible_id]["pv"] <= 0:
        joueurs[cible_id]["alive"] = False
        msg += "\n💀 Mort !"

    update.message.reply_text(msg)

def proteger(update: Update, context: CallbackContext):
    user = update.message.from_user

    if joueurs[user.id]["role"] not in ["Garde rapproché", "Escorte"]:
        update.message.reply_text("❌ Tu ne peux pas protéger.")
        return

    try:
        cible_id = int(context.args[0])
    except:
        update.message.reply_text("Usage: /proteger ID")
        return

    joueurs[cible_id]["protect"] = True
    update.message.reply_text("🛡️ Protection activée")

def enqueter(update: Update, context: CallbackContext):
    user = update.message.from_user

    if joueurs[user.id]["role"] != "Détective":
        update.message.reply_text("❌ Réservé au détective")
        return

    try:
        cible_id = int(context.args[0])
    except:
        return

    role = joueurs[cible_id]["role"]
    context.bot.send_message(user.id, f"🔍 Rôle : {role}")

def arreter(update: Update, context: CallbackContext):
    user = update.message.from_user

    if joueurs[user.id]["role"] != "Policier":
        return

    cible_id = int(context.args[0])
    joueurs[cible_id]["alive"] = False

    update.message.reply_text("🚔 Suspect arrêté !")

# --- Lynchs ---
def lynch(update):
    vivants = [i for i in joueurs if joueurs[i]["alive"]]

    if not vivants:
        return

    cible = random.choice(vivants)

    # Héros peut sauver
    heros = [i for i in joueurs if joueurs[i]["role"] == "Héros" and joueurs[i]["alive"]]

    if heros and random.random() < 0.5:
        update.message.reply_text("🦸 Le héros sauve la victime !")
        return

    joueurs[cible]["alive"] = False
    update.message.reply_text(f"⚖️ {joueurs[cible]['nom']} a été lynché !")

# --- Victoire ---
def check_win(update):
    ville = [j for j in joueurs.values() if j["role"] in roles_ville and j["alive"]]
    bads = [j for j in joueurs.values() if j["role"] in roles_bads and j["alive"]]

    if not ville:
        update.message.reply_text("🏴 Les criminels gagnent !")
    elif not bads:
        update.message.reply_text("🏳️ La ville gagne !")

# --- Main ---
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("join", join))
    dp.add_handler(CommandHandler("startgame", startgame))
    dp.add_handler(CommandHandler("statut", statut))
    dp.add_handler(CommandHandler("phase", phase_cmd))
    dp.add_handler(CommandHandler("attaquer", attaquer))
    dp.add_handler(CommandHandler("proteger", proteger))
    dp.add_handler(CommandHandler("enqueter", enqueter))
    dp.add_handler(CommandHandler("arreter", arreter))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
