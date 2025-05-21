import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from source.controller.controller import Controller
from source.model.PDFgenEN import PDFGenerator  # tua logica


BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Logging
logging.basicConfig(level=logging.INFO)

# Messaggio di benvenuto
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "🎥 Benvenuto!\n\n"
        "Questo bot analizza i tuoi video. "
        "Per iniziare, invia un video come file (non come messaggio video breve).\n\n"
        "📩 Dopo l'elaborazione riceverai un risultato."
    )
    await update.message.reply_text(welcome_msg)

# Gestione del video

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_file = update.message.video or update.message.document
    if not video_file:
        await update.message.reply_text("⚠️ Per favore invia un video come file.")
        return

    file = await context.bot.get_file(video_file.file_id)
    file_path = f"temp/{video_file.file_id}.mp4"
    os.makedirs("temp", exist_ok=True)
    await file.download_to_drive(file_path)

    await update.message.reply_text("⏳ Analizzando il video...")

    try:
        # Chiama la tua applicazione qui
        #result = process_video(file_path)
        [result, percentual] = Controller.onAnalize(file_path, 'name', 'surname', 'weight', 'height', 'birth', 'position', 'hand')

        await update.message.reply_text(f"✅ Analisi completata:\n\n{result}")
        output_path = "scheda_giocatore.pdf"
        background_image = "static/images/background.png"

        

        generator = PDFGenerator(output_path, background_image)
        frasi=generator.raggruppa_frasi_per_fase(result)
        generator.crea_pdf(
            nome = 'nome',
            cognome = 'cognome',
            data_nascita = 'dob',
            posizione = 'ruolo',
            mano_dominante = 'mano_dominante',
            frasi_per_fase=frasi
        )
        # Invia il PDF
        with open(output_path, 'rb') as pdf_file:
            await update.message.reply_document(pdf_file, filename="report.pdf")

    except Exception as e:
        await update.message.reply_text(f"❌ Errore: {str(e)}")

    finally:
        # Pulizia
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(output_path):
            os.remove(output_path)

# Avvio bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

    print("Bot avviato.")
    app.run_polling()

if __name__ == "__main__":
    main()
