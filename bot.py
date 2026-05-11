import asyncio
import os

import discord
from discord import Intents, Interaction, Message, app_commands
from dotenv import load_dotenv
from rich.console import Console

from db_stuff import DBClient
from ui_stuff import StickyModal

load_dotenv()

console = Console()

CACHE_REFRESH_INTERVAL = 300  # seconds
GUILD_ID = int(os.getenv("GUILD_ID"))
OWNER_ID = int(os.getenv("OWNER_ID"))


def is_authorized(interaction: Interaction) -> bool:
    return interaction.user.guild_permissions.administrator or interaction.user.id == OWNER_ID


class StickyBot(discord.Client):
    def __init__(self):
        intents = Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

        self.sticky_locks: dict[int, asyncio.Lock] = {}
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))
        console.print("Commands synced.", style="green")


client = StickyBot()
db_client = DBClient(console, CACHE_REFRESH_INTERVAL)


@client.event
async def on_ready():
    console.print(f"Logged in as [green]{client.user.name}[/green]")
    await db_client.start_cache_refresh()

    console.print("Validating sticky messages...")
    stale = []

    for sticky in db_client.stickied_messages:
        channel = client.get_channel(sticky["channel_id"])

        if channel is None:
            console.print(f"[yellow]Channel {sticky['channel_id']} not found. Marking sticky {sticky['message_id']} for removal.[/yellow]")
            stale.append(sticky["message_id"])
            continue

        try:
            await channel.fetch_message(sticky["message_id"])
            console.print(f"[green]✓[/green] Sticky {sticky['message_id']} in #{channel.name} is valid")
        except discord.NotFound:
            console.print(f"[yellow]Sticky {sticky['message_id']} not found in #{channel.name}. Marking for removal.[/yellow]")
            stale.append(sticky["message_id"])
        except Exception as e:
            console.print(f"[red]Error validating sticky {sticky['message_id']}: {e}[/red]")

    if stale:
        console.print(f"[yellow]Removing {len(stale)} stale sticky message(s)...[/yellow]")
        for message_id in stale:
            db_client.delete_sticky_message(message_id)
        db_client.refresh_cache()
        console.print("[green]✓ Cleaned up stale sticky messages.[/green]")
    else:
        console.print("[green]✓ All sticky messages are valid![/green]")


@client.event
async def on_message(message: Message):
    if message.author.id == client.user.id:
        return

    if message.channel.id not in db_client.listened_channels:
        return

    if message.channel.id not in client.sticky_locks:
        client.sticky_locks[message.channel.id] = asyncio.Lock()

    async with client.sticky_locks[message.channel.id]:
        for sticky in db_client.stickied_messages:
            if sticky["channel_id"] != message.channel.id:
                continue

            try:
                old_message = await message.channel.fetch_message(sticky["message_id"])
                await old_message.delete()
                new_message = await message.channel.send(embed=create_embed(sticky["title"], sticky["description"], sticky["color"]))
                db_client.refresh_sticky_message(old_message.id, new_message.id)
                db_client.refresh_cache()
            except discord.NotFound:
                console.print(f"[yellow]Sticky {sticky['message_id']} not found in channel {message.channel.id}. Recreating.[/yellow]")
                new_message = await message.channel.send(embed=create_embed(sticky["title"], sticky["description"], sticky["color"]))
                db_client.refresh_sticky_message(sticky["message_id"], new_message.id)
                db_client.refresh_cache()
            except Exception as e:
                console.print(f"[red]Error handling sticky {sticky['message_id']} in channel {message.channel.id}: {e}[/red]")

            break


# -----------------------------
# --- Sticky Message Commands --
# -----------------------------

@client.tree.command(name="make-sticky", description="Creates a message that stays at the bottom of the channel.")
async def make_sticky(interaction: Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    await interaction.response.send_modal(StickyModal(create_sticky_message))


def create_embed(title: str, description: str, color: str) -> discord.Embed:
    embed_color = discord.Color.default()
    if color:
        try:
            embed_color = discord.Color(int(color.lstrip("#"), 16))
        except ValueError:
            pass  # Invalid color, fallback to default

    embed = discord.Embed(title=title, description=description, color=embed_color)
    return embed


async def create_sticky_message(title: str, description: str, color: str, interaction: Interaction):
    sticky_msg = await interaction.channel.send(embed=create_embed(title, description, color))
    db_client.post_sticky_message(sticky_msg.id, interaction.channel.id, interaction.guild.id, title, description, color)
    db_client.refresh_cache()
    await interaction.response.send_message("Sticky message created!", ephemeral=True)


@client.tree.command(name="remove-sticky", description="Removes a sticky message from this channel.")
@app_commands.describe(message_id="The ID of the sticky message to remove")
async def remove_sticky(interaction: Interaction, message_id: str):
    if not is_authorized(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    await interaction.response.send_message("Removing sticky message...", ephemeral=True)

    try:
        message = await interaction.channel.fetch_message(int(message_id))
        await message.delete()
    except discord.NotFound:
        pass  # Already gone from Discord, still clean up DB

    db_client.delete_sticky_message(int(message_id))
    db_client.refresh_cache()
    await interaction.edit_original_response(content="Sticky message removed!")


@remove_sticky.autocomplete("message_id")
async def remove_sticky_autocomplete(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
    filtered = [
        s for s in db_client.stickied_messages
        if str(s["message_id"]).startswith(current) and s["channel_id"] == interaction.channel.id
    ]
    return [
        app_commands.Choice(
            name=f"ID: {s['message_id']} | Title: {s['title'][:30]}{'...' if len(s['title']) > 30 else ''}",
            value=str(s["message_id"])
        )
        for s in filtered[:25]
    ]


@client.tree.command(name="refresh-cache", description="Manually refreshes the sticky message cache.")
async def refresh_cache_command(interaction: Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    db_client.refresh_cache()

    embed = discord.Embed(title="Cache Refreshed", color=discord.Color.green())
    embed.add_field(name="Sticky Messages", value=len(db_client.stickied_messages), inline=False)
    embed.add_field(name="Listened Channels", value=len(db_client.listened_channels), inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


client.run(os.getenv("TOKEN"))
