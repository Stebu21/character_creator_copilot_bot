from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
import random
import os

# Ottimizzazione per la produzione: usa variabili d'ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8302793448:AAHrfBj1RaWc1BpTcsmP-Y9K4RC0GjkVHWE")
if TELEGRAM_TOKEN == "8302793448:AAHrfBj1RaWc1BpTcsmP-Y9K4RC0GjkVHWE":
    print("ATTENZIONE: Il token Telegram non è stato impostato come variabile d'ambiente. Usando il valore di default.")

# Stati della conversazione
(
    QUANTI_PERSONAGGI, ASSEGNA_STAT, SCEGLI_CLASSE, SCEGLI_SOTTOCLASSE, SCEGLI_EQUIPAGGIAMENTO,
    SCEGLI_LIVELLO, SCEGLI_BONUS, APPLICA_ASI, SCEGLI_TALENTO, SCEGLI_TRUCCHETTI_E_INCANTESIMI,
    SCEGLI_LINGUE, INSERISCI_NOME, SCEGLI_RAZZA,
) = range(13)

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

razze_disponibili = ['Umano', 'Elfo', 'Halfling', 'Nano', 'Dragonide', 'Gnomo', 'Mezzelfo', 'Mezzorco', 'Tiefling']

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
    'Barbaro': ['Sentinel', 'Tough', 'Great Weapon Master', 'Polearm Master', 'Mobile', 'Resilient (Costituzione)', 'Martial Adept'],
    'Bardo': ['War Caster', 'Spell Sniper', 'Resilient (Carisma)', 'Inspiring Leader', 'Fey Touched', 'Shadow Touched'],
    'Chierico': ['War Caster', 'Spell Sniper', 'Elemental Adept', 'Resilient (Saggezza)', 'Healer', 'Fey Touched'],
    'Druido': ['War Caster', 'Spell Sniper', 'Resilient (Saggezza)', 'Elemental Adept', 'Fey Touched', 'Magic Initiate'],
    'Guerriero': ['Great Weapon Master', 'Polearm Master', 'Sentinel', 'Sharpshooter', 'Crossbow Expert', 'Mobile', 'Tough', 'Martial Adept', 'Resilient (Forza)'],
    'Ladro': ['Alert', 'Skulker', 'Sharpshooter', 'Mobile', 'Defensive Duelist', 'Resilient (Destrezza)', 'Sentinel'],
    'Mago': ['War Caster', 'Elemental Adept', 'Resilient (Costituzione)', 'Spell Sniper', 'Fey Touched', 'Shadow Touched', 'Ritual Caster'],
    'Monaco': ['Mobile', 'Sentinel', 'Tough', 'Resilient (Saggezza)', 'Alert'],
    'Paladino': ['Sentinel', 'Great Weapon Master', 'Polearm Master', 'Shield Master', 'Inspiring Leader', 'Resilient (Carisma)'],
    'Ranger': ['Sharpshooter', 'Crossbow Expert', 'Sentinel', 'Skulker', 'Mobile', 'Resilient (Destrezza)'],
    'Stregone': ['War Caster', 'Spell Sniper', 'Elemental Adept', 'Resilient (Carisma)', 'Fey Touched', 'Shadow Touched'],
    'Warlock': ['War Caster', 'Spell Sniper', 'Fey Touched', 'Shadow Touched', 'Resilient (Carisma)', 'Inspiring Leader'],
    'Artefice': ['Artificer Initiate', 'Infusion', 'Resilient (Costituzione)', 'Fey Touched', 'Elemental Adept'],
    'Mago da Guerra': ['War Caster', 'Spell Sniper', 'Elemental Adept', 'Resilient (Intelligenza)', 'Fey Touched', 'Ritual Caster'],
}

