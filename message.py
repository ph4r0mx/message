import os
import discord
from discord.ext import commands
from discord.ui import Select, View, Modal, TextInput

# ----- TON TOKEN DIRECTEMENT ICI -----
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1469055922935562333  # Ton serveur

# ----- Intents -----
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Très important pour lire les messages textuels

bot = commands.Bot(command_prefix="!", intents=intents)

# ----- Modal pour écrire le message -----
class MessageModal(Modal):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(title=f"Envoyer un message dans {channel.name}")
        self.channel = channel
        self.message_input = TextInput(
            label="Ton message",
            placeholder="Écris ici ton message...",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        await self.channel.send(self.message_input.value)
        await interaction.response.send_message(f"Message envoyé dans {self.channel.mention} ✅", ephemeral=True)

# ----- Commande pour afficher le menu des salons -----
@bot.command()
async def menu(ctx):
    options = [
        discord.SelectOption(label=channel.name, value=str(channel.id))
        for channel in ctx.guild.text_channels
    ]

    select = Select(
        placeholder="Choisis le salon où envoyer le message",
        options=options
    )

    async def select_callback(interaction: discord.Interaction):
        channel_id = int(select.values[0])
        channel = bot.get_channel(channel_id)
        await interaction.response.send_modal(MessageModal(channel))

    select.callback = select_callback

    view = View()
    view.add_item(select)
    await ctx.send("Choisis un salon pour envoyer ton message :", view=view)

# ----- Quand le bot est prêt -----
@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

bot.run(TOKEN)


