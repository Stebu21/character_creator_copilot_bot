from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
import random
import os

TELEGRAM_TOKEN = "Inserire telegram token"

# Stati della conversazione
(
    QUANTI_PERSONAGGI, SCEGLI_CLASSE, SCEGLI_SOTTOCLASSE, SCEGLI_LIVELLO,
    SCEGLI_BONUS_LIV4, SCEGLI_BONUS_LIV8, APPLICA_ASI_1,
    SCEGLI_TALENTO_1, FINE_CREAZIONE
) = range(9)

# Dati di D&D - LISTA COMPLETA
classi_disponibili = {
    'Barbaro': ['Sentiero del Berserker', 'Sentiero del Guerriero Totemico', 'Sentiero del Predatore', 'Sentiero del Giuramento'],
    'Bardo': ['Collegio del Sapere', 'Collegio della Valor', 'Collegio della Glielamagia', 'Collegio delle Spade', 'Collegio della Creazione', 'Collegio dell\'Eloquenza'],
    'Chierico': ['Dominio della Conoscenza', 'Dominio della Vita', 'Dominio della Luce', 'Dominio della Natura', 'Dominio della Tempesta', 'Dominio dell\'Inganno', 'Dominio della Guerra', 'Dominio del Cimitero', 'Dominio della Forgia', 'Dominio della Grazia', 'Dominio del Tempo', 'Dominio della Pace'],
    'Druido': ['Circolo della Terra', 'Circolo della Luna', 'Circolo del Pastore', 'Circolo del Sogno', 'Circolo delle Spore'],
    'Guerriero': ['Maestro di Battaglia', 'Cavaliere Mistico', 'Campione', 'Cavaliere Runa', 'Cavaliere Samurai', 'Cavaliere Spirituale', 'Maestro d\'Armi', 'Cavaliere Runa'],
    'Ladro': ['Ladro', 'Assassino', 'Mistificatore Arcano', 'Inquisitore', 'Maestro della Lama Ombra', 'Spirito della Notte'],
    'Mago': ['Scuola di Invocazione', 'Scuola di Divinazione', 'Scuola di Abjurazione', 'Scuola di Ammaliamento', 'Scuola di Necromanzia', 'Scuola di Trasmutazione', 'Scuola di Illusione', 'Bladesinger', 'War Mage'],
    'Monaco': ['Via della Mano Aperta', 'Via della Sombra', 'Via dei Quattro Elementi', 'Via del Kensei', 'Via del Drago Ascendente', 'Via dell\'Anima del Teschio'],
    'Paladino': ['Giuramento di Devozione', 'Giuramento degli Antichi', 'Giuramento di Vendetta', 'Giuramento della Conquista', 'Giuramento della Redenzione', 'Giuramento della Gloria'],
    'Ranger': ['Cacciatore', 'Maestro delle Bestie', 'Cacciatore della Notte', 'Cercatore di Sentieri', 'Gloomy Hunter', 'Cacciatore di Draghi', 'Maestro delle Bestie'],
    'Stregone': ['Stirpe Draconica', 'Magia Selvaggia', 'Stirpe Ombra', 'Magia di Tempesta', 'Magia Criptica', 'Anima di Fuoco'],
    'Warlock': ['Il Signore', 'L\'Immortale', 'L\'Arcifata', 'Il Grande Antico', 'Il Celestiale', 'Il Genio', 'Il Mutaforma'],
    'Artefice': ['Alchimista', 'Armaiolo', 'Artigliere', 'Fabbro delle Rune'],
    'Mago da Guerra': ['Scuola di Abjurazione', 'Scuola di Divinazione', 'Scuola di Evocazione', 'Scuola di Necromanzia', 'Scuola di Trasmutazione', 'Scuola di Illusione'],
}

stat_primarie = {
    'Barbaro': ['Forza', 'Costituzione'],
    'Bardo': ['Carisma', 'Destrezza'],
    'Chierico': ['Saggezza', 'Forza'],
    'Druido': ['Saggezza', 'Costituzione'],
    'Guerriero': ['Forza', 'Costituzione'],
    'Ladro': ['Destrezza', 'Intelligenza'],
    'Mago': ['Intelligenza', 'Costituzione'],
    'Monaco': ['Destrezza', 'Saggezza'],
    'Paladino': ['Forza', 'Carisma'],
    'Ranger': ['Destrezza', 'Saggezza'],
    'Stregone': ['Carisma', 'Costituzione'],
    'Warlock': ['Carisma', 'Costituzione'],
    'Artefice': ['Intelligenza', 'Costituzione'],
    'Mago da Guerra': ['Intelligenza', 'Costituzione'],
}

talenti_per_classe = {
    'Barbaro': ['Sentinel', 'Tough', 'Great Weapon Master', 'Polearm Master', 'Mobile', 'Resilient (Constitution)', 'Martial Adept'],
    'Bardo': ['War Caster', 'Spell Sniper', 'Resilient (Charisma)', 'Inspiring Leader', 'Fey Touched', 'Shadow Touched'],
    'Chierico': ['War Caster', 'Spell Sniper', 'Elemental Adept', 'Resilient (Wisdom)', 'Healer', 'Fey Touched'],
    'Druido': ['War Caster', 'Spell Sniper', 'Resilient (Wisdom)', 'Elemental Adept', 'Fey Touched', 'Magic Initiate'],
    'Guerriero': ['Great Weapon Master', 'Polearm Master', 'Sentinel', 'Sharpshooter', 'Crossbow Expert', 'Mobile', 'Tough', 'Martial Adept', 'Resilient (Strength)'],
    'Ladro': ['Alert', 'Skulker', 'Sharpshooter', 'Mobile', 'Defensive Duelist', 'Resilient (Dexterity)', 'Sentinel'],
    'Mago': ['War Caster', 'Elemental Adept', 'Resilient (Constitution)', 'Spell Sniper', 'Fey Touched', 'Shadow Touched', 'Ritual Caster'],
    'Monaco': ['Mobile', 'Sentinel', 'Tough', 'Resilient (Wisdom)', 'Alert'],
    'Paladino': ['Sentinel', 'Great Weapon Master', 'Polearm Master', 'Shield Master', 'Inspiring Leader', 'Resilient (Charisma)'],
    'Ranger': ['Sharpshooter', 'Crossbow Expert', 'Sentinel', 'Skulker', 'Mobile', 'Resilient (Dexterity)'],
    'Stregone': ['War Caster', 'Spell Sniper', 'Elemental Adept', 'Resilient (Charisma)', 'Fey Touched', 'Shadow Touched'],
    'Warlock': ['War Caster', 'Spell Sniper', 'Fey Touched', 'Shadow Touched', 'Resilient (Charisma)', 'Inspiring Leader'],
    'Artefice': ['Artificer Initiate', 'Infusion', 'Resilient (Constitution)', 'Fey Touched', 'Elemental Adept'],
    'Mago da Guerra': ['War Caster', 'Spell Sniper', 'Elemental Adept', 'Resilient (Intelligence)', 'Fey Touched', 'Ritual Caster'],
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
    await update.message.reply_text("Benvenuto! Quanti personaggi vuoi creare? (1-10)", reply_markup=ReplyKeyboardRemove())
    return QUANTI_PERSONAGGI

async def quanti_personaggi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num_personaggi = int(update.message.text)
        if not 1 <= num_personaggi <= 10:
            raise ValueError
    except (ValueError, TypeError):
        await update.message.reply_text("Per favore, inserisci un numero valido da 1 a 10.")
        return QUANTI_PERSONAGGI

    context.user_data['num_rimanenti'] = num_personaggi
    context.user_data['num_personaggi_iniziali'] = num_personaggi
    return await inizia_creazione_personaggio(update, context)

async def inizia_creazione_personaggio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('num_rimanenti', 0) <= 0:
        await update.message.reply_text("Creazione terminata. Grazie!", reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    
    context.user_data['num_rimanenti'] -= 1
    context.user_data['talenti'] = []

    reply_keyboard = [list(classi_disponibili.keys())[i:i + 3] for i in range(0, len(classi_disponibili), 3)]
    
    message_text = (
        f"Creazione personaggio #{context.user_data['num_personaggi_iniziali'] - context.user_data['num_rimanenti']}/{context.user_data['num_personaggi_iniziali']}\n"
        "Per iniziare, quale classe vuoi scegliere?"
    )

    await update.message.reply_text(
        message_text,
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
    context.user_data['punti_asi_da_distribuire'] = 0
    
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
    
    return await finalize_character(update, context)

async def scegli_bonus_liv4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == '2 punti nelle statistiche':
        context.user_data['punti_asi_da_distribuire'] = 2
        await update.message.reply_text(
            "Perfetto! Scegli la prima statistica da aumentare di 1 punto.",
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
        context.user_data['punti_asi_da_distribuire'] = 4
        await update.message.reply_text(
            "Perfetto! Scegli la prima statistica da aumentare di 1 punto. (Hai 4 punti da distribuire)",
            reply_markup=ReplyKeyboardMarkup([['Forza', 'Destrezza', 'Costituzione'], ['Intelligenza', 'Saggezza', 'Carisma']], one_time_keyboard=True)
        )
        return APPLICA_ASI_1
    elif choice == '1 ASI + 1 Talento':
        context.user_data['punti_asi_da_distribuire'] = 2
        context.user_data['talenti_da_scegliere'] = 1
        await update.message.reply_text(
            "Perfetto! Scegli la prima statistica da aumentare di 1 punto.",
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
    
    context.user_data['stats'][stat_choice] += 1
    context.user_data['punti_asi_da_distribuire'] -= 1
    
    if context.user_data['punti_asi_da_distribuire'] > 0:
        await update.message.reply_text(
            f"Ottimo. Scegli un'altra statistica da aumentare di 1 punto. Ti rimangono {context.user_data['punti_asi_da_distribuire']} punti.",
            reply_markup=ReplyKeyboardMarkup([['Forza', 'Destrezza', 'Costituzione'], ['Intelligenza', 'Saggezza', 'Carisma']], one_time_keyboard=True)
        )
        return APPLICA_ASI_1
    
    return await gestisci_transizione(update, context)


async def scegli_talento_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feat_choice = update.message.text
    classe = context.user_data['classe']
    if feat_choice not in talenti_per_classe.get(classe, []):
        await update.message.reply_text("Talento non valido. Riprova.")
        return SCEGLI_TALENTO_1
    
    context.user_data['talenti'].append(feat_choice)
    context.user_data['talenti_da_scegliere'] -= 1

    return await gestisci_transizione(update, context)

async def gestisci_transizione(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('talenti_da_scegliere', 0) > 0:
        classe = context.user_data['classe']
        talenti_disponibili_per_classe = talenti_per_classe.get(classe, [])
        reply_keyboard = [talenti_disponibili_per_classe[i:i+2] for i in range(0, len(talenti_disponibili_per_classe), 2)]
        
        await update.message.reply_text("Ora scegli il tuo prossimo talento:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return SCEGLI_TALENTO_1
    else:
        return await finalize_character(update, context)

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
    
    # Continua la creazione se ci sono altri personaggi
    if context.user_data.get('num_rimanenti', 0) > 0:
        return await inizia_creazione_personaggio(update, context)
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Creazione personaggio annullata.', reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

async def next_char(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('num_rimanenti', 0) > 0:
        return await inizia_creazione_personaggio(update, context)
    await update.message.reply_text('Nessun altro personaggio da creare. Invia /crea per iniziare.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    if not TELEGRAM_TOKEN:
        print("Errore: il token Telegram non è stato impostato come variabile d'ambiente.")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("crea", start)],
        states={
            QUANTI_PERSONAGGI: [MessageHandler(filters.TEXT & ~filters.COMMAND, quanti_personaggi)],
            SCEGLI_CLASSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, classe_scelta)],
            SCEGLI_SOTTOCLASSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sottoclasse_scelta)],
            SCEGLI_LIVELLO: [MessageHandler(filters.TEXT & ~filters.COMMAND, livello_scelto)],
            SCEGLI_BONUS_LIV4: [MessageHandler(filters.TEXT & ~filters.COMMAND, scegli_bonus_liv4)],
            SCEGLI_BONUS_LIV8: [MessageHandler(filters.TEXT & ~filters.COMMAND, scegli_bonus_liv8)],
            APPLICA_ASI_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, applica_asi_1)],
            SCEGLI_TALENTO_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, scegli_talento_1)],
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start), CommandHandler('next', next_char)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('next', next_char))
    print("Bot avviato... premi Ctrl+C per fermarlo.")
    app.run_polling(poll_interval=2.0)

if __name__ == "__main__":
    main()