competenze_iniziali = {
    'Barbaro': {'armature': ['leggera', 'media', 'scudo'], 'armi': ['semplice', 'da guerra'], 'attrezzi': []},
    'Bardo': {'armature': ['leggera'], 'armi': ['semplice', 'balestra a mano', 'spada lunga', 'stocco', 'spada corta'], 'attrezzi': ['strumento musicale (3)'], 'sottoclasse': {'Collegio della Valor': {'armature': ['media', 'scudo'], 'armi': ['da guerra']}}},
    'Chierico': {'armature': ['leggera', 'media', 'scudo'], 'armi': ['semplice'], 'attrezzi': [], 'sottoclasse': {'Dominio della Vita': {'armature': ['pesante']}, 'Dominio della Guerra': {'armature': ['pesante'], 'armi': ['da guerra']}, 'Dominio della Forgia': {'armature': ['pesante']}}},
    'Druido': {'armature': ['leggera', 'media', 'scudo'], 'armi': ['semplice'], 'attrezzi': ['erborista'], 'note': 'Non indossano armature o scudi di metallo.'},
    'Guerriero': {'armature': ['leggera', 'media', 'pesante', 'scudo'], 'armi': ['semplice', 'da guerra'], 'attrezzi': []},
    'Ladro': {'armature': ['leggera'], 'armi': ['semplice', 'spada lunga', 'stocco', 'balestra a mano'], 'attrezzi': ['attrezzi da scasso']},
    'Mago': {'armature': [], 'armi': ['pugnale', 'dardo', 'fionda', 'bastone', 'balestra leggera'], 'attrezzi': []},
    'Monaco': {'armature': [], 'armi': ['semplice', 'spada corta'], 'attrezzi': ['un tipo di attrezzi da artigiano o uno strumento musicale']},
    'Paladino': {'armature': ['leggera', 'media', 'pesante', 'scudo'], 'armi': ['semplice', 'da guerra'], 'attrezzi': []},
    'Ranger': {'armature': ['leggera', 'media', 'scudo'], 'armi': ['semplice', 'da guerra'], 'attrezzi': []},
    'Stregone': {'armature': ['leggera'], 'armi': ['semplice'], 'attrezzi': []},
    'Warlock': {'armature': ['leggera'], 'armi': ['semplice'], 'attrezzi': []},
    'Artefice': {'armature': ['leggera', 'media', 'scudo'], 'armi': ['semplice', 'da guerra'], 'attrezzi': ['attrezzi da artigiano (2)']},
    'Mago da Guerra': {'armature': [], 'armi': ['semplice', 'pugnale', 'dardo', 'fionda', 'bastone', 'balestra leggera'], 'attrezzi': []},
}

equipaggiamento_iniziale_nuovo = {
    'Barbaro': {'scelta_1': ['Ascia bipenne', 'Qualsiasi arma marziale da mischia'], 'scelta_2': ['Due asce da mano', 'Qualsiasi arma semplice'], 'fisso': ['Un pacchetto da esploratore', 'Quattro giavellotti']},
    'Bardo': {'scelta_1': ['Stocco', 'Spada lunga', 'Qualsiasi arma semplice'], 'scelta_2': ['Un pacchetto da diplomatico', 'Un pacchetto da intrattenitore'], 'scelta_3': ['Liuto', 'Qualsiasi altro strumento musicale'], 'fisso': ['Armatura di cuoio', 'Pugnale']},
    'Chierico': {'scelta_1': ['Mazza', 'Martello da guerra'], 'scelta_2': ['Balestra leggera e 20 dardi', 'Qualsiasi arma semplice da mischia'], 'scelta_3': ['Un pacchetto da sacerdote', 'Un pacchetto da esploratore'], 'fisso': ['Scudo', 'Simbolo sacro']},
    'Druido': {'scelta_1': ['Scudo di legno', 'Qualsiasi arma semplice'], 'scelta_2': ['Scimitarra', 'Qualsiasi arma da mischia semplice'], 'fisso': ['Armatura di cuoio', 'Un pacchetto da esploratore', 'Focus druidico']},
    'Guerriero': {'scelta_1': ['Armatura di maglia', 'Armatura di cuoio, arco lungo e 20 frecce'], 'scelta_2': ['Un\'arma marziale e uno scudo', 'Due armi marziali'], 'scelta_3': ['Una balestra leggera e 20 dardi', 'Due asce da mano'], 'scelta_4': ['Un pacchetto da avventuriero', 'Un pacchetto da esploratore']},
    'Ladro': {'scelta_1': ['Stocco', 'Spada corta'], 'scelta_2': ['Arco corto e 20 frecce', 'Spada corta'], 'scelta_3': ['Pacchetto da scassinatore', 'Pacchetto da avventuriero', 'Pacchetto da esploratore'], 'fisso': ['Armatura di cuoio', 'Due pugnali', 'Attrezzi da scasso']},
    'Mago': {'scelta_1': ['Bastone', 'Pugnale'], 'scelta_2': ['Pacchetto da studioso', 'Pacchetto da avventuriero'], 'scelta_3': ['Borsa dei componenti', 'Focus arcano'], 'fisso': ['Libro degli incantesimi']},
    'Monaco': {'scelta_1': ['Spada corta', 'Qualsiasi arma semplice'], 'scelta_2': ['Pacchetto da avventuriero', 'Pacchetto da esploratore'], 'fisso': ['10 giavellotti']},
    'Paladino': {'scelta_1': ['Un\'arma marziale e uno scudo', 'Due armi marziali'], 'scelta_2': ['Cinque giavellotti', 'Un\'arma da mischia semplice'], 'scelta_3': ['Un pacchetto da sacerdote', 'Un pacchetto da esploratore'], 'fisso': ['Armatura di maglia', 'Simbolo sacro']},
    'Ranger': {'scelta_1': ['Armatura di maglia', 'Armatura di cuoio'], 'scelta_2': ['Due spade corte', 'Due armi semplici'], 'scelta_3': ['Un pacchetto da avventuriero', 'Un pacchetto da esploratore'], 'fisso': ['Arco lungo', '20 frecce']},
    'Stregone': {'scelta_1': ['Balestra leggera e 20 dardi', 'Qualsiasi arma semplice'], 'scelta_2': ['Borsa dei componenti', 'Focus arcano'], 'scelta_3': ['Pacchetto da avventuriero', 'Pacchetto da esploratore'], 'fisso': ['Due pugnali']},
    'Warlock': {'scelta_1': ['Balestra leggera e 20 dardi', 'Qualsiasi arma semplice'], 'scelta_2': ['Borsa dei componenti', 'Focus arcano'], 'scelta_3': ['Pacchetto da studioso', 'Pacchetto da avventuriero'], 'fisso': ['Armatura di cuoio', 'Due pugnali']},
    'Artefice': {'scelta_1': ['Martello da guerra', 'Qualsiasi arma semplice'], 'scelta_2': ['Balestra leggera e 20 dardi', 'Qualsiasi arma semplice'], 'scelta_3': ['Pacchetto da avventuriero', 'Pacchetto da esploratore'], 'fisso': ['Armatura di scaglie', 'Scudo', 'Una serie di attrezzi da artigiano', 'Una serie di attrezzi da scasso']},
    'Mago da Guerra': {'scelta_1': ['Balestra leggera e 20 dardi', 'Qualsiasi arma semplice'], 'scelta_2': ['Un\'armatura di cuoio', 'Un\'armatura di scaglie'], 'scelta_3': ['Uno scudo', 'Nessuno scudo'], 'scelta_4': ['Un pacchetto da avventuriero', 'Un pacchetto da studioso']},
}

