import discord
from discord import app_commands
from playwright.async_api import async_playwright
import asyncio
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MINESTRATOR_EMAIL = os.getenv('MINESTRATOR_EMAIL')
MINESTRATOR_PASSWORD = os.getenv('MINESTRATOR_PASSWORD')
MINESTRATOR_PANEL_URL = os.getenv('MINESTRATOR_PANEL_URL')  # URL du panel de gestion de votre serveur

# Configuration du bot Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Commande /start pour démarrer le serveur
@tree.command(name="start", description="Démarre le serveur Minecraft hébergé sur MineStrator")
async def start(interaction: discord.Interaction):
    await interaction.response.defer()  # Répondre de manière différée pour éviter le timeout

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Connexion au panel MineStrator
            await page.goto('https://minestrator.com/login')
            await page.fill('input[name="email"]', MINESTRATOR_EMAIL)
            await page.fill('input[name="password"]', MINESTRATOR_PASSWORD)
            await page.click('button[type="submit"]')

            # Attendre que la connexion soit effective
            await page.wait_for_url('**/dashboard**', timeout=10000)

            # Naviguer vers le panel de gestion du serveur
            await page.goto(MINESTRATOR_PANEL_URL)

            # Cliquer sur le bouton de démarrage (ajustez le sélecteur selon l'interface de MineStrator)
            start_button = await page.query_selector('button:has-text("Démarrer")')  # Ajustez le sélecteur si nécessaire
            if start_button:
                await start_button.click()
                await page.wait_for_timeout(5000)  # Attendre que l'action soit effectuée
                await interaction.followup.send("Le serveur Minecraft a été démarré avec succès !")
            else:
                await interaction.followup.send("Erreur : Bouton de démarrage non trouvé. Vérifiez l'URL du panel ou l'état du serveur.")

            await browser.close()

    except Exception as e:
        await interaction.followup.send(f"Erreur lors du démarrage du serveur : {str(e)}")

# Événement déclenché lorsque le bot est prêt
@client.event
async def on_ready():
    print(f'Connecté en tant que {client.user}')
    await tree.sync()  # Synchroniser les commandes slash
    print("Commandes synchronisées")

# Lancer le bot
async def main():
    await client.start(DISCORD_TOKEN)

if __name__ == "__main__":
    if os.getenv('EMSCRIPTEN'):
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())