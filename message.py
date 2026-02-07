import os
import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import traceback

# =====================
# CONFIG
# =====================
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ DISCORD_TOKEN manquant dans Railway")

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
        super().__init__(title=f"Message pour #{channel.name}")
        self.channel = channel

        self.message_input = TextInput(
            label="Ton message",
            placeholder="Écris ton message ici…",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        print(f"📝 [{interaction.user}] tente d'envoyer dans #{self.channel.name}")
        
        try:
            # Vérifier les permissions
            perms = self.channel.permissions_for(interaction.guild.me)
            if not perms.send_messages:
                await interaction.response.send_message(
                    f"❌ Je n'ai pas la permission d'envoyer dans {self.channel.mention}",
                    ephemeral=True
                )
                print(f"⚠️ Permissions manquantes dans #{self.channel.name}")
                return
            
            # Envoyer le message
            msg = await self.channel.send(self.message_input.value)
            print(f"✅ Message envoyé : {msg.jump_url}")
            
            # Confirmer à l'utilisateur
            await interaction.response.send_message(
                f"✅ Message envoyé dans {self.channel.mention}\n[Voir le message]({msg.jump_url})",
                ephemeral=True
            )
            
        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ Permission refusée pour {self.channel.mention}",
                ephemeral=True
            )
            print(f"❌ Forbidden dans #{self.channel.name}")
            
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"❌ Erreur Discord : {e}",
                ephemeral=True
            )
            print(f"❌ HTTPException : {e}")
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erreur inattendue : {type(e).__name__}",
                ephemeral=True
            )
            print(f"❌ ERREUR CRITIQUE :")
            traceback.print_exc()

# =====================
# SELECT MENU
# =====================
class ChannelSelect(Select):
    def __init__(self, guild: discord.Guild):
        options = []

        # Récupérer tous les salons textuels accessibles
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.view_channel and perms.send_messages:
                options.append(
                    discord.SelectOption(
                        label=f"#{channel.name}",
                        value=str(channel.id),
                        description=f"Catégorie : {channel.category.name if channel.category else 'Aucune'}"
                    )
                )

        # Si aucun salon disponible
        if not options:
            options.append(
                discord.SelectOption(
                    label="Aucun salon disponible",
                    value="0",
                    description="Le bot n'a accès à aucun salon"
                )
            )

        super().__init__(
            placeholder="📌 Sélectionne un salon",
            options=options[:25],  # Discord limite à 25 options
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        channel_id = int(self.values[0])
        
        # Vérifier si c'est le salon "aucun"
        if channel_id == 0:
            await interaction.response.send_message(
                "❌ Aucun salon disponible",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(channel_id)

        if channel is None:
            await interaction.response.send_message(
                "❌ Salon introuvable",
                ephemeral=True
            )
            return

        # Ouvrir le modal
        await interaction.response.send_modal(MessageModal(channel))

# =====================
# VIEW
# =====================
class ChannelView(View):
    def __init__(self, guild: discord.Guild):
        super().__init__(timeout=300)  # 5 minutes de timeout
        self.add_item(ChannelSelect(guild))

# =====================
# COMMANDES
# =====================
@bot.command(name="menu")
async def menu(ctx: commands.Context):
    """Affiche le menu de sélection de salon"""
    if ctx.guild is None:
        await ctx.send("❌ Cette commande ne fonctionne que dans un serveur")
        return

    view = ChannelView(ctx.guild)
    await ctx.send(
        "📨 **Choisis le salon où envoyer ton message :**",
        view=view
    )

@bot.command(name="ping")
async def ping(ctx: commands.Context):
    """Vérifie si le bot est en ligne"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong ! Latence : {latency}ms")

@bot.command(name="permissions")
async def permissions(ctx: commands.Context, channel: discord.TextChannel = None):
    """Vérifie les permissions du bot dans un salon"""
    if ctx.guild is None:
        return
    
    target = channel or ctx.channel
    perms = target.permissions_for(ctx.guild.me)
    
    status = []
    checks = {
        "View Channel": perms.view_channel,
        "Send Messages": perms.send_messages,
        "Embed Links": perms.embed_links,
        "Attach Files": perms.attach_files,
        "Read Message History": perms.read_message_history
    }
    
    for perm_name, has_perm in checks.items():
        emoji = "✅" if has_perm else "❌"
        status.append(f"{emoji} {perm_name}")
    
    await ctx.send(
        f"**Permissions dans {target.mention} :**\n" + "\n".join(status)
    )

# =====================
# EVENTS
# =====================
@bot.event
async def on_ready():
    print("=" * 50)
    print(f"✅ Bot connecté : {bot.user}")
    print(f"📊 ID : {bot.user.id}")
    print(f"🌐 Serveurs : {len(bot.guilds)}")
    print("=" * 50)
    
    # Lister les serveurs
    for guild in bot.guilds:
        print(f"  - {guild.name} ({guild.id})")
        text_channels = len([c for c in guild.text_channels if c.permissions_for(guild.me).send_messages])
        print(f"    └─ Salons accessibles : {text_channels}/{len(guild.text_channels)}")

@bot.event
async def on_command_error(ctx: commands.Context, error):
    """Gestion globale des erreurs"""
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu n'as pas les permissions nécessaires")
        return
    
    print(f"❌ Erreur dans {ctx.command} :")
    traceback.print_exception(type(error), error, error.__traceback__)

# =====================
# RUN
# =====================
if __name__ == "__main__":
    print("🚀 Démarrage du bot...")
    bot.run(TOKEN)
