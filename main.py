import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta

TELEGRAM_API_TOKEN = "8193746104:AAHsdMqrC-CO0ZGe0hnj18mgTcuTcxrH0-I"

async def search_ace_stream(query):
    """search-ace.stream'den maç araması yapar"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        url = f"https://search-ace.stream/?q={query}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for elem in soup.find_all('a', href=True):
            href = elem['href']
            if "acestream://" in href:
                title = elem.get_text(strip=True) or query
                links.append((href, title))
        return links
    except Exception as e:
        print(f"search-ace.stream hatası: {str(e)}")
        return []

async def acestream(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sources = [
        "https://soccer9.sportshub.stream/",
        "https://acestream.me/",
        "https://www.acestream.live/"
    ]
    try:
        now_tr = datetime.now(tz=None)  # Türkiye saati (UTC+3)
        events = []
        live_matches = []  # search-ace.stream için maç isimleri

        # Web kaynaklarından veri çek
        for url in sources:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                event_elements = soup.find_all('a', href=True)
                for elem in event_elements:
                    href = elem['href']
                    title = elem.get_text(strip=True) or None
                    
                    if "sportshub.stream/event" in href and "live" in (title.lower() if title else ""):
                        events.append((href, title))
                        if title:
                            # Canlı maç isimlerini al, search-ace.stream'de aratmak için
                            teams = title.replace("live", "").strip().split(" – ")
                            if len(teams) >= 1:
                                live_matches.append(teams[0])  # İlk takımı al
                    elif "acestream.me" in url and "acestream://" in href:
                        events.append((href, title))
                    elif "acestream.live" in url and "acestream://" in href:
                        events.append((href, title))
            except Exception as e:
                print(f"{url} için hata: {str(e)}")
                continue

        # search-ace.stream'den canlı maçlar için arama yap
        for match in live_matches[:5]:  # İlk 5 maçla sınırlı, performansı korumak için
            search_results = await search_ace_stream(match)
            events.extend(search_results)

        if not events:
            await update.message.reply_text("Şu anda canlı maç bulunamadı.")
            return

        seen_titles = set()
        message = "Canlı Maçlar ve AceStream Linkleri:\n"
        found_links = False
        for event_url, event_title in events:
            if not event_title:  # Başlık boşsa detaydan al
                try:
                    full_url = event_url if event_url.startswith("http") else f"https://{event_url.split('/')[0]}{event_url}"
                    event_response = requests.get(full_url, timeout=10)
                    event_soup = BeautifulSoup(event_response.text, 'html.parser')
                    event_title = event_soup.find('title').text.strip() if event_soup.find('title') else "Maç"
                except:
                    event_title = "Maç"

            normalized_title = event_title.lower().replace("live", "").replace("now", "").replace("playing", "").replace(" ", "")
            if normalized_title in seen_titles:
                continue
            seen_titles.add(normalized_title)

            acestream_links = []
            if "sportshub.stream/event" in event_url:
                try:
                    full_url = event_url if event_url.startswith("http") else f"https://sportshub.stream{event_url}"
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
