# -*- coding: utf-8 -*-

import json
import logging
import sys

from openai import OpenAI

# 配置日志系统
logger = logging.getLogger('word_helper')
logger.setLevel(logging.INFO)

# 检查是否已经有处理器，如果没有才添加
if not logger.handlers:
    # 文件处理器
    file_handler = logging.FileHandler('../log/word_requests.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

# 单词缓存
words_cache = {}


def get_word_meaning(word):
    """获取单词的中文释义，优先使用缓存，如果缓存中没有则请求 API"""

    if word in words_cache:
        logger.info(f"Cache hit for word: {word}")
        return words_cache[word]

    try:
        import os
        client = OpenAI(api_key=os.environ.get('DeepSeek_AI', ''), base_url="https://api.deepseek.com")

        with open("prompts/default.md", "r", encoding="utf-8") as f:
            system_prompt = f.read()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": word},
        ]

        logger.info(f"Requesting meaning for word: {word}")
        logger.info(f"Request content: {json.dumps(messages, ensure_ascii=False)}")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False,
        )

        meaning = response.choices[0].message.content
        words_cache[word] = meaning

        logger.info(f"Response for word '{word}': {meaning}")
        return meaning

    except Exception as e:
        logger.error(f"Error getting meaning for word '{word}': {e}")
        return f"获取释义出错：{e}"
