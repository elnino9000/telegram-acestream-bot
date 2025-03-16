import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Telegram bot token'ı
TELEGRAM_API_TOKEN = "8193746104:AAHsdMqrC-CO0ZGe0hnj18mgTcuTcxrH0-I"

# /acestream komutu için fonksiyon
async def acestream(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """AceStream linklerini scrape et ve sadece link olanları gönder."""
    url = "https://soccer9.sportshub.stream/"
    try:
        # Siteye bağlan
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tüm maçları bul
        events = []
        event_elements = soup.find_all('a', href=True)
        for elem in event_elements:
            href = elem['href']
            if "sportshub.stream/event" in href:
                title = elem.get_text(strip=True) or "Bilinmeyen Maç"
                events.append((href, title))

        if not events:
            await update.message.reply_text("Şu anda canlı etkinlik bulunamadı.")
            return

        # Sadece AceStream linki olan maçları ekle
        message = "Canlı Maçlar ve AceStream Linkleri:\n"
        found_links = False
        for event_url, event_title in events:  # Tüm maçlar, limit yok
            try:
                full_url = f"https://sportshub.stream{event_url}" if not event_url.startswith("http") else event_url
                event_response = requests.get(full_url)
                event_soup = BeautifulSoup(event_response.text, 'html.parser')

                acestream_links = []
                for link in event_soup.find_all('a', href=True):
                    if "acestream://" in link['href']:
                        acestream_links.append(link['href'])

                # Sadece link varsa mesaj’a ekle
                if acestream_links:
                    message += f"\n{event_title}:\n" + "\n".join(acestream_links[:3]) + "\n"
                    found_links = True

            except Exception as e:
                print(f"{event_title} için hata: {str(e)}")  # Hataları log’a yaz, Telegram’a yazma

        # Mesajı 4000 karakterlik parçalara böl ve gönder
        if not found_links:
            await update.message.reply_text("Şu anda AceStream linki olan maç bulunamadı.")
        else:
            max_length = 4000
            if len(message) > max_length:
                parts = [message[i:i + max_length] for i in range(0, len(message), max_length)]
                for part in parts:
                    await update.message.reply_text(part)
            else:
                await update.message.reply_text(message)

        print(f"Bot çalışıyor: {len(events)} etkinlik tarandı, AceStream linki olanlar gönderildi.")
    except Exception as e:
        await update.message.reply_text(f"Bir hata oluştu: {str(e)}")
        print(f"Bot hatası: {str(e)}")

# Ana fonksiyon
def main() -> None:
    """Botu başlat."""
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()
    application.add_handler(CommandHandler("acestream", acestream))
    print("Bot çalışıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
