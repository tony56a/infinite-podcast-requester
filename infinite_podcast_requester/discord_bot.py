import discord
import grpc
import logging
import script_builder_utils

from config import configuration
from discord import app_commands
from discord.ext import commands
from enums.v1 import (
    ext_user_source_pb2,
    script_type_pb2,
    character_type_pb2,
    speaker_voice_type_pb2,
)
from services.v1 import script_service_pb2_grpc, script_service_pb2

logger = logging.getLogger()


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)

async def character_type_autocomplete(
    interaction: discord.Interaction,
    current: str,
):
    character_types = {
        "Normal": character_type_pb2.CHARACTER_TYPE_NORMAL, 
        "Skeleton": character_type_pb2.CHARACTER_TYPE_SKELETON, 
        "Robot": character_type_pb2.CHARACTER_TYPE_ROBOT,
        "Random": -1,
        }
    
    return [
        app_commands.Choice(name=character_type, value=character_types[character_type])
        for character_type in character_types.keys() if current.lower() in character_type.lower()
    ]

async def show_type_autocomplete(
    interaction: discord.Interaction,
    current: str,
):
    show_types = {
        "Podcast": script_type_pb2.SCRIPT_TYPE_PODCAST,
        "Rap Battle": script_type_pb2.SCRIPT_TYPE_RAP_BATTLE, 
        "Business Talk": script_type_pb2.SCRIPT_TYPE_BUSINESS_TALK,
        }
    
    return [
        app_commands.Choice(name=show_type, value=show_types[show_type])
        for show_type in show_types.keys() if current.lower() in show_type.lower()
    ]

async def voice_type_autocomplete(
    interaction: discord.Interaction,
    current: str,
):
    speaker_types = {
        "Male": speaker_voice_type_pb2.SPEAKER_VOICE_TYPE_MALE,
        "Female": speaker_voice_type_pb2.SPEAKER_VOICE_TYPE_FEMALE, 
        "Random": -1,
        }
    
    return [
        app_commands.Choice(name=speaker_type, value=speaker_types[speaker_type])
        for speaker_type in speaker_types.keys() if current.lower() in speaker_type.lower()
    ]

@app_commands.command(name="generate_script", description="Generate a script for playback")
@app_commands.autocomplete(character_type=character_type_autocomplete, show_type=show_type_autocomplete, voice_type=voice_type_autocomplete)
@app_commands.describe(topic='The topic the show is about',
                        character_type='The voice channel to send the clip to',
                       show_type='The type of show (podcast, rap battle, etc)',
                       voice_type='The type of voice to use')
async def generate_show_cmd(interaction: discord.Interaction, topic: str, character_type: int, show_type: int, voice_type: int):
    if character_type < 0:
        character_type = None
    if voice_type < 0:
        voice_type = None

    character = script_builder_utils.build_character(
        character_type=character_type,
        speaker_voice_type=voice_type
    )

    user = script_builder_utils.build_user(ext_id=interaction.user.global_name, source=ext_user_source_pb2.EXT_USER_SOURCE_DISCORD)
    script_request = script_builder_utils.build_script_request(topic = topic, user=user, guest_character=character)
    try:
        async with grpc.aio.insecure_channel(
            configuration["service"]["path"]
        ) as grpc_channel:
            service = script_service_pb2_grpc.ScriptServiceStub(grpc_channel)
            await service.CreateScript(request=script_request)
    except Exception as e:
        logger.exception(e)
    await interaction.response.send_message(f'Sent a request for a show with topic {topic}', ephemeral=True)

@app_commands.command(name="regenerate_script", description="Regenerate a script for playback")
@app_commands.describe(script_id='The ID of the show to regenerate')
async def regenerate_show_cmd(interaction: discord.Interaction, script_id: str):
    user = script_builder_utils.build_user(ext_id=interaction.user.global_name, source=ext_user_source_pb2.EXT_USER_SOURCE_DISCORD)
    regen_request = script_service_pb2.GenerateScriptRequest(id=script_id, requesting_user=user)
    try:
        async with grpc.aio.insecure_channel(
            configuration["service"]["path"]
        ) as grpc_channel:
            service = script_service_pb2_grpc.ScriptServiceStub(grpc_channel)
            await service.GenerateScript(request=regen_request)
    except Exception as e:
        logger.exception(e)
    await interaction.response.send_message(f'Regenerating {script_id}', ephemeral=True)

async def send_status_message(message: str):
    for channel_id in configuration["discord"]["broadcast_channels"]:
        channel = bot.get_channel(channel_id)
        await channel.send(message)
