import os
import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput

# =====================
# CONFIG
# =====================
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN manquant")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =====================
# MODAL
# =====================
class MessageModal(Modal):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(title=f"Envoyer un message dans #{channel.name}")
        self.channel = channel

        self.message = TextInput(
            label="Message",
            style=discord.InputTextStyle.paragraph,
            required=True,
            max_length=2000
        )
        self.add_item(self.message)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.channel.send(self.message.value)
            await interaction.response.send_message(
                "✅ Message envoyé",
                ephemeral=True
            )
        except Exception as e:
            print("ERREUR :", e)
            await interaction.response.send_message(
                "❌ Impossible d’envoyer le message (permissions)",
                ephemeral=True
            )

# =====================
# SELECT MENU
# =====================
class ChannelSelect(Select):
    def __init__(self, guild: discord.Guild):
        options = []

        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.send_messages and perms.view_channel:
                options.append(
                    discord.SelectOption(
                        label=channel.name,
                        value=str(channel.id)
                    )
                )

        super().__init__(
            placeholder="Choisis un salon",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        channel_id = int(self.values[0])
        channel = interaction.guild.get_channel(channel_id)

        if channel is None:
            await interaction.response.send_message(
                "❌ Salon introuvable",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(MessageModal(channel))

# =====================
# VIEW
# =====================
class ChannelView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=None)
        self.add_item(ChannelSelect(guild))

# =====================
# COMMANDE !menu
# =====================
@bot.command()
async def menu(ctx: commands.Context):
    if ctx.guild is None:
        return

    await ctx.send(
        "📨 **Choisis le salon où envoyer le message :**",
        view=ChannelView(ctx.guild)
    )

# =====================
# READY
# =====================
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

bot.run(TOKEN)
