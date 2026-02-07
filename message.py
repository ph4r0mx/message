import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Modal pour saisir le message
class MessageModal(discord.ui.Modal, title="Écris ton message"):
    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel
        self.message_input = discord.ui.TextInput(
            label="Message à envoyer",
            style=discord.TextStyle.paragraph,
            placeholder="Écris ton message ici...",
            required=True,
            max_length=2000
        )
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        await self.channel.send(self.message_input.value)
        await interaction.response.send_message(f"Message envoyé dans {self.channel.name} ✅", ephemeral=True)

# Select pour choisir le salon
class ChannelSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=channel.name, description=f"ID: {channel.id}", value=str(channel.id))
            for guild in bot.guilds
            for channel in guild.text_channels
        ]
        super().__init__(placeholder="Choisis un salon...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        channel_id = int(self.values[0])
        channel = bot.get_channel(channel_id)
        if channel:
            modal = MessageModal(channel)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message("Salon introuvable !", ephemeral=True)

class ChannelView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ChannelSelect())

@bot.command()
async def envoyer(ctx):
    """Commande pour envoyer un message interactif"""
    view = ChannelView()
    await ctx.send("Choisis le salon où tu veux envoyer ton message :", view=view)

# Token depuis Railway
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)

