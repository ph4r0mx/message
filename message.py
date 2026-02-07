import os
import discord
from discord.ext import commands
from discord.ui import Select, View, Modal, TextInput

# =====================
# CONFIG
# =====================
TOKEN = os.getenv("DISCORD_TOKEN")  # Variable Railway
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN non défini dans les variables Railway")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =====================
# MODAL (écriture du message)
# =====================
class MessageModal(Modal):
    def __init__(self, channel: discord.TextChannel):
        super().__init__(title=f"Envoyer un message dans #{channel.name}")
        self.channel = channel

        self.message_input = TextInput(
            label="Ton message",
            placeholder="Écris ton message ici...",
            style=discord.InputTextStyle.paragraph,
            required=True,
            max_length=2000
        )
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.channel.send(self.message_input.value)
            await interaction.response.send_message(
                f"✅ Message envoyé dans {self.channel.mention}",
                ephemeral=True
            )
        except Exception as e:
            print("ERREUR ENVOI MESSAGE :", e)
            await interaction.response.send_message(
                "❌ Impossible d’envoyer le message (permissions ?)",
                ephemeral=True
            )

# =====================
# COMMANDE !menu
# =====================
@bot.command()
async def menu(ctx: commands.Context):
    # Sécurité
    if ctx.guild is None:
        return

    # Options = salons textuels où le bot peut écrire
    options = []
    for channel in ctx.guild.text_channels:
        perms = channel.permissions_for(ctx.guild.me)
        if perms.send_messages and perms.view_channel:
            options.append(
                discord.SelectOption(
                    label=channel.name,
                    value=str(channel.id)
                )
            )

    if not options:
        await ctx.send("❌ Aucun salon disponible.")
        return

    select = Select(
        placeholder="Choisis le salon",
        options=options,
        min_values=1,
        max_values=1
    )

    async def select_callback(interaction: discord.Interaction):
        channel_id = int(select.values[0])
        channel = interaction.guild.get_channel(channel_id)

        if channel is None:
            await interaction.response.send_message(
                "❌ Salon introuvable.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(MessageModal(channel))

    select.callback = select_callback

    view = View(timeout=None)
    view.add_item(select)

    await ctx.send(
        "📨 **Choisis le salon où envoyer le message :**",
        view=view
    )

# =====================
# READY
# =====================
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

# =====================
# RUN
# =====================
bot.run(TOKEN)
