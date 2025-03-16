import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_API_TOKEN = "8193746104:AAHsdMqrC-CO0ZGe0hnj18mgTcuTcxrH0-I"

async def acestream(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sources = [
        "https://soccer9.sportshub.stream/",  # İlk kaynak
        "https://acestreamid.com/"           # İkinci kaynak
    ]
    try:
        events = []
        for url in sources:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            event_elements = soup.find_all('a', href=True)
            for elem in event_elements:
                href = elem['href']
                title = elem.get_text(strip=True) or "Bilinmeyen Maç"
                # İlk site için "sportshub.stream/event", ikinci site için "acestream://" kontrolü
                if ("sportshub.stream/event" in href and "live" in title.lower()) or ("acestream://" in href):
                    events.append((href, title))

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

            acestream_links = []
            if "sportshub.stream/event" in event_url:
                try:
                    full_url = f"https://sportshub.stream{event_url}" if not event_url.startswith("http") else event_url
                    event_response = requests.get(full_url, timeout=10)
                    event_soup = BeautifulSoup(event_response.text, 'html.parser')
                    for link in event_soup.find_all('a', href=True):
                        if "acestream://" in link['href']:
                            acestream_links.append(link['href'])
                except Exception as e:
                    print(f"{event_title} için hata: {str(e)}")
            elif "acestream://" in event_url:
                acestream_links.append(event_url)

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

        print(f"Bot çalışıyor: {len(events)} canlı etkinlik tarandı (Kaynaklar: {', '.join(sources)}).")
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
