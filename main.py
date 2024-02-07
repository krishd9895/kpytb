import telebot
from pytube import YouTube, Playlist
from telebot import types
import os

telegram_token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(telegram_token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome to the Utube DL bot!\n Try /help")


@bot.message_handler(commands=['help'])
def help(message):
    help_text = "This bot allows you to download YouTube videos, Audios and playlists.\n\n" \
                "Usage:\n" \
                "1. Send a single video URL to download that video.\n" \
                "2. Send a playlist URL to download all videos in the playlist.\n\n"
            
    bot.reply_to(message, help_text)


@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    download_links = get_direct_download_links(url)

    if download_links:
        response_text = "Here are the download links:"
        sent_message = bot.send_message(message.chat.id, response_text)

        for link in download_links:
            title = link['title']
            buttons = []

            if 'video' in link:
                video_button = types.InlineKeyboardButton(text='Download Video📽️', url=link['video'])
                buttons.append(video_button)

            if 'audio' in link:
                audio_button = types.InlineKeyboardButton(text='Download Audio📣', url=link['audio'])
                buttons.append(audio_button)

            if buttons:
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(*buttons)
                bot.send_message(message.chat.id, title, reply_markup=markup)
            else:
                bot.send_message(message.chat.id, title)
    else:
        bot.reply_to(message, "Sorry, unable to retrieve download links for the provided URL.")


def get_direct_download_links(url):
    try:
        download_links = []

        if 'playlist' in url:
            # If the URL contains 'playlist', treat it as a playlist URL
            playlist = Playlist(url)
            video_urls = playlist.video_urls

            for video_url in video_urls:
                yt = YouTube(video_url)

                # Retrieve the highest quality video with audio
                video_stream = yt.streams.get_highest_resolution()
                audio_stream = yt.streams.get_audio_only()
                download_links.append({
                    'title': yt.title,
                    'video': video_stream.url,
                    'audio': audio_stream.url
                })

                # Retrieve the 360p video with audio
                video_360p = yt.streams.filter(res="360p").first()
                if video_360p:
                    download_links.append({
                        'title': yt.title + ' (360p)',
                        'video': video_360p.url,
                    })

                # Retrieve the low-quality audio track separately
                audio_only_stream = yt.streams.filter(only_audio=True).last()
                if audio_only_stream:
                    download_links.append({
                        'title': yt.title + ' (Low Quality Audio)',
                        'audio': audio_only_stream.url
                    })
        else:
            # Treat it as a single video URL
            yt = YouTube(url)

            # Retrieve the highest quality video with audio
            video_stream = yt.streams.get_highest_resolution()
            audio_stream = yt.streams.get_audio_only()
            download_links.append({
                'title': yt.title,
                'video': video_stream.url,
                'audio': audio_stream.url
            })

            # Retrieve the 360p video with audio
            video_360p = yt.streams.filter(res="360p").first()
            if video_360p:
                download_links.append({
                    'title': yt.title + ' (360p)',
                    'video': video_360p.url,
                })

            # Retrieve the low-quality audio track separately
            audio_only_stream = yt.streams.filter(only_audio=True).last()
            if audio_only_stream:
                download_links.append({
                    'title': yt.title + ' (Low Quality Audio)',
                    'audio': audio_only_stream.url
                })

        return download_links
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []


bot.polling()
              