lingue_conoscibili = {
    'standard': ['Nano', 'Elfico', 'Gigante', 'Gnomesco', 'Goblin', 'Halfling', 'Orchesco'],
    'esotiche': ['Abissale', 'Celestiale', 'Draconico', 'Infernale', 'Primordiale', 'Sottocomune'],
}

incantatori = ['Mago', 'Stregone', 'Warlock', 'Chierico', 'Bardo', 'Druido', 'Paladino', 'Ranger', 'Artefice']

magie_iniziali = {
    'Mago': {'trucchetti': 3, 'incantesimi': 6},
    'Stregone': {'trucchetti': 4, 'incantesimi': 2},
    'Warlock': {'trucchetti': 2, 'incantesimi': 2},
    'Chierico': {'trucchetti': 3, 'incantesimi': 0}, # I chierici scelgono incantesimi ogni giorno, ma trucchetti sono fissi.
    'Bardo': {'trucchetti': 2, 'incantesimi': 4},
    'Druido': {'trucchetti': 2, 'incantesimi': 0}, # I druidi scelgono incantesimi ogni giorno, ma trucchetti sono fissi.
    'Paladino': {'trucchetti': 0, 'incantesimi': 0}, # I Paladini non hanno trucchetti e ottengono incantesimi al 2° livello
    'Ranger': {'trucchetti': 0, 'incantesimi': 0}, # I Ranger non hanno trucchetti e ottengono incantesimi al 2° livello
    'Artefice': {'trucchetti': 2, 'incantesimi': 2},
}

trucchetti_disponibili = {
    'Bardo': ['Lame Cantanti', 'Fiamma del Mago', 'Illusione Minore', 'Luce', 'Prestigiazione', 'Scherzo di Spettri'],
    'Chierico': ['Fiamma Sacra', 'Guida', 'Lama della Fiamma', 'Luce', 'Resistenza', 'Taumaturgia'],
    'Druido': ['Frustata di Spine', 'Guida', 'Infestare', 'Lame Cantanti', 'Pugno di Pietra', 'Spruzzo Velenoso'],
    'Mago': ['Dardo di Fuoco', 'Fiamma del Mago', 'Illusione Minore', 'Luce', 'Mano Magica', 'Prestigiazione'],
    'Stregone': ['Dardo di Fuoco', 'Fiamma del Mago', 'Illusione Minore', 'Luce', 'Mano Magica', 'Spruzzo Velenoso'],
    'Warlock': ['Contatto Glaciale', 'Dardo Esplosivo', 'Fiamma del Mago', 'Illusione Minore', 'Mano Magica', 'Resistenza'],
    'Artefice': ['Lame Cantanti', 'Mano Magica', 'Riparare', 'Spruzzo Velenoso'],
}

