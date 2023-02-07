from graia.ariadne.app import Ariadne
from graia.ariadne.model import Friend, Group
from graia.ariadne.message import Source
from typing import Union, Any, Dict, Tuple
from config import Config
from loguru import logger
import asyncio
from charapi import CharacterBot
import atexit


config = Config.load_config()

class ChatSession:
    def __init__(self, charId=config.characters.default_character_id):
        self.ai = CharacterBot(charId)
        
    def reset_conversation(self):
        del self.ai
        self.__init__()

    def load_conversation(self, keyword='default'):
        if not keyword in config.characters.keywords:
            if keyword == 'default':
                self.__init__()
            else:
                raise ValueError("预设不存在，请检查你的输入是否有问题！")
        else:
            self.__init__(config.characters.keywords[keyword])

        try:
            return self.ai.get_initial_message()
        except:
            return config.characters.loaded_successful

    async def get_chat_response(self, message) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.ai.send_message, message)

__sessions = {}

def get_chat_session(id: str) -> ChatSession:
    if id not in __sessions:
        __sessions[id] = ChatSession()
    return __sessions[id]

def exit_handler():
    logger.info("正在清理浏览器会话……")
    for k, v in __sessions.items():
        try:
            del v.ai
        except:
            pass

atexit.register(exit_handler)