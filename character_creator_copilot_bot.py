from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
import random

# Sostituisci questo con il tuo token API
TELEGRAM_TOKEN = "8302793448:AAHrfBj1RaWc1BpTcsmP-Y9K4RC0GjkVHWE"

# Stati della conversazione
SCEGLI_CLASSE, SCEGLI_SOTTOCLASSE, SCEGLI_LIVELLO = range(3)

# Dati completi di D&D 5e per classi e sottoclassi
classi_disponibili = {
    'Barbaro': ['Sentiero del Berserker', 'Sentiero del Guerriero Totemico', 'Sentiero del Furioso', 'Sentiero del Mago Selvaggio'],
    'Bardo': ['Collegio della Sapienza', 'Collegio del Valore', 'Collegio della Fama', 'Collegio della Spada'],
    'Chierico': ['Dominio della Conoscenza', 'Dominio della Guerra', 'Dominio della Vita', 'Dominio della Luce'],
    'Druido': ['Circolo della Terra', 'Circolo della Luna', 'Circolo delle Stelle', 'Circolo del Fuoco Selvaggio'],
    'Guerriero': ['Maestro di Battaglia', 'Cavaliere Mistico', 'Campione', 'Cavaliere Runico'],
    'Mago': ['Scuola di Invocazione', 'Scuola di Divinazione', 'Scuola di Abjurazione', 'Scuola di Illusione'],
    'Ladro': ['Ladro', 'Assassino', 'Ingannatore Arcano', 'Inquisitore'],
    'Stregone': ['Stirpe Draconica', 'Magia Selvaggia', 'Anima Divina', 'Stregone della Marea'],
    'Warlock': ['Il Patrono Celestiale', 'Il Patrono Fatato', 'L\'Immortale', 'L\'Arcifata'],
    'Monaco': ['Via della Mano Aperta', 'Via dell\'Ombra', 'Via del Sole Nascente', 'Via del Kensei'],
    'Ranger': ['Cacciatore', 'Maestro delle Bestie', 'Esploratore', 'Vagabondo Fatato'],
    'Paladino': ['Giuramento di Devozione', 'Giuramento di Vendetta', 'Giuramento degli Antichi', 'Giuramento di Gloria'],
}

# Associazione delle statistiche primarie per ogni classe
stat_primarie = {
    'Barbaro': ['Forza', 'Costituzione'],
    'Bardo': ['Carisma', 'Destrezza'],
    'Chierico': ['Saggezza', 'Forza'],
    'Druido': ['Saggezza', 'Costituzione'],
    'Guerriero': ['Forza', 'Costituzione'],
    'Mago': ['Intelligenza', 'Costituzione'],
    'Ladro': ['Destrezza', 'Intelligenza'],
    'Stregone': ['Carisma', 'Costituzione'],
    'Warlock': ['Carisma', 'Destrezza'],
    'Monaco': ['Destrezza', 'Saggezza'],
    'Ranger': ['Destrezza', 'Saggezza'],
    'Paladino': ['Forza', 'Carisma'],
}

# 🎲 Logica del lancio dei dadi (la stessa, ma i risultati vengono ordinati)
def roll_dnd_stats():
    """Genera 6 valori per le statistiche usando il metodo 4d6, eliminando il più basso."""
    stats_list = []
    for _ in range(6):
        rolls = [random.randint(1, 6) for _ in range(4)]
        rolls.sort()
        stats_list.append(sum(rolls[1:]))
    stats_list.sort(reverse=True) # Ordina i valori dal più alto al più basso
    return stats_list

def assign_stats(class_name, stats_values):
    """Assegna i punteggi lanciati in base alle statistiche primarie della classe."""
    primary_stats = stat_primarie.get(class_name, [])
    
    # Inizializza tutte le statistiche a 0
    all_stats = {
        'Forza': 0, 'Destrezza': 0, 'Costituzione': 0, 
        'Intelligenza': 0, 'Saggezza': 0, 'Carisma': 0
    }
    
    # Assegna i punteggi più alti alle statistiche primarie
    assigned_count = 0
    for stat in primary_stats:
        if assigned_count < len(stats_values):
            all_stats[stat] = stats_values[assigned_count]
            assigned_count += 1
    
    # Assegna i restanti punteggi alle altre statistiche
    remaining_stats = [stat for stat in all_stats.keys() if stat not in primary_stats]
    for stat in remaining_stats:
        if assigned_count < len(stats_values):
            all_stats[stat] = stats_values[assigned_count]
            assigned_count += 1
            
    return all_stats

