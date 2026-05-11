import discord
from discord.ui import Modal, TextInput


class StickyModal(Modal, title="Create Sticky Message"):
    content = TextInput(
        label="Message Content",
        style=discord.TextStyle.paragraph,
        placeholder="Enter the content of your sticky message...",
        required=True,
        max_length=1800,
    )

    def __init__(self, callback):
        super().__init__()
        self.callback_fn = callback

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback_fn(self.content.value, interaction)
