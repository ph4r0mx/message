import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

pending_messages = {}

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

@bot.command()
async def envoyer(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("Quel est le message que tu veux envoyer ?")
        
        def check_msg(m):
            return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)
        
        message = await bot.wait_for("message", check=check_msg)
        pending_messages[ctx.author.id] = message.content

        await ctx.send("Dans quel salon veux-tu l'envoyer ? Réponds avec le nom ou l'ID du salon.")

        def check_channel(m):
            return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)
        
        channel_msg = await bot.wait_for("message", check=check_channel)
        
        channel = None
        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name=channel_msg.content)
            if channel is not None:
                break
            if channel_msg.content.isdigit():
                channel = guild.get_channel(int(channel_msg.content))
                if channel is not None:
                    break

        if channel is None:
            await ctx.send("Salon introuvable ! Vérifie le nom ou l'ID.")
        else:
            await channel.send(pending_messages[ctx.author.id])
            await ctx.send(f"Message envoyé dans {channel.name} ✅")
            del pending_messages[ctx.author.id]
    else:
        await ctx.send("Envoie-moi un DM pour utiliser cette commande !")

# Récupère le token depuis la variable d'environnement RAILWAY_DISCORD_TOKEN
token = os.environ.get("RAILWAY_DISCORD_TOKEN")
bot.run(token)