incantesimi_disponibili = {
    'Bardo': ['Charme su Persona', 'Colpo Accurato', 'Dardo Incantato', 'Individuazione del Magico', 'Parola Guaritrice', 'Sonno'],
    'Chierico': ['Arma Spirituale', 'Benedizione', 'Ferire', 'Scudo della Fede', 'Onda Tonante', 'Parola Guaritrice'],
    'Druido': ['Onda di Marea', 'Camminare sull\'Acqua', 'Erbaccia', 'Incantesimi di cura', 'Rovina', 'Spruzzo Velenoso'],
    'Mago': ['Armatura Magica', 'Dardo Incantato', 'Mano Magica', 'Onda Tonante', 'Sonno', 'Raggio di Gelo'],
    'Stregone': ['Dardo Incantato', 'Mano Magica', 'Scudo', 'Sonno', 'Charme su Persona'],
    'Warlock': ['Charme su Persona', 'Dardo Incantato', 'Mano Magica', 'Raggio di Gelo', 'Sonno'],
    'Paladino': ['Incantesimi di Cura', 'Dardo Incantato'], # Incantesimi di 1° livello base
    'Ranger': ['Charme su Persona', 'Dardo Incantato'], # Incantesimi di 1° livello base
    'Artefice': ['Incantesimi di Cura', 'Dardo Incantato', 'Scudo'],
}


def roll_dnd_stats():
    """Tira 4d6 e somma i 3 più alti, ripetuto 6 volte."""
    stats_list = []
    for _ in range(6):
        rolls = sorted([random.randint(1, 6) for _ in range(4)])
        stats_list.append(sum(rolls[1:]))
    stats_list.sort(reverse=True)
    return stats_list

def assegna_competenze(class_name, subclass_name=None):
    """Calcola le competenze totali basate su classe e sottoclasse."""
    competenze = competenze_iniziali.get(class_name, {})
    proficienze = competenze.get('armature', []) + competenze.get('armi', []) + competenze.get('attrezzi', [])

    subclass_data = competenze.get('sottoclasse', {}).get(subclass_name, {})
    proficienze += subclass_data.get('armature', []) + subclass_data.get('armi', []) + subclass_data.get('attrezzi', [])

    return proficienze

def check_proficiency(option_str, proficiencies):
    """Verifica se l'utente è competente con un'opzione di equipaggiamento."""
    option_str_lower = option_str.lower()

    # Mappatura delle armature alle competenze
    armature_map = {
        'cuoio': 'leggera',
        'maglia': 'media',
        'scaglie': 'media',
        'piastre': 'pesante',
        'scudo': 'scudo',
    }

    # Controllo armature
    for armor, prof in armature_map.items():
        if armor in option_str_lower and prof in proficiencies:
            return True

    # Controllo armi
    if 'arma marziale' in option_str_lower and 'da guerra' in proficiencies: return True
    if 'arma semplice' in option_str_lower and 'semplice' in proficiencies: return True

    # Armi specifiche
    if 'stocco' in option_str_lower and 'stocco' in proficiencies: return True
    if 'spada lunga' in option_str_lower and 'spada lunga' in proficiencies: return True
    if 'spada corta' in option_str_lower and 'spada corta' in proficiencies: return True
    if 'pugnale' in option_str_lower and 'pugnale' in proficiencies: return True
    if 'arco' in option_str_lower and 'arco' in proficiencies: return True
    if 'balestra' in option_str_lower and 'balestra leggera' in proficiencies: return True
    if 'mazza' in option_str_lower and 'semplice' in proficiencies: return True # Caso specifico per Chierico
    if 'martello da guerra' in option_str_lower and 'semplice' in proficiencies: return True
    if 'ascia bipenne' in option_str_lower and 'da guerra' in proficiencies: return True
    if 'asce da mano' in option_str_lower and 'semplice' in proficiencies: return True
    if 'scimitarra' in option_str_lower and 'semplice' in proficiencies: return True
    if 'bastone' in option_str_lower and 'semplice' in proficiencies: return True
    if 'pugnale' in option_str_lower and 'semplice' in proficiencies: return True
    if 'giavellotti' in option_str_lower and 'semplice' in proficiencies: return True

    # Pacchetti e oggetti generici
    if any(item in option_str_lower for item in ['pacchetto', 'focus', 'borsa', 'liuto', 'giavellotti', 'dardi', 'frecce', 'libro', 'simbolo', 'scudo di legno', 'due pugnali', 'attrezzi da scasso', 'scudo']):
        return True

    return False

def get_asi_levels(classe, livello):
    levels = []
    base_levels = [4, 8, 12, 16, 19]
    if classe == 'Guerriero':
        base_levels.extend([6, 14])
    if classe == 'Ladro':
        base_levels.extend([10, 18])
    for l in base_levels:
        if l <= livello:
            levels.append(l)
    return sorted(list(set(levels)))

# Handlers
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
    context.user_data['equipaggiamento_scelto'] = []
    context.user_data['equipaggiamento_fisso'] = []
    context.user_data['competenze'] = []
    context.user_data['lingue'] = ['Comune']
    context.user_data['trucchetti_scelti'] = []
    context.user_data['incantesimi_scelti'] = []
    context.user_data['lista_incantesimi_da_scegliere'] = []
    context.user_data['lista_trucchetti_da_scegliere'] = []
    context.user_data['stats_da_assegnare'] = roll_dnd_stats()
    context.user_data['stats'] = {'Forza': 0, 'Destrezza': 0, 'Costituzione': 0, 'Intelligenza': 0, 'Saggezza': 0, 'Carisma': 0}

    message_text = f"Creazione personaggio #{context.user_data['num_personaggi_iniziali'] - context.user_data['num_rimanenti']}/{context.user_data['num_personaggi_iniziali']}\n"
    message_text += "Per prima cosa, che nome avrà il tuo personaggio?"
    await update.message.reply_text(message_text, reply_markup=ReplyKeyboardRemove())
    return INSERISCI_NOME

async def inserisci_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nome_personaggio = update.message.text.strip()
    if not nome_personaggio:
        await update.message.reply_text("Per favore, inserisci un nome valido.")
        return INSERISCI_NOME
    context.user_data['nome'] = nome_personaggio

    reply_keyboard = [razze_disponibili[i:i + 3] for i in range(0, len(razze_disponibili), 3)]
    await update.message.reply_text(
        f"Ottimo, {nome_personaggio}! Ora scegli la sua razza.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SCEGLI_RAZZA

async def scegli_razza(update: Update, context: ContextTypes.DEFAULT_TYPE):
    razza_scelta = update.message.text
    if razza_scelta not in razze_disponibili:
        await update.message.reply_text("Per favore, scegli una razza dalla lista.")
        return SCEGLI_RAZZA
    context.user_data['razza'] = razza_scelta

    stats_rolled = context.user_data['stats_da_assegnare']
    message_text = (
        f"Hai ottenuto i seguenti punteggi: {', '.join(map(str, stats_rolled))}\n\n"
        f"Scegli dove assegnare il tuo punteggio più alto, che è {stats_rolled[0]}."
    )
    reply_keyboard = [['Forza', 'Destrezza', 'Costituzione'], ['Intelligenza', 'Saggezza', 'Carisma']]

    await update.message.reply_text(
        message_text,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASSEGNA_STAT

async def assegna_stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stat_choice = update.message.text
    if stat_choice not in context.user_data['stats'] or context.user_data['stats'][stat_choice] != 0:
        await update.message.reply_text("Scelta non valida o statistica già assegnata. Scegli una statistica libera.")
        return ASSEGNA_STAT

    stats_da_assegnare = context.user_data['stats_da_assegnare']
    context.user_data['stats'][stat_choice] = stats_da_assegnare.pop(0)

    if not stats_da_assegnare:
        return await chiedi_classe(update, context)

    message = f"Punteggio {context.user_data['stats'][stat_choice]} assegnato a {stat_choice}.\n"
    message += f"Ora scegli dove assegnare il prossimo punteggio: {stats_da_assegnare[0]}"

    stats_libere = [s for s, v in context.user_data['stats'].items() if v == 0]
    reply_keyboard = [stats_libere[i:i + 3] for i in range(0, len(stats_libere), 3)]

    await update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASSEGNA_STAT

async def chiedi_classe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [list(classi_disponibili.keys())[i:i + 3] for i in range(0, len(classi_disponibili), 3)]
    await update.message.reply_text(
        "Ottimo! Ora scegli la classe.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SCEGLI_CLASSE

async def classe_scelta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text
    if user_choice not in classi_disponibili:
        await update.message.reply_text("Per favor, scegli una classe dalla lista.")
        return SCEGLI_CLASSE
    context.user_data['classe'] = user_choice

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

    context.user_data['competenze'] = assegna_competenze(classe, user_choice)

    equip_options = equipaggiamento_iniziale_nuovo.get(classe, {})
    context.user_data['opzioni_equip_rimanenti'] = [v for k, v in equip_options.items() if k.startswith('scelta')]
    context.user_data['equipaggiamento_fisso'] = equip_options.get('fisso', [])

    return await chiedi_equipaggiamento(update, context)

async def chiedi_equipaggiamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    opzioni_rimanenti = context.user_data.get('opzioni_equip_rimanenti')

    if not opzioni_rimanenti:
        return await chiedi_livello(update, context)

    opzioni = opzioni_rimanenti[0]
    opzioni_valide = [opt for opt in opzioni if check_proficiency(opt, context.user_data['competenze'])]

    if not opzioni_valide:
        await update.message.reply_text("Ops, non ci sono opzioni di equipaggiamento valide per la tua classe. Passiamo alla prossima scelta.")
        opzioni_rimanenti.pop(0)
        return await chiedi_equipaggiamento(update, context)

    reply_keyboard = [opzioni_valide[i:i + 2] for i in range(0, len(opzioni_valide), 2)]

    await update.message.reply_text(
        f"Scegli l'equipaggiamento per la tua classe:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SCEGLI_EQUIPAGGIAMENTO

async def gestisci_scelta_equipaggiamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text
    opzioni_rimanenti = context.user_data.get('opzioni_equip_rimanenti')

    if not opzioni_rimanenti or user_choice not in opzioni_rimanenti[0]:
        await update.message.reply_text("Scelta non valida. Per favore, scegli un'opzione dalla tastiera.")
        return SCEGLI_EQUIPAGGIAMENTO

    context.user_data['equipaggiamento_scelto'].append(user_choice)
    opzioni_rimanenti.pop(0)

    return await chiedi_equipaggiamento(update, context)

async def chiedi_livello(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    context.user_data['livelli_bonus_da_applicare'] = get_asi_levels(context.user_data['classe'], livello)

    return await gestisci_bonus(update, context)

async def gestisci_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    livelli_bonus = context.user_data['livelli_bonus_da_applicare']
    if not livelli_bonus:
        # Dopo ASI/Talenti, controlla se la classe ha magia
        if context.user_data['classe'] in incantatori and context.user_data['livello'] >= 1:
            return await gestisci_magie_e_trucchetti(update, context)
        else:
            return await chiedi_lingue(update, context)

    livello_corrente_bonus = livelli_bonus.pop(0)
    context.user_data['livello_corrente_bonus'] = livello_corrente_bonus

    reply_keyboard = [['2 punti nelle statistiche', '1 talento']]
    await update.message.reply_text(
        f"Al livello {livello_corrente_bonus}, hai una scelta da fare.\n"
        "Vuoi usare 2 punti nelle statistiche o scegliere un talento?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SCEGLI_BONUS

async def scegli_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == '2 punti nelle statistiche':
        context.user_data['punti_asi_da_distribuire'] = 2
        return await applica_asi_step(update, context)
    elif choice == '1 talento':
        context.user_data['talenti_da_scegliere'] = 1
        return await scegli_talento_step(update, context)
    else:
        await update.message.reply_text("Scelta non valida. Riprova.")
        context.user_data['livelli_bonus_da_applicare'].insert(0, context.user_data['livello_corrente_bonus'])
        return SCEGLI_BONUS

async def applica_asi_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats_list = [['Forza', 'Destrezza', 'Costituzione'], ['Intelligenza', 'Saggezza', 'Carisma']]
    await update.message.reply_text(
        f"Perfetto! Scegli la statistica da aumentare di 1 punto. Ti rimangono {context.user_data['punti_asi_da_distribuire']} punti.",
        reply_markup=ReplyKeyboardMarkup(stats_list, one_time_keyboard=True)
    )
    return APPLICA_ASI

async def applica_asi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stat_choice = update.message.text
    if stat_choice not in context.user_data['stats']:
        await update.message.reply_text("Scelta non valida. Riprova.")
        return APPLICA_ASI

    context.user_data['stats'][stat_choice] += 1
    context.user_data['punti_asi_da_distribuire'] -= 1

    if context.user_data['punti_asi_da_distribuire'] > 0:
        return await applica_asi_step(update, context)

    return await gestisci_bonus(update, context)

async def scegli_talento_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    classe = context.user_data['classe']
    talenti_disponibili_per_classe = talenti_per_classe.get(classe, [])
    reply_keyboard = [talenti_disponibili_per_classe[i:i + 2] for i in range(0, len(talenti_disponibili_per_classe), 2)]

    await update.message.reply_text(
        f"Scegli un talento dalla lista. Ti rimangono {context.user_data['talenti_da_scegliere']} talenti da scegliere.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SCEGLI_TALENTO

async def scegli_talento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feat_choice = update.message.text
    classe = context.user_data['classe']
    if feat_choice not in talenti_per_classe.get(classe, []):
        await update.message.reply_text("Talento non valido. Riprova.")
        return SCEGLI_TALENTO

    context.user_data['talenti'].append(feat_choice)
    context.user_data['talenti_da_scegliere'] -= 1

    if context.user_data['talenti_da_scegliere'] > 0:
        return await scegli_talento_step(update, context)

    return await gestisci_bonus(update, context)

async def gestisci_magie_e_trucchetti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    classe = context.user_data['classe']
    opzioni_magia = magie_iniziali.get(classe, {})

    # Gestione Trucchetti
    if opzioni_magia.get('trucchetti', 0) > 0 and not context.user_data.get('trucchetti_finiti', False):
        context.user_data['numero_trucchetti_da_scegliere'] = opzioni_magia['trucchetti']
        context.user_data['lista_trucchetti_da_scegliere'] = trucchetti_disponibili.get(classe, [])
        return await scegli_trucchetto(update, context)

    # Gestione Incantesimi
    if opzioni_magia.get('incantesimi', 0) > 0 and not context.user_data.get('incantesimi_finiti', False):
        context.user_data['numero_incantesimi_da_scegliere'] = opzioni_magia['incantesimi']
        context.user_data['lista_incantesimi_da_scegliere'] = incantesimi_disponibili.get(classe, [])
        return await scegli_incantesimo(update, context)

    # Se non ha più magie da scegliere, passa alle lingue
    return await chiedi_lingue(update, context)


async def scegli_trucchetto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lista_trucchetti = context.user_data['lista_trucchetti_da_scegliere']
    reply_keyboard = [lista_trucchetti[i:i + 2] for i in range(0, len(lista_trucchetti), 2)]

    await update.message.reply_text(
        f"Scegli un trucchetto. Ti rimangono {context.user_data['numero_trucchetti_da_scegliere']} da scegliere.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SCEGLI_TRUCCHETTI_E_INCANTESIMI

async def scegli_incantesimo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lista_incantesimi = context.user_data['lista_incantesimi_da_scegliere']
    reply_keyboard = [lista_incantesimi[i:i + 2] for i in range(0, len(lista_incantesimi), 2)]

    await update.message.reply_text(
        f"Scegli un incantesimo. Ti rimangono {context.user_data['numero_incantesimi_da_scegliere']} da scegliere.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SCEGLI_TRUCCHETTI_E_INCANTESIMI

async def gestisci_scelta_magia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text
    
    # Check if a trucchetto is being selected
    if context.user_data.get('numero_trucchetti_da_scegliere', 0) > 0:
        if user_choice not in context.user_data['lista_trucchetti_da_scegliere']:
            await update.message.reply_text("Scelta non valida. Riprova.")
            return await scegli_trucchetto(update, context)

        context.user_data['trucchetti_scelti'].append(user_choice)
        context.user_data['numero_trucchetti_da_scegliere'] -= 1
        context.user_data['lista_trucchetti_da_scegliere'].remove(user_choice)

        if context.user_data['numero_trucchetti_da_scegliere'] > 0:
            return await scegli_trucchetto(update, context)
        else:
            context.user_data['trucchetti_finiti'] = True
            return await gestisci_magie_e_trucchetti(update, context)

    # Check if a spell is being selected
    if context.user_data.get('numero_incantesimi_da_scegliere', 0) > 0:
        if user_choice not in context.user_data['lista_incantesimi_da_scegliere']:
            await update.message.reply_text("Scelta non valida. Riprova.")
            return await scegli_incantesimo(update, context)

        context.user_data['incantesimi_scelti'].append(user_choice)
        context.user_data['numero_incantesimi_da_scegliere'] -= 1
        context.user_data['lista_incantesimi_da_scegliere'].remove(user_choice)

        if context.user_data['numero_incantesimi_da_scegliere'] > 0:
            return await scegli_incantesimo(update, context)
        else:
            context.user_data['incantesimi_finiti'] = True
            return await gestisci_magie_e_trucchetti(update, context)

    # Should not be reached
    await update.message.reply_text("Errore nella selezione della magia. Riproviamo da capo.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def chiedi_lingue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['lingue_da_scegliere'] = 1
    lingue_disponibili = [l for l in lingue_conoscibili['standard'] + lingue_conoscibili['esotiche'] if l not in context.user_data['lingue']]
    reply_keyboard = [lingue_disponibili[i:i + 3] for i in range(0, len(lingue_disponibili), 3)]

    await update.message.reply_text(
        f"Scegli una lingua extra per il tuo personaggio (il Comune è automatico):",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SCEGLI_LINGUE

async def gestisci_lingue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lingua_scelta = update.message.text
    lingue_disponibili_tutte = lingue_conoscibili['standard'] + lingue_conoscibili['esotiche']
    
    if lingua_scelta not in lingue_disponibili_tutte or lingua_scelta in context.user_data['lingue']:
        await update.message.reply_text("Lingua non valida o già scelta. Per favore, scegli una lingua dalla lista.")
        return SCEGLI_LINGUE

    context.user_data['lingue'].append(lingua_scelta)
    context.user_data['lingue_da_scegliere'] -= 1
    
    # Non essendoci più lingue da scegliere, passiamo alla finalizzazione.
    return await finalize_character(update, context)


async def finalize_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats_final = context.user_data['stats']
    talenti_final = ", ".join(context.user_data['talenti']) if context.user_data['talenti'] else "Nessuno"
    equip_scelto = ", ".join(context.user_data['equipaggiamento_scelto']) if context.user_data['equipaggiamento_scelto'] else "Nessuno"
    equip_fisso = ", ".join(context.user_data['equipaggiamento_fisso']) if context.user_data['equipaggiamento_fisso'] else "Nessuno"
    competenze_final = ", ".join(context.user_data['competenze']) if context.user_data['competenze'] else "Nessuna"
    lingue_final = ", ".join(context.user_data['lingue']) if context.user_data['lingue'] else "Nessuna"
    trucchetti_final = ", ".join(context.user_data['trucchetti_scelti']) if context.user_data['trucchetti_scelti'] else "Nessuno"
    incantesimi_final = ", ".join(context.user_data['incantesimi_scelti']) if context.user_data['incantesimi_scelti'] else "Nessuno"


    message = (
        "<b>Personaggio generato! ✨</b>\n\n"
        f"<b>Nome:</b> {context.user_data['nome']}\n"
        f"<b>Razza:</b> {context.user_data['razza']}\n"
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
        f"<b>Equipaggiamento:</b>\n"
        f"  - Scelte: {equip_scelto}\n"
        f"  - Fisso: {equip_fisso}\n\n"
        f"<b>Competenze:</b>\n"
        f"{competenze_final}\n\n"
        f"<b>Lingue:</b>\n"
        f"{lingue_final}\n\n"
        f"<b>Talenti:</b> {talenti_final}\n\n"
        f"<b>Magie:</b>\n"
        f"  - Trucchetti: {trucchetti_final}\n"
        f"  - Incantesimi: {incantesimi_final}"
    )

    await update.message.reply_html(message, reply_markup=ReplyKeyboardRemove())

    if context.user_data.get('num_rimanenti', 0) > 0:
        return await inizia_creazione_personaggio(update, context)

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Creazione personaggio annullata.', reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def main():
    if TELEGRAM_TOKEN == "YOUR_TOKEN_HERE":
        print("Errore: il token Telegram non è stato impostato. Per favore, sostituisci 'YOUR_TOKEN_HERE' con il tuo token o imposta la variabile d'ambiente TELEGRAM_TOKEN.")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("crea", start)],
        states={
            QUANTI_PERSONAGGI: [MessageHandler(filters.TEXT & ~filters.COMMAND, quanti_personaggi)],
            INSERISCI_NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, inserisci_nome)],
            SCEGLI_RAZZA: [MessageHandler(filters.TEXT & ~filters.COMMAND, scegli_razza)],
            ASSEGNA_STAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, assegna_stat)],
            SCEGLI_CLASSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, classe_scelta)],
            SCEGLI_SOTTOCLASSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sottoclasse_scelta)],
            SCEGLI_EQUIPAGGIAMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, gestisci_scelta_equipaggiamento)],
            SCEGLI_LIVELLO: [MessageHandler(filters.TEXT & ~filters.COMMAND, livello_scelto)],
            SCEGLI_BONUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, scegli_bonus)],
            APPLICA_ASI: [MessageHandler(filters.TEXT & ~filters.COMMAND, applica_asi)],
            SCEGLI_TALENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, scegli_talento)],
            SCEGLI_TRUCCHETTI_E_INCANTESIMI: [MessageHandler(filters.TEXT & ~filters.COMMAND, gestisci_scelta_magia)],
            SCEGLI_LINGUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, gestisci_lingue)],
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)],
    )

    app.add_handler(conv_handler)
    print("Bot avviato... premi Ctrl+C per fermarlo.")
    app.run_polling(poll_interval=2.0)

if __name__ == "__main__":
    main()
