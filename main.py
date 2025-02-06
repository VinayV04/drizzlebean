#import discord
#import os
from discord.ext import commands
import asyncio
import discord
# YouTube downloader
import yt_dlp
from data.tokens import DISCORD_TOKEN
#from discord.ext import voice_recv
#from multiprocessing import Process
#from audio_to_text import save_audio

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
# Initialize the Discord bot
bot = commands.Bot(command_prefix = '!', intents = intents)
"""found_drew = False
current_channel = None
bot_joined = False
vc = None
users = {}
class User:
    audio_data = []
    count = 0
    name = ""
    def __init__(self, name="", count=0, audio_data=[]):
        self.name = name
        self.count = count
        self.audio_data = audio_data
    
# Define an event to be triggered when a message is sent
@bot.command()
async def joinvoice(after, before, member):
    global found_drew, bot_joined, current_channel, vc, count, khase_data, vinay_data, drew_data

    def callback(user, data: voice_recv.VoiceData):
            global users
            if user.name not in users:
                users[user.name] = User(user.name, 1, [data.pcm])
            else:
                users[user.name].count = users[user.name].count + 1
                users[user.name].audio_data.append(data.pcm)
            
            if users[user.name].count > 800:
                 print(user.name + " ")
                 Process(target=save_audio, args=[users[user.name].audio_data, f"{user.name}.wav"]).start()
                 users[user.name].count = 0
                 #users[user.name].audio_data.clear()

    if member.channel is not None:
        for user in member.channel.members:
            if (user.display_name == 'bipty' or user.display_name == 'drewski') and not found_drew:
                if not found_drew:
                    found_drew = True
                break

        if found_drew and current_channel != member.channel:
            if bot_joined:
                key = next(iter(current_channel.voice_states))
                await current_channel.voice_states[key].channel.guild.voice_client.disconnect() # look into vc.move_to()
                current_channel = member.channel 
                vc = await current_channel.connect(cls=voice_recv.VoiceRecvClient)
            else:
                current_channel = member.channel
                bot_joined = True
                vc = await current_channel.connect(cls=voice_recv.VoiceRecvClient)
            vc.listen(voice_recv.BasicSink(callback)) """





# We'll keep a simple data structure to hold per-guild queues and playback state
guild_queues = {}  # {guild_id: [ (title, url), ... ]}
guild_now_playing = {}  # {guild_id: "Song Title"}
guild_is_paused = {}  # {guild_id: bool}


# Utility function: get (or create) the queue for a guild
def get_guild_queue(guild_id):
    if guild_id not in guild_queues:
        guild_queues[guild_id] = []
    return guild_queues[guild_id]


async def play_next_in_queue(ctx):
    """Play the next song in the queue (if any) for the guild."""
    voice_client = ctx.voice_client
    if voice_client is None or not voice_client.is_connected():
        return  # Bot is not connected to a voice channel

    queue = get_guild_queue(ctx.guild.id)

    if len(queue) == 0:
        # No more songs in the queue
        guild_now_playing[ctx.guild.id] = None
        return

    # Pop the next song from the queue
    song_title, song_url = queue.pop(0)
    guild_now_playing[ctx.guild.id] = song_title

    await ctx.send(f"Now playing: **{song_title}**")

    # Use yt_dlp to get a direct audio source
    # We'll use FFmpegPCMAudio to play in Discord
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',  # for direct URL or searching
        'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 sometimes causes issues
    }
    # Create a stream player via yt_dlp and ffmpeg
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(song_url, download=False)
        audio_url = info['url']

    # Create the audio source
    audio_source = discord.FFmpegPCMAudio(audio_url,
                                          before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5')

    def after_playing(error):
        if error:
            print(f"Error after playing: {error}")
        # Move on to the next track
        fut = asyncio.run_coroutine_threadsafe(play_next_in_queue(ctx), bot.loop)
        try:
            fut.result()
        except Exception as e:
            print(f"Error in after_playing: {e}")

    voice_client.play(audio_source, after=after_playing)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.command(name='join')
async def join_channel(ctx):
    """Make the bot join the user's current voice channel."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Joined {channel}")
    else:
        await ctx.send("You are not in a voice channel.")


@bot.command(name='leave')
async def leave_channel(ctx):
    """Disconnect the bot from the voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Left the voice channel.")
        guild_queues[ctx.guild.id] = []
        guild_now_playing[ctx.guild.id] = None
    else:
        await ctx.send("I'm not in a voice channel.")


@bot.command(name='play')
async def play(ctx, *, search_query: str):
    """
    Play a song by searching on YouTube. If the bot isn't in a channel, it joins.
    Usage: !play <search keywords or YouTube URL>
    """
    # If the bot is not in a voice channel, try to join the user's channel
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("You must be in a voice channel or use !join first.")
            return

    # Use yt_dlp to search for the track
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',  # search for the first matching result
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)

        # If it's a search, 'entries' might be present. If it's a direct URL, it might not be
        if 'entries' in info:
            # Take first item from a search
            info = info['entries'][0]
        video_title = info.get('title', 'Unknown Title')
        video_webpage_url = info.get('webpage_url', None)

    # Add this song to the queue
    queue = get_guild_queue(ctx.guild.id)
    queue.append((video_title, video_webpage_url))

    await ctx.send(f"**{video_title}** added to the queue.")

    # If nothing is playing right now, start playback immediately
    voice_client = ctx.voice_client
    if not voice_client.is_playing():
        await play_next_in_queue(ctx)


@bot.command(name='queue')
async def queue_list(ctx):
    """Show the current queue of songs."""
    queue = get_guild_queue(ctx.guild.id)
    now_playing = guild_now_playing.get(ctx.guild.id, None)

    if now_playing:
        message = f"**Now playing:** {now_playing}\n\n"
    else:
        message = "**Nothing is currently playing.**\n\n"

    if len(queue) == 0:
        message += "*Queue is empty.*"
    else:
        message += "**Queue:**\n"
        for i, (title, url) in enumerate(queue, start=1):
            message += f"{i}. {title}\n"
    await ctx.send(message)


@bot.command(name='skip')
async def skip_song(ctx):
    """Skip the current song."""
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Song skipped.")
    else:
        await ctx.send("No song is currently playing.")


@bot.command(name='pause')
async def pause_song(ctx):
    """Pause the current song."""
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        guild_is_paused[ctx.guild.id] = True
        await ctx.send("Song paused.")
    else:
        await ctx.send("No song is currently playing to pause.")


@bot.command(name='resume')
async def resume_song(ctx):
    """Resume a paused song."""
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        guild_is_paused[ctx.guild.id] = False
        await ctx.send("Song resumed.")
    else:
        await ctx.send("No song is paused at the moment.")

@bot.command()
async def drew(ctx):
    await ctx.send("drew is now a bot")

@bot.command()
async def whatdoesdrewlike(ctx):
    await ctx.send("big booty latinas and a buffalo ranch chicken strip sandwich")


@bot.command()
async def whatdoesdrewsay(ctx):
    await ctx.send("what, umm.... what.... what say that again..... what.... yeah, no, wait..... what")

@bot.command()
async def drewbuild(ctx):
    await ctx.send("Height: 6'1\nWeight: 205 lbs\nVertical: 2% Dunk Chance\nStatus: Uncle Dilembe\nOverall: 23")



def main():
    #overlay = Process(target=start_overlay)
    #overlay.start() 
    bot.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()