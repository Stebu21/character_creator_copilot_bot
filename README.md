# 🧙‍♂️ D&D Character Creator Bot

Un bot Telegram interattivo per creare rapidamente personaggi di Dungeons & Dragons, completo di statistiche generate, scelta di classe, sottoclasse, livello e gestione di talenti e bonus statistici (ASI).

## ✨ Caratteristiche Principali

* **Creazione Multipla**: Crea fino a 10 personaggi con un'unica sessione.
* **Gestione Livelli**: Gestisce le scelte di bonus per le statistiche e i talenti per i personaggi di livello 4, 8, e superiori.
* **Distribuzione Punti**: Permette di distribuire i punti bonus per le statistiche su più attributi, non solo uno.
* **Generazione Statistiche**: Genera automaticamente le sei statistiche del personaggio con il metodo "4d6 drop lowest".

---

## 🛠️ Installazione

Segui questi passaggi per avviare il bot in locale.

**Prerequisiti**
* **Python 3.8+**: Assicurati di avere una versione recente di Python installata.
* **Token Telegram**: Avrai bisogno di un token di un bot Telegram. Puoi ottenerne uno da BotFather su Telegram.

**Passaggi**
1.  Clona il repository:
    ```bash
    git clone [https://github.com/Stebu21/character_creator_copilot_bot.git](https://github.com/Stebu21/character_creator_copilot_bot.git)
    ```
2.  Spostati nella directory del progetto:
    ```bash
    cd character_creator_copilot_bot
    ```
3.  Installa le dipendenze richieste:
    ```bash
    pip install python-telegram-bot
    ```
4.  Configura il tuo token di Telegram come variabile d'ambiente. Questo è il metodo più sicuro per gestire le credenziali.

    **Su macOS / Linux:**
    ```bash
    export TELEGRAM_TOKEN="IL_TUO_TOKEN_QUI"
    ```

    **Su Windows (Command Prompt):**
    ```bash
    set TELEGRAM_TOKEN="IL_TUO_TOKEN_QUI"
    ```

5.  Avvia il bot:
    ```bash
    python character_creator_copilot_bot.py
    ```

---

## 🚀 Utilizzo

Dopo aver avviato il bot, cerca il tuo bot su Telegram e inizia una conversazione.

* Invia il comando `/crea` per iniziare la creazione di un nuovo personaggio.
* Segui le istruzioni per scegliere la classe, la sottoclasse, il livello e i bonus.
* In qualsiasi momento, puoi inviare `/cancel` per annullare la creazione.

---

## 🤝 Contribuire

I contributi sono sempre i benvenuti! Se vuoi migliorare il bot, sentiti libero di aprire una **issue** per segnalare un bug o proporre una nuova funzionalità, oppure apri una **pull request** con le tue modifiche.

---

## 📄 Licenza

Questo progetto è distribuito sotto licenza [Nome Licenza (es. MIT, GPLv3)]. Vedi il file `LICENSE` per i dettagli.

---

## 📧 Contatti

* **GitHub**: [@Stebu21](https://github.com/Stebu21)
