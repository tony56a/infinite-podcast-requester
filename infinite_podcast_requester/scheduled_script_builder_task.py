import asyncio
import grpc
import logging
import redis

from config import configuration
from enums.v1 import (
    ext_user_source_pb2,
    script_type_pb2,
    character_type_pb2,
    speaker_voice_type_pb2,
)
from services.v1 import script_service_pb2_grpc
from script_builder_utils import build_random_script

logger = logging.getLogger()

async def my_function(redis_client):
    # Start periodic script generation
    while True:
        count = redis_client.get_length(redis_client.script_queue)

        if count < 30:
            script_request = build_random_script()
            logger.info(
                f"adding script request topic={script_request.script.topic} " + 
                    f"character_type={character_type_pb2.CharacterType.Name(script_request.script.characters[0].character_type)}",
            )
            try:
                async with grpc.aio.insecure_channel(
                    configuration["service"]["path"]
                ) as grpc_channel:
                    service = script_service_pb2_grpc.ScriptServiceStub(grpc_channel)
                    await service.CreateScript(request=script_request)
            except Exception as e:
                logger.exception(e)
        else:
            logger.info("skipping automated request")

        await asyncio.sleep(30)