import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Telegram bot token'ını buraya yaz (Glitch'teki token'ı kullan)
TELEGRAM_API_TOKEN = "your_bot_token_here"  # Buraya kendi token'ını koy

# /acestream komutu için fonksiyon
async def acestream(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """AceStream linklerini scrape et ve gönder."""
    url = "https://soccer9.sportshub.stream/"  # Örnek URL, senin scrap ettiğin siteyi kullan
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Örnek: Maç listesini bul (senin koduna göre düzenle)
        events = soup.find_all('div', class_='event')  # Bu kısmı senin scraping mantığına göre değiştir
        if not events:
            await update.message.reply_text("Şu anda canlı etkinlik bulunamadı.")
            return

        message = "Canlı Maçlar:\n"
        for event in events[:5]:  # İlk 5 maçı göster
            title = event.get_text(strip=True)  # Örnek, senin mantığına göre uyarla
            message += f"- {title}\n"
        
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Bir hata oluştu: {str(e)}")

# Ana fonksiyon
def main() -> None:
    """Botu başlat."""
    # Application oluştur
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Komut handler'ını ekle
    application.add_handler(CommandHandler("acestream", acestream))

    # Botu çalıştır
    print("Bot çalışıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
