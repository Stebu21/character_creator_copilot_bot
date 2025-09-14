from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
import random
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Stati della conversazione
(
    SCEGLI_CLASSE, SCEGLI_SOTTOCLASSE, SCEGLI_LIVELLO,
    SCEGLI_BONUS_LIV4, SCEGLI_BONUS_LIV8, SCEGLI_TALENTO_1,
    SCEGLI_TALENTO_2, APPLICA_ASI_1, APPLICA_ASI_2
) = range(9)

# Dati di D&D
classi_disponibili = {
    'Barbaro': ['Sentiero del Berserker', 'Sentiero del Guerriero Totemico'],
    'Guerriero': ['Maestro di Battaglia', 'Cavaliere Mistico'],
    'Ladro': ['Ladro', 'Assassino'],
    'Mago': ['Scuola di Invocazione', 'Scuola di Divinazione'],
}

stat_primarie = {
    'Barbaro': ['Forza', 'Costituzione'],
    'Guerriero': ['Forza', 'Costituzione'],
    'Ladro': ['Destrezza', 'Intelligenza'],
    'Mago': ['Intelligenza', 'Costituzione'],
}

# NUOVA STRUTTURA DATI: Talenti specifici per classe
talenti_per_classe = {
    'Barbaro': ['Sentinella', 'Resiliente', 'Maestro d\'Armi', 'Tavern Brawler'],
    'Guerriero': ['Combattente', 'Maestro di Scudi', 'Sentinella', 'Grande Arma', 'Resiliente'],
    'Ladro': ['Combattente', 'Tiratore Scelto', 'Maestro degli Archi', 'Mano Lesta'],
    'Mago': ['Incantatore da Guerra', 'Resiliente', 'Ritual Caster', 'Elemental Adept'],
}

def roll_dnd_stats():
    stats_list = []
    for _ in range(6):
        rolls = sorted([random.randint(1, 6) for _ in range(4)])
        stats_list.append(sum(rolls[1:]))
    stats_list.sort(reverse=True)
    return stats_list

def assign_stats(class_name, stats_values):
    all_stats = {'Forza': 0, 'Destrezza': 0, 'Costituzione': 0, 'Intelligenza': 0, 'Saggezza': 0, 'Carisma': 0}
    primary_stats = stat_primarie.get(class_name, [])
    
    assigned_count = 0
    for stat in primary_stats:
        if assigned_count < len(stats_values):
            all_stats[stat] = stats_values[assigned_count]
            assigned_count += 1
    
    remaining_stats = [stat for stat in all_stats.keys() if stat not in primary_stats]
    for stat in remaining_stats:
        if assigned_count < len(stats_values):
            all_stats[stat] = stats_values[assigned_count]
            assigned_count += 1
    return all_stats

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Benvenuto! Invia il comando /crea per iniziare.")
    return ConversationHandler.END

