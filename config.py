from __future__ import annotations
from typing import List, Union, Literal
from pydantic import BaseModel, BaseConfig, Extra, Field
from charset_normalizer import from_bytes
from loguru import logger
import sys
import toml


class Mirai(BaseModel):
    qq: int
    """Bot 的 QQ 号"""
    api_key: str
    """mirai-api-http 的 verifyKey"""
    http_url: str = "http://localhost:8080"
    """mirai-api-http 的 http 适配器地址"""
    ws_url: str = "http://localhost:8080"
    """mirai-api-http 的 ws 适配器地址"""

class TextToImage(BaseModel):
    font_size: int = 30
    """字号"""
    width: int = 700
    """生成图片宽度"""
    font_path: str = "fonts/sarasa-mono-sc-regular.ttf"
    """字体路径"""
    offset_x: int = 50
    """横坐标"""
    offset_y: int = 50
    """纵坐标"""


class Trigger(BaseModel):
    prefix: List[str] = [""]
    """触发响应的前缀，默认不需要"""
    require_mention: Literal["at", "mention", "none"] = "at"
    """群内 [需要 @ 机器人 / 需要 @ 或以机器人名称开头 / 不需要 @] 才响应（请注意需要先 @ 机器人后接前缀）"""
    reset_command: List[str] = ["重置会话"]
    """重置会话的命令"""
    rollback_command: List[str] = ["回滚会话"]
    """回滚会话的命令"""


class Response(BaseModel):
    placeholder: str = (
        "您好！我是 Assistant，一个由 OpenAI 训练的大型语言模型。我不是真正的人，而是一个计算机程序，可以通过文本聊天来帮助您解决问题。如果您有任何问题，请随时告诉我，我将尽力回答。\n"
        "如果您需要重置我们的会话，请回复`重置会话`。"
    )
    """对空消息回复的占位符"""

    reset = "会话已重置。"
    """重置会话时发送的消息"""

    error_format: str = (
        "出现故障！如果这个问题持续出现，请和我说“重置会话” 来开启一段新的会话，或者发送 “回滚对话” 来回溯到上一条对话，你上一条说的我就当作没看见。"
        "\n{exc}"
    )
    """发生错误时发送的消息，请注意可以插入 {exc} 作为异常占位符"""

    quote: bool = True
    """是否回复触发的那条消息"""
    
    timeout: float = 30.0
    """发送提醒前允许的响应时间"""

    timeout_format: str = "我还在思考中，请再等一下~"
    """响应时间过长时要发送的提醒"""

class System(BaseModel):
    accept_group_invite: bool = False
    """自动接收邀请入群请求"""

    accept_friend_request: bool = False
    """自动接收好友请求"""

class Characters(BaseModel):
    command: str = r"加载角色 (\w+)"
    """加载角色的指令，使用正则表达式匹配。默认为 加载角色 角色名"""

    default_character_id: str = "imCTKnpaPqOs-w6QdvStdPLm15UZ7QdBImd8uo4ylw4"
    """默认使用的角色 ID"""

    keywords: dict[str, str] = {
        "拜登": "Vb8Efxa3nNAmL1xYgmYjYOnVVAT9ztTkYDQCeQjKR50",
        "丁真": "f4z5XLwZuK_txuvCd8SLuzN4veppXT0bE65kdWicZ1s",
        "杠精": "imCTKnpaPqOs-w6QdvStdPLm15UZ7QdBImd8uo4ylw4",
        "角色扮演-勇者": "q0Vd_OrT1UoDbw2SQ0MfmMomoBbxAk9ZPorsAv3j9TA"
    }
    """角色对应的 ID"""

    loaded_successful: str = "角色加载成功！"
    """加载成功的提示"""

class Config(BaseModel):
    mirai: Mirai
    text_to_image: TextToImage = TextToImage()
    trigger: Trigger = Trigger()
    response: Response = Response()
    system: System = System()
    characters: Characters = Characters()

    @staticmethod
    def load_config() -> Config:
        try:
            with open("config.cfg", "rb") as f:
                guessed_str = from_bytes(f.read()).best()
                if not guessed_str:
                    raise ValueError("无法识别 TOML 格式！")
                
                return Config.parse_obj(toml.loads(str(guessed_str)))
        except Exception as e:
            logger.exception(e)
            logger.error("配置文件有误，请重新修改！")
            exit(-1)

    @staticmethod
    def save_config(config: Config) -> Config:
        try:
            with open("config.cfg", "rb") as f:
                guessed_str = from_bytes(f.read()).best()
            with open("config.cfg", "wb") as f:
                logger.debug(f"配置文件编码 {guessed_str.encoding}")
                parsed_json = toml.dumps(config.dict()).encode(sys.getdefaultencoding())
                f.write(parsed_json)
        except Exception as e:
                logger.exception(e)
                logger.warning("配置保存失败。")
