mport discord
from discord.ext import commands
from discord.ui import Button, View
import random
from datetime import datetime, timedelta

TOKEN = 'YOUR_NEW_BOT_TOKEN'  # Replace with your bot token
ADMIN_ID = 761596177250254848  # Replace with your ID

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

bp_codes = [
    # Add your BP codes here
]

# List of allowed voice channel IDs
voice_channel_ids = [
    1274680827569246281
    # Add more IDs here...
]

# Logs channel ID
logs_channel_id = 1274610027491233857  
user_stream_times = {}

# Function to check if the user has streamed for 30 minutes
async def check_stream_time(user):
    if user in user_stream_times and user_stream_times[user] is not None:
        elapsed_time = datetime.utcnow() - user_stream_times[user]
        if elapsed_time >= timedelta(minutes=30):
            return True, None
        else:
            remaining_time = timedelta(minutes=30) - elapsed_time
            return False, remaining_time
    return False, timedelta(minutes=30)

# Function to pick a random code
def pick_code(codes):
    if codes:
        code = random.choice(codes)
        codes.remove(code)
        return code
    return None

# Function to send BP code
async def bpcodes(interaction):
    code = pick_code(bp_codes)
    if code:
        user_stream_times[interaction.user] = None  # Reset stream time
        embed = discord.Embed(title="Your BP Code", description=f"**{code}**", color=discord.Color.green())
        embed.set_footer(text="Use this code responsibly.")
        await interaction.user.send(embed=embed)
        
        # Log the event in the logs channel
        logs_channel = bot.get_channel(logs_channel_id)
        if logs_channel:
            await logs_channel.send(f"{interaction.user.mention} has received a BP Key: {code}")
    else:
        await interaction.user.send("Keys are finished. Please wait for a refill.")

class CodeButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="BP Key", style=discord.ButtonStyle.primary)
    async def apply_bp(self, interaction: discord.Interaction, button: discord.ui.Button):
        can_receive, remaining_time = await check_stream_time(interaction.user)
        if can_receive:
            await bpcodes(interaction)
            await interaction.response.send_message("BP Key has been sent to your DMs.", ephemeral=True)
        else:
            await interaction.response.send_message(f"You opened a stream but you haven't completed the time. Please wait {remaining_time} before requesting a BP Key.", ephemeral=True)

@bot.command(name='start')
async def start(ctx):
    embed = discord.Embed(
        title="FREE KEYS",
        description="Click the button below to request a BP Key.",
        color=discord.Color.blue()
    )
    embed.set_image(url="https://i.imgur.com/0F1pDSS.png")  # Replace with your image URL
    view = CodeButton()
    await ctx.send(embed=embed, view=view)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id in voice_channel_ids and after.self_stream:
        if member not in user_stream_times or user_stream_times[member] is None:
            user_stream_times[member] = datetime.utcnow()
        elif isinstance(user_stream_times[member], timedelta):
            user_stream_times[member] = datetime.utcnow() - user_stream_times[member]
    elif before.channel and before.channel.id in voice_channel_ids and not after.self_stream:
        if member in user_stream_times:
            elapsed_time = datetime.utcnow() - user_stream_times[member]
            if isinstance(user_stream_times[member], datetime):
                user_stream_times[member] = elapsed_time
            else:
                user_stream_times[member] += elapsed_time  # Accumulate the time
            
            # Check if the user has completed 30 minutes
            if elapsed_time >= timedelta(minutes=30):
                try:
                    await member.send("You have completed 30 minutes of streaming. You can get your BP key now.")
                except discord.Forbidden:
                    pass  # Ignore if unable to send a message

bot.run(TOKEN)
