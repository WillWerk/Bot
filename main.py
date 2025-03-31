import discord
import tweepy
import os
import asyncio
from dotenv import load_dotenv

# Laad de API-sleutels en tokens vanuit .env
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# Twitter-authenticatie
client_twitter = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET
)

# Discord client instellen
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Laad de tweets uit het bestand
def load_tweets(filename="tweets.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return [line.strip().replace("/n", "\n") for line in file if line.strip()]
    except FileNotFoundError:
        return []

tweets = load_tweets()

@client.event
async def on_ready():
    print(f'✅ {client.user} is ingelogd en klaar om te tweeten!')
    asyncio.create_task(send_periodic_tweet())

async def send_periodic_tweet(channel=None):
    while True:
        global tweets
        if not tweets:
            if channel:
                await channel.send("❌ Geen tweets meer over!")
            return

        tweet_text = tweets.pop(0)  # Pak de eerste tweet en verwijder uit lijst
        try:
            print(f"Probeer tweet te plaatsen: {tweet_text}")
            print(f"Twitter credentials aanwezig?: API Key: {'Ja' if TWITTER_API_KEY else 'Nee'}, API Secret: {'Ja' if TWITTER_API_SECRET else 'Nee'}, Access Token: {'Ja' if TWITTER_ACCESS_TOKEN else 'Nee'}, Access Secret: {'Ja' if TWITTER_ACCESS_SECRET else 'Nee'}")

            if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
                raise Exception("Niet alle Twitter credentials zijn aanwezig in .env")

            response = client_twitter.create_tweet(text=tweet_text)
            if response and hasattr(response, 'data'):
                print(f"Tweet posted successfully! Tweet ID: {response.data['id']}")
                if channel:
                    await channel.send(f"✅ Tweet geplaatst: {tweet_text}")
            else:
                error_msg = "No response data received from Twitter"
                print(error_msg)
                if channel:
                    await channel.send(f"❌ {error_msg}")

            # Opslaan van resterende tweets
            with open("tweets.txt", "w", encoding="utf-8") as file:
                file.write("\n".join(tweets))

        except Exception as e:
            if channel:
                await channel.send(f"❌ Fout bij tweeten: {e}")
            print(f"Fout: {e}")

        # Wacht 8 uur voor de volgende tweet
        await asyncio.sleep(8 * 60 * 60)  # 8 uur in seconden

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith("!tweet"):
        try:
            await send_periodic_tweet(message.channel)
        except Exception as e:
            await message.channel.send(f"❌ Fout bij tweeten: {e}")
            print(f"Fout: {e}")

# Start de bot
client.run(DISCORD_TOKEN)
