import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_API_TOKEN = "8193746104:AAHsdMqrC-CO0ZGe0hnj18mgTcuTcxrH0-I"

async def acestream(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sources = [
        "https://acestream.me/",
        "https://www.acestream.live/",
        "https://acestream.online/",
        "https://www.livefootball.ws/acestream.html"
    ]
    try:
        events = []
        
        # Her kaynaktan veri çek
        for url in sources:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                event_elements = soup.find_all('a', href=True)
                source_links = 0
                for elem in event_elements:
                    href = elem['href']
                    title = elem.get_text(strip=True) or None
                    
                    if "acestream://" in href:
                        if not title:  # Başlık boşsa detaydan al
                            try:
                                event_response = requests.get(url, timeout=10)
                                event_soup = BeautifulSoup(event_response.text, 'html.parser')
                                title_tag = event_soup.find('title') or event_soup.find('h1')
                                title = title_tag.text.strip() if title_tag else "Maç"
                            except:
                                title = "Maç"
                        events.append((href, title))
                        source_links += 1
                print(f"{url}: {source_links} etkinlik bulundu.")
            except Exception as e:
                print(f"{url} için hata: {str(e)}")
                continue

        if not events:
            await update.message.reply_text("Şu anda canlı maç bulunamadı.")
            return

        seen_titles = set()
        message = "Canlı Maçlar ve AceStream Linkleri:\n"
        found_links = False
        for event_url, event_title in events:
            normalized_title = event_title.lower().replace("live", "").replace("now", "").replace("playing", "").replace(" ", "")
            if normalized_title in seen_titles:
                continue
            seen_titles.add(normalized_title)

            acestream_links = [event_url]  # Doğrudan AceStream linki

            if acestream_links:
                message += f"\n{event_title}:\n" + "\n".join(acestream_links) + "\n"
                found_links = True

        if not found_links:
            await update.message.reply_text("Şu anda AceStream linki olan canlı maç bulunamadı.")
        else:
            max_length = 4000
            if len(message) > max_length:
                parts = [message[i:i + max_length] for i in range(0, len(message), max_length)]
                for part in parts:
                    await update.message.reply_text(part)
            else:
                await update.message.reply_text(message)

        print(f"Bot çalışıyor: {len(events)} canlı etkinlik tarandı.")
    except Exception as e:
        await update.message.reply_text(f"Bir hata oluştu: {str(e)}")
        print(f"Bot hatası: {str(e)}")

def main() -> None:
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()
    application.add_handler(CommandHandler("acestream", acestream))
    print("Bot çalışıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