# 🤖 Funzioni per gestire gli stati della conversazione (aggiornate)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce il comando /start e termina la conversazione se attiva."""
    if 'conversazione' in context.user_data:
        context.user_data.clear()
        await update.message.reply_text('Conversazione di creazione annullata. Riprova con /crea.')
    else:
        await update.message.reply_text("Benvenuto! Invia il comando /crea per iniziare a creare un nuovo personaggio.")
        
    return ConversationHandler.END

async def crea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inizia la conversazione chiedendo la classe."""
    reply_keyboard = [list(classi_disponibili.keys())[i:i+3] for i in range(0, len(classi_disponibili), 3)]
    await update.message.reply_text(
        "Ottimo! Per iniziare, quale classe vuoi scegliere?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Scegli una classe")
    )
    return SCEGLI_CLASSE

async def classe_scelta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salva la classe e chiede la sottoclasse."""
    user_choice = update.message.text
    if user_choice not in classi_disponibili:
        await update.message.reply_text(
            "Per favore, scegli una classe dalla lista."
        )
        return SCEGLI_CLASSE
        
    context.user_data['classe'] = user_choice
    sottoclassi = classi_disponibili[user_choice]
    reply_keyboard = [sottoclassi[i:i+2] for i in range(0, len(sottoclassi), 2)]
    
    await update.message.reply_text(
        f"Perfetto! E la sottoclasse di un {user_choice}?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Scegli una sottoclasse")
    )
    return SCEGLI_SOTTOCLASSE

async def sottoclasse_scelta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salva la sottoclasse e chiede il livello."""
    user_choice = update.message.text
    classe = context.user_data.get('classe')
    if user_choice not in classi_disponibili.get(classe, []):
        await update.message.reply_text(
            "Per favore, scegli una sottoclasse dalla lista."
        )
        return SCEGLI_SOTTOCLASSE
        
    context.user_data['sottoclasse'] = user_choice
    
    await update.message.reply_text(
        f"Ottimo! Infine, a quale livello è il tuo personaggio? (1-20)",
        reply_markup=ReplyKeyboardRemove()
    )
    return SCEGLI_LIVELLO

async def livello_scelto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salva il livello e genera il personaggio."""
    try:
        livello = int(update.message.text)
        if not 1 <= livello <= 20:
            raise ValueError
    except (ValueError, TypeError):
        await update.message.reply_text("Per favore, inserisci un numero da 1 a 20.")
        return SCEGLI_LIVELLO
        
    context.user_data['livello'] = livello
    
    # Genera le statistiche e le assegna in base alla classe
    stats_values = roll_dnd_stats()
    final_stats = assign_stats(context.user_data['classe'], stats_values)
    
    message = (
        "<b>Personaggio generato! ✨</b>\n\n"
        f"<b>Classe:</b> {context.user_data['classe']}\n"
        f"<b>Sottoclasse:</b> {context.user_data['sottoclasse']}\n"
        f"<b>Livello:</b> {context.user_data['livello']}\n\n"
        "<b>Statistiche generate:</b>\n"
        f"Forza: {final_stats['Forza']}\n"
        f"Destrezza: {final_stats['Destrezza']}\n"
        f"Costituzione: {final_stats['Costituzione']}\n"
        f"Intelligenza: {final_stats['Intelligenza']}\n"
        f"Saggezza: {final_stats['Saggezza']}\n"
        f"Carisma: {final_stats['Carisma']}\n"
    )

    await update.message.reply_html(message, reply_markup=ReplyKeyboardRemove())
    
    context.user_data.clear()
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Annulla la conversazione."""
    await update.message.reply_text('Creazione personaggio annullata.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# 🚀 Avvio del bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("crea", crea)],
        states={
            SCEGLI_CLASSE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, classe_scelta)
            ],
            SCEGLI_SOTTOCLASSE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, sottoclasse_scelta)
            ],
            SCEGLI_LIVELLO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, livello_scelto)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('start', start))

    print("Bot avviato... premi Ctrl+C per fermarlo.")
    app.run_polling()

if __name__ == "__main__":
    main()