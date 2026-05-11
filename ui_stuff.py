import discord
from discord.ui import Modal, TextInput
from discord import Embed


class StickyModal(Modal, title="Create Sticky Message"):
    embed_title = TextInput(
        label="Title",
        style=discord.TextStyle.short,
        placeholder="Enter your title...",
        required=True,
        max_length=1800,
    )
    description = TextInput(
        label="Description",
        style=discord.TextStyle.paragraph,
        placeholder="Enter your description...",
        required=True,
        max_length=1800,
    )
    color = TextInput(
        label="Color (Hex Code)",
        style=discord.TextStyle.short,
        placeholder="e.g. #FF5733",
        required=False,
        max_length=7,
    )

    def __init__(self, callback):
        super().__init__()
        self.callback_fn = callback

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback_fn(self.embed_title.value, self.description.value, self.color.value, interaction)
