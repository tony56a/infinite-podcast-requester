import random
import uuid

from enums.v1 import (
    ext_user_source_pb2,
    script_type_pb2,
    character_type_pb2,
)
from models.v1 import script_pb2, user_pb2, script_guest_character_pb2
from services.v1 import script_service_pb2
from google.protobuf import wrappers_pb2

def build_user(ext_id, source):
    return user_pb2.User(
        ext_id=ext_id,
        user_source=source,
    )


def build_character(name=None, character_type=None, speaker_voice_type=None):
    if name is not None:
        name = wrappers_pb2.StringValue(name)
    return script_guest_character_pb2.ScriptGuestCharacter(
        name=name, character_type=character_type, speaker_voice_type=speaker_voice_type
    )

def build_script_request(
    topic,
    user=None,
    guest_character=None,
    script_type=script_type_pb2.ScriptType.SCRIPT_TYPE_PODCAST,
):
    if user is None:
        user = user_pb2.User(
            ext_id="admin",
            user_source=ext_user_source_pb2.EXT_USER_SOURCE_AUTOMATION,
        )
    if guest_character is None:
        guest_character = build_character()
    script = script_pb2.Script(
        request_id=str(uuid.uuid4()),
        requesting_user=user,
        characters=[guest_character],
        script_type=script_type,
        topic=topic,
    )
    return script_service_pb2.CreateScriptRequest(script=script)

def build_random_script():
    character_types = [
        character_type_pb2.CharacterType.CHARACTER_TYPE_NORMAL,
        character_type_pb2.CharacterType.CHARACTER_TYPE_ROBOT,
        character_type_pb2.CharacterType.CHARACTER_TYPE_SKELETON,
    ]
    topic = [
        "A toally random and absurd podcast topic",
        "A totally normal and ordinary podcast topic",
        "A spooky and dark topic, but with a humurous viewpoint",
    ]
    return build_script_request(
        topic=random.choice(topic),
        guest_character=build_character(character_type=random.choice(character_types)),
    )

