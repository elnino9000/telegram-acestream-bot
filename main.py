import aiohttp
import asyncio
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TELEGRAM_API_TOKEN = "8193746104:AAHsdMqrC-CO0ZGe0hnj18mgTcuTcxrH0-I"

# Yeni kaynaklar
SOURCES = [
    "https://www.stream2watch.ws/",
    "https://www.vipbox.tv/",
    "https://www.cricfree.sc/",
    "https://soccerstreams100.com/"
]

# Asenkron istekler ile veri çekme ve AceStream linklerini bulma
async def fetch_acestream_links(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                page = await response.text()
                soup = BeautifulSoup(page, 'html.parser')
                event_elements = soup.find_all('a', href=True)

                links = []
                for elem in event_elements:
                    href = elem['href']
                    title = elem.get_text(strip=True) or None
                    
                    # Eğer AceStream linki varsa
                    if "acestream://" in href:
                        if not title:  # Başlık boşsa, sayfa başlığını al
                            try:
                                title = soup.find('title').get_text(strip=True)
                            except:
                                title = "Maç"
                        links.append((href, title))
                
                return links
            else:
                return []
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return []

# Telegram komutu için main fonksiyon
async def acestream(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_acestream_links(session, url) for url in SOURCES]
        all_events = await asyncio.gather(*tasks)
        
        events = [event for sublist in all_events for event in sublist]
        
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

            if event_url:
                message += f"\n{event_title}:\n" + event_url + "\n"
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

# Ana fonksiyon
def main() -> None:
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()
    application.add_handler(CommandHandler("acestream", acestream))
    print("Bot çalışıyor...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
