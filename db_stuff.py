import asyncio
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


class DBClient:
    listened_channels: list[int] = []
    stickied_messages: list = []

    def __init__(self, console, cache_refresh_interval):
        # Setting up database connection
        db_url: str = os.getenv("DATABASE_URL")
        self.engine = create_engine(db_url)

        self.console = console
        self.cache_refresh_interval = cache_refresh_interval

        self.refresh_cache()

    async def start_cache_refresh(self):
        asyncio.create_task(self.refresh_cache_task())

    async def refresh_cache_task(self):
        print("Starting cache refresh task...")
        while True:
            self.console.log("Refreshing cache...")
            self.refresh_cache()
            await asyncio.sleep(self.cache_refresh_interval)

    def refresh_cache(self):
        self.listened_channels = self.fetch_listened_channels()
        self.stickied_messages = self.fetch_sticky_messages()

    def fetch_sticky_messages(self):
        try:
            with Session(self.engine) as session:
                result = session.execute(text("SELECT * FROM sticky_messages"))
                return [row._asdict() for row in result]
        except Exception as e:
            self.console.print(f"Error fetching sticky messages: {e}", style="red")
            return []

    def fetch_listened_channels(self):
        try:
            data = self.fetch_sticky_messages()
            return list(set([msg["channel_id"] for msg in data]))
        except Exception as e:
            self.console.print(f"Error fetching listened channels: {e}", style="red")
            return []

    def post_sticky_message(self, message_id: int, channel_id: int, guild_id: int, title: str, description: str, color: str):
        try:
            with Session(self.engine) as session:
                session.execute(
                    text("""
                        INSERT INTO sticky_messages (message_id, channel_id, guild_id, title, description, color)
                        VALUES (:message_id, :channel_id, :guild_id, :title, :description, :color)
                    """),
                    {"message_id": message_id, "channel_id": channel_id, "guild_id": guild_id, "title": title, "description": description, "color": color}
                )
                session.commit()
        except Exception as e:
            self.console.print(f"Error posting sticky message: {e}", style="red")

    def refresh_sticky_message(self, old_id: int, new_id: int):
        try:
            with Session(self.engine) as session:
                session.execute(
                    text("UPDATE sticky_messages SET message_id = :new_id WHERE message_id = :old_id"),
                    {"new_id": new_id, "old_id": old_id}
                )
                session.commit()
        except Exception as e:
            self.console.print(f"Error refreshing sticky message: {e}", style="red")

    def delete_sticky_message(self, message_id: int):
        try:
            with Session(self.engine) as session:
                session.execute(
                    text("DELETE FROM sticky_messages WHERE message_id = :message_id"),
                    {"message_id": message_id}
                )
                session.commit()
        except Exception as e:
            self.console.print(f"Error deleting sticky message: {e}", style="red")
