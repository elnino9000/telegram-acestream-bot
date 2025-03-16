import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Telegram bot token'ı (senin token'ın)
TELEGRAM_API_TOKEN = "8193746104:AAHsdMqrC-CO0ZGe0hnj18mgTcuTcxrH0-I"

# /acestream komutu için fonksiyon
async def acestream(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """AceStream linklerini scrape et ve gönder."""
    url = "https://soccer9.sportshub.stream/"  # Senin kullandığın ana URL
    try:
        # Siteye bağlan
        response = requests.get(url)
        response.raise_for_status()  # Hata varsa yakala
        soup = BeautifulSoup(response.text, 'html.parser')

        # Maç listesini bul (loglara göre uyarladım)
        events = []
        event_elements = soup.find_all('a', href=True)  # Maç linklerini bul
        for elem in event_elements:
            href = elem['href']
            if "sportshub.stream/event" in href:
                title = elem.get_text(strip=True) or "Bilinmeyen Maç"
                events.append((href, title))

        if not events:
            await update.message.reply_text("Şu anda canlı etkinlik bulunamadı.")
            return

        # İlk 5 maçı al, detaylı scraping yap
        message = "Canlı Maçlar ve AceStream Linkleri:\n"
        for event_url, event_title in events[:5]:
            try:
                # Her maçın detay sayfasına git
                full_url = f"https://sportshub.stream{event_url}" if not event_url.startswith("http") else event_url
                event_response = requests.get(full_url)
                event_soup = BeautifulSoup(event_response.text, 'html.parser')

                # AceStream linklerini bul
                acestream_links = []
                for link in event_soup.find_all('a', href=True):
                    if "acestream://" in link['href']:
                        acestream_links.append(link['href'])

                if acestream_links:
                    message += f"\n{event_title}:\n" + "\n".join(acestream_links[:3]) + "\n"  # İlk 3 link
                else:
                    message += f"\n{event_title}: AceStream linki bulunamadı.\n"
            except Exception as e:
                message += f"\n{event_title}: Hata: {str(e)}\n"

        # Mesajı gönder (Telegram limiti 4096 karakter)
        await update.message.reply_text(message[:4096])
        print(f"Bot çalışıyor: {len(events)} etkinlik bulundu, mesaj gönderildi.")
    except Exception as e:
        await update.message.reply_text(f"Bir hata oluştu: {str(e)}")
        print(f"Bot hatası: {str(e)}")

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
