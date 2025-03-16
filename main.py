# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
from bs4 import BeautifulSoup
import re
import time

TELEGRAM_API_TOKEN = "8193746104:AAHsdMqrC-CO0ZGe0hnj18mgTcuTcxrH0-I"

def get_live_events():
    url = "https://soccer9.sportshub.stream/"
    try:
        print("Siteye bağlanılıyor:", url)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        events = []
        links = soup.find_all("a")
        print("Link sayısı:", len(links))
        for link in links:
            href = link.get("href") or ""
            if "sportshub.stream/event" in href and href not in events:
                parent_text = link.parent.text if link.parent else ""
                if any(keyword in parent_text.upper() for keyword in ["LIVE", "CANLI", "NOW"]):
                    match_name = parent_text.split("LIVE")[0].strip().upper()
                    events.append((href, match_name))
        print("Bulunan canlı etkinlikler:", events)
        return events
    except Exception as e:
        print("Hata (get_live_events):", str(e))
        return []

def scrape_event(event_data):
    event_url, match_name = event_data
    try:
        print("Event sayfasına bağlanılıyor:", event_url)
        response = requests.get(event_url)
        response.raise_for_status()
        page_source = response.text
        codes = re.findall(r"acestream://[a-f0-9]{40}", page_source)
        print("Bulunan AceStream kodları:", codes)
        if codes:
            return (event_url, match_name, list(set(codes)))
        return (event_url, match_name, [])
    except Exception as e:
        print("Hata (scrape_event):", str(e))
        return (event_url, match_name, [])

def start(update, context):
    update.message.reply_text('Merhaba! Canlı maçları ve AceStream linklerini almak için /acestream komutunu kullanabilirsin.')

def send_acestream_links(update, context):
    print("send_acestream_links çalıştı")
    events = get_live_events()
    print("Events:", events)
    
    if not events:
        update.message.reply_text("Şu an canlı maç bulunmamaktadır.")
        return
    
    message = "Canlı maçlar ve AceStream linkleri:\n"
    total_acestream_count = 0
    matches_with_links = []
    
    # Tüm etkinlikleri tara ve sadece AceStream linki olanları al
    for event in events:
        event_url, match_name = event
        print("Scraping:", event_url)
        _, _, codes = scrape_event((event_url, match_name))
        if codes:  # Sadece link varsa ekle
            matches_with_links.append((event_url, match_name, codes))
            total_acestream_count += len(codes)
    
    # Eğer hiç AceStream linki yoksa
    if not matches_with_links:
        update.message.reply_text("Şu anda AceStream linki bulunan maç yok.")
        return
    
    # Mesajı oluştur
    message += f"Tarama sonucu: {len(matches_with_links)} maçta toplam {total_acestream_count} AceStream linki bulundu.\n"
    for event_url, match_name, codes in matches_with_links:
        event_message = f"\nMaç: {match_name}\nURL: {event_url}\nAceStream Linkleri:\n"
        for code in codes:
            event_message += f"  - {code}\n"
        
        # Mesaj 4000 karakteri aşarsa, mevcut mesajı gönder ve yeni bir tane başlat
        if len(message) + len(event_message) > 4000:
            update.message.reply_text(message)
            message = "Canlı maçlar ve AceStream linkleri (devam):\n"
        message += event_message
    
    # Kalan mesajı gönder
    if message.strip():
        update.message.reply_text(message)

def main():
    updater = Updater(TELEGRAM_API_TOKEN)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('acestream', send_acestream_links))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()