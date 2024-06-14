import re
import json
import time
from os import getenv

import google.generativeai as genai

from utils.logging_handler import get_logger

logger = get_logger(__name__)
JSON_FORMAT = re.compile(r"\{.*\}")
JSON_CLEANUP = re.compile(r"\n|\t|\r")

class Gemini:
    call_datetimes = {}

    def __init__(self) -> None:
        g_key = getenv('GEMINI_KEY')
        if not g_key:
            raise EnvironmentError("Missing GEMINI_KEY env")
        genai.configure(api_key=g_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def text_request(self, text: str) -> str | None:
        try:
            response = self.model.generate_content(text, generation_config={'temperature': 0.9})
            Gemini.update_counter(response.usage_metadata.total_token_count)
            return response.text
        except Exception as e:
            logger.error("Gemini error: %s", e)

    def json_request(self, text: str) -> str | None:
        context = "ONLY RESPONSE TO THIS WITH A JSON COMPATIBLE STRING, WITHOUT ANY CONTEXT TEXT:"
        try:
            response = self.model.generate_content(context + text, generation_config={'temperature': 0.9})
            Gemini.update_counter(response.usage_metadata.total_token_count)
            return json.loads(JSON_FORMAT.findall(JSON_CLEANUP.sub('',response.text))[0])
        except (json.JSONDecodeError, IndexError):
            logger.error("Gemini bad JSON")
        except Exception as e:
            logger.error("Gemini error: %s", e)

    @classmethod
    def update_counter(cls, tokens: int) -> None:
        actual_time = time.time()
        cls.call_datetimes[actual_time] = tokens
        cls.call_datetimes = {k: v for k, v in Gemini.call_datetimes.items() if (actual_time - k) < 60}
        logger.info("Minute tokens: %s  -  Minute requests: %s", sum(cls.call_datetimes.values()), len(cls.call_datetimes))