async def crea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [list(classi_disponibili.keys())[i:i + 3] for i in range(0, len(classi_disponibili), 3)]
    await update.message.reply_text(
        "Per iniziare, quale classe vuoi scegliere?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SCEGLI_CLASSE

async def classe_scelta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text
    if user_choice not in classi_disponibili:
        await update.message.reply_text("Per favore, scegli una classe dalla lista.")
        return SCEGLI_CLASSE
    context.user_data['classe'] = user_choice
    context.user_data['stats'] = assign_stats(user_choice, roll_dnd_stats())
    
    sottoclassi = classi_disponibili[user_choice]
    reply_keyboard = [sottoclassi[i:i + 2] for i in range(0, len(sottoclassi), 2)]
    await update.message.reply_text(
        f"Perfetto! E la sottoclasse di un {user_choice}?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SCEGLI_SOTTOCLASSE

async def sottoclasse_scelta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text
    classe = context.user_data.get('classe')
    if user_choice not in classi_disponibili.get(classe, []):
        await update.message.reply_text("Per favore, scegli una sottoclasse dalla lista.")
        return SCEGLI_SOTTOCLASSE
    context.user_data['sottoclasse'] = user_choice
    context.user_data['talenti'] = []
    
    await update.message.reply_text(
        f"Ottimo! Infine, a quale livello è il tuo personaggio? (1-20)",
        reply_markup=ReplyKeyboardRemove()
    )
    return SCEGLI_LIVELLO

async def livello_scelto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        livello = int(update.message.text)
        if not 1 <= livello <= 20:
            raise ValueError
    except (ValueError, TypeError):
        await update.message.reply_text("Per favore, inserisci un numero da 1 a 20.")
        return SCEGLI_LIVELLO
        
    context.user_data['livello'] = livello
    context.user_data['asi_points_applied'] = 0
    
    if livello >= 8:
        reply_keyboard = [['2 ASI (+4 punti)', '1 ASI + 1 Talento', '2 Talenti']]
        await update.message.reply_text(
            f"A livello 8, hai a disposizione un'altra scelta.\n"
            "Cosa vuoi fare?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return SCEGLI_BONUS_LIV8
    elif livello >= 4:
        reply_keyboard = [['2 punti nelle statistiche', '1 talento']]
        await update.message.reply_text(
            "A livello 4, hai una scelta da fare.\n"
            "Vuoi usare 2 punti nelle statistiche o scegliere un talento?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return SCEGLI_BONUS_LIV4
    
    await finalize_character(update, context)
    return ConversationHandler.END

async def scegli_bonus_liv4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == '2 punti nelle statistiche':
        context.user_data['punti_da_applicare'] = 2
        await update.message.reply_text(
            "Perfetto! Scegli la statistica da aumentare di 2 punti.",
            reply_markup=ReplyKeyboardMarkup([['Forza', 'Destrezza', 'Costituzione'], ['Intelligenza', 'Saggezza', 'Carisma']], one_time_keyboard=True)
        )
        return APPLICA_ASI_1
    elif choice == '1 talento':
        classe = context.user_data['classe']
        talenti_disponibili_per_classe = talenti_per_classe.get(classe, [])
        reply_keyboard = [talenti_disponibili_per_classe[i:i+2] for i in range(0, len(talenti_disponibili_per_classe), 2)]
        
        await update.message.reply_text("Scegli un talento dalla lista:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        context.user_data['talenti_da_scegliere'] = 1
        return SCEGLI_TALENTO_1
    else:
        await update.message.reply_text("Scelta non valida. Riprova.")
        return SCEGLI_BONUS_LIV4

async def scegli_bonus_liv8(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == '2 ASI (+4 punti)':
        context.user_data['asi_da_applicare'] = 2
        await update.message.reply_text(
            "Perfetto! Scegli la statistica per il tuo primo aumento di +2.",
            reply_markup=ReplyKeyboardMarkup([['Forza', 'Destrezza', 'Costituzione'], ['Intelligenza', 'Saggezza', 'Carisma']], one_time_keyboard=True)
        )
        return APPLICA_ASI_1
    elif choice == '1 ASI + 1 Talento':
        context.user_data['asi_da_applicare'] = 1
        context.user_data['talenti_da_scegliere'] = 1
        await update.message.reply_text(
            "Perfetto! Scegli la statistica da aumentare di 2 punti.",
            reply_markup=ReplyKeyboardMarkup([['Forza', 'Destrezza', 'Costituzione'], ['Intelligenza', 'Saggezza', 'Carisma']], one_time_keyboard=True)
        )
        return APPLICA_ASI_1
    elif choice == '2 Talenti':
        context.user_data['talenti_da_scegliere'] = 2
        
        classe = context.user_data['classe']
        talenti_disponibili_per_classe = talenti_per_classe.get(classe, [])
        reply_keyboard = [talenti_disponibili_per_classe[i:i+2] for i in range(0, len(talenti_disponibili_per_classe), 2)]
        
        await update.message.reply_text("Scegli il tuo primo talento:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return SCEGLI_TALENTO_1
    else:
        await update.message.reply_text("Scelta non valida. Riprova.")
        return SCEGLI_BONUS_LIV8

async def applica_asi_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stat_choice = update.message.text
    if stat_choice not in context.user_data['stats']:
        await update.message.reply_text("Scelta non valida. Riprova.")
        return APPLICA_ASI_1
    
    context.user_data['stats'][stat_choice] += 2
    context.user_data['asi_points_applied'] += 2
    
    if context.user_data.get('asi_da_applicare', 0) > 1:
        context.user_data['asi_da_applicare'] -= 1
        await update.message.reply_text(
            "Ottimo. Scegli la prossima statistica da aumentare di 2 punti.",
            reply_markup=ReplyKeyboardMarkup([['Forza', 'Destrezza', 'Costituzione'], ['Intelligenza', 'Saggezza', 'Carisma']], one_time_keyboard=True)
        )
        return APPLICA_ASI_2
    
    await finalize_or_next_step(update, context)
    return ConversationHandler.END

async def applica_asi_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stat_choice = update.message.text
    if stat_choice not in context.user_data['stats']:
        await update.message.reply_text("Scelta non valida. Riprova.")
        return APPLICA_ASI_2

    context.user_data['stats'][stat_choice] += 2
    context.user_data['asi_points_applied'] += 2

    if 'talenti_da_scegliere' in context.user_data and context.user_data['talenti_da_scegliere'] > 0:
        await update.message.reply_text("Ottimo. Ora scegli il tuo talento:",
            reply_markup=ReplyKeyboardMarkup([list(talenti_disponibili.keys())[i:i+2] for i in range(0, len(talenti_disponibili), 2)], one_time_keyboard=True)
        )
        context.user_data['talenti_da_scegliere'] -= 1
        return SCEGLI_TALENTO_1

    await finalize_character(update, context)
    return ConversationHandler.END

async def scegli_talento_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feat_choice = update.message.text
    classe = context.user_data['classe']
    if feat_choice not in talenti_per_classe.get(classe, []):
        await update.message.reply_text("Talento non valido. Riprova.")
        return SCEGLI_TALENTO_1
    
    context.user_data['talenti'].append(feat_choice)

    if context.user_data.get('talenti_da_scegliere', 0) > 0:
        context.user_data['talenti_da_scegliere'] -= 1
        await update.message.reply_text("Scegli il tuo prossimo talento:",
            reply_markup=ReplyKeyboardMarkup([list(talenti_per_classe.get(classe, []))[i:i+2] for i in range(0, len(talenti_per_classe.get(classe, [])), 2)], one_time_keyboard=True)
        )
        return SCEGLI_TALENTO_2
    
    await finalize_character(update, context)
    return ConversationHandler.END

async def scegli_talento_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feat_choice = update.message.text
    classe = context.user_data['classe']
    if feat_choice not in talenti_per_classe.get(classe, []):
        await update.message.reply_text("Talento non valido. Riprova.")
        return SCEGLI_TALENTO_2
    
    context.user_data['talenti'].append(feat_choice)

    await finalize_character(update, context)
    return ConversationHandler.END

async def finalize_or_next_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('talenti_da_scegliere', 0) > 0:
        classe = context.user_data['classe']
        context.user_data['talenti_da_scegliere'] -= 1
        await update.message.reply_text("Perfetto. Ora scegli il tuo talento:",
            reply_markup=ReplyKeyboardMarkup([list(talenti_per_classe.get(classe, []))[i:i+2] for i in range(0, len(talenti_per_classe.get(classe, [])), 2)], one_time_keyboard=True)
        )
        return SCEGLI_TALENTO_1
    else:
        await finalize_character(update, context)
        return ConversationHandler.END

async def finalize_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats_final = context.user_data['stats']
    talenti_final = ", ".join(context.user_data['talenti']) if context.user_data['talenti'] else "Nessuno"

    message = (
        "<b>Personaggio generato! ✨</b>\n\n"
        f"<b>Classe:</b> {context.user_data['classe']}\n"
        f"<b>Sottoclasse:</b> {context.user_data['sottoclasse']}\n"
        f"<b>Livello:</b> {context.user_data['livello']}\n\n"
        "<b>Statistiche Finali:</b>\n"
        f"Forza: {stats_final['Forza']}\n"
        f"Destrezza: {stats_final['Destrezza']}\n"
        f"Costituzione: {stats_final['Costituzione']}\n"
        f"Intelligenza: {stats_final['Intelligenza']}\n"
        f"Saggezza: {stats_final['Saggezza']}\n"
        f"Carisma: {stats_final['Carisma']}\n\n"
        f"<b>Talenti:</b> {talenti_final}"
    )

    await update.message.reply_html(message, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Creazione personaggio annullata.', reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def main():
    if not TELEGRAM_TOKEN:
        print("Errore: il token Telegram non è stato impostato come variabile d'ambiente.")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("crea", crea)],
        states={
            SCEGLI_CLASSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, classe_scelta)],
            SCEGLI_SOTTOCLASSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sottoclasse_scelta)],
            SCEGLI_LIVELLO: [MessageHandler(filters.TEXT & ~filters.COMMAND, livello_scelto)],
            SCEGLI_BONUS_LIV4: [MessageHandler(filters.TEXT & ~filters.COMMAND, scegli_bonus_liv4)],
            SCEGLI_BONUS_LIV8: [MessageHandler(filters.TEXT & ~filters.COMMAND, scegli_bonus_liv8)],
            APPLICA_ASI_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, applica_asi_1)],
            APPLICA_ASI_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, applica_asi_2)],
            SCEGLI_TALENTO_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, scegli_talento_1)],
            SCEGLI_TALENTO_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, scegli_talento_2)],
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('start', start))
    print("Bot avviato... premi Ctrl+C per fermarlo.")
    app.run_polling(poll_interval=2.0)

if __name__ == "__main__":
    main()