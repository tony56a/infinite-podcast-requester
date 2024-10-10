import asyncio
import discord
import logging

from redis_client import RedisClient
from logging.handlers import TimedRotatingFileHandler
from rabbitmq_listener import listener_init
from scheduled_script_builder_task import my_function
from discord_bot import bot, generate_show_cmd, regenerate_show_cmd
from config import configuration

logger = logging.getLogger()
rotating_file_handler = TimedRotatingFileHandler(
    filename="requester.log", when="h", interval=6, backupCount=4
)
formatter = logging.Formatter("%(asctime)s %(name)s:%(levelname)s - %(message)s")
rotating_file_handler.setFormatter(formatter)
logger.addHandler(rotating_file_handler)
logger.setLevel(logging.INFO)

redis_client = None

@bot.event
async def on_ready():
    guild_ids = configuration["discord"]["guilds"]
    guilds = [discord.utils.get(bot.guilds, id=guild_id)
              for guild_id in guild_ids]
    bot.tree.add_command(generate_show_cmd, guilds=guilds)
    bot.tree.add_command(regenerate_show_cmd, guilds=guilds)
    for guild in guilds:
        await bot.tree.sync(guild=guild)
    logger.info("discord client ready")

async def run():
    global redis_client

    redis_client = RedisClient()

    rabbitmq_task = asyncio.create_task(listener_init())
    task = asyncio.create_task(my_function(redis_client=redis_client))
    async with bot:
        await bot.start(configuration["discord"]["token"])
    await task


if __name__ == "__main__":
    asyncio.run(run())
