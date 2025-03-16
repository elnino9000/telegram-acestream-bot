import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_API_TOKEN = "8193746104:AAHsdMqrC-CO0ZGe0hnj18mgTcuTcxrH0-I"

async def acestream(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = "https://soccer9.sportshub.stream/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

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

        # Tekrarları önlemek için set kullanıyoruz
        seen_titles = set()
        message = "Canlı Maçlar ve AceStream Linkleri:\n"
        found_links = False
        for event_url, event_title in events:
            if event_title in seen_titles:
                continue  # Tekrar eden maçı atla
            seen_titles.add(event_title)
            try:
                full_url = f"https://sportshub.stream{event_url}" if not event_url.startswith("http") else event_url
                event_response = requests.get(full_url)
                event_soup = BeautifulSoup(event_response.text, 'html.parser')

                acestream_links = []
                for link in event_soup.find_all('a', href=True):
                    if "acestream://" in link['href']:
                        acestream_links.append(link['href'])

                if acestream_links:
                    message += f"\n{event_title}:\n" + "\n".join(acestream_links[:3]) + "\n"
                    found_links = True

            except Exception as e:
                print(f"{event_title} için hata: {str(e)}")

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

def main() -> None:
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()
    application.add_handler(CommandHandler("acestream", acestream))
    print("Bot çalışıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
