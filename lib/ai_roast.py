"""
使用 GitHub Models API (GPT-4o-mini) 產生 ≤7 字的嘴砲回覆。
當使用者拒絕抽籤結果時，AI 會回嘴。
"""

import os
import random
from openai import OpenAI

# 離線備用句（API 失敗時使用）
FALLBACK_ROASTS = [
    "吃土啦",
    "那就餓著吧",
    "自己煮啦",
    "喝西北風啊",
    "吃空氣好了",
    "餓死算了",
    "太挑了吧",
    "嘴那麼刁喔",
    "有本事別吃",
    "隨便你啦",
]

SYSTEM_PROMPT = (
    "你是一個毒舌的美食助手。使用者一直拒絕餐廳推薦，你要用嘲諷、搞笑的語氣回嘴。"
    "規則：\n"
    "1. 回覆必須是繁體中文\n"
    "2. 最多7個字，不能超過\n"
    "3. 不要加標點符號\n"
    "4. 語氣要像朋友之間的吐槽，不要太惡毒\n"
    "5. 每次回覆都不一樣，要有創意\n"
    "範例回覆: 吃土啦、自己煮啦、那就餓著吧、喝西北風啊、太挑了吧、嘴那麼刁喔"
)


def get_roast(reject_count: int = 1) -> str:
    """
    呼叫 GitHub Models API 取得嘴砲回覆。

    Args:
        reject_count: 使用者已拒絕的次數（可用於調整語氣強度）

    Returns:
        ≤7 字的嘴砲字串
    """
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return random.choice(FALLBACK_ROASTS)

    try:
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=token,
        )

        user_msg = f"使用者已經拒絕了{reject_count}次推薦，給一句嘴砲回覆，不要帶標點。"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=1.0,
            max_tokens=30,
        )

        reply = response.choices[0].message.content.strip()

        # 安全清淨化：移除 HTML 危險字符
        for char in ["<", ">", '"', "'", "\\", "/", "&"]:
            reply = reply.replace(char, "")

        # 移除標點符號
        for char in ["。", "！", "!", "，", ",", "？", "?", "；", ";"]:
            reply = reply.replace(char, "")

        reply = reply.strip()

        # 如果超過7個字或為空，使用備用句
        if len(reply) > 7 or len(reply) == 0:
            return random.choice(FALLBACK_ROASTS)

        return reply

    except Exception as e:
        print(f"⚠ AI 嘴砲 API 失敗: {e}，使用備用句")
        return random.choice(FALLBACK_ROASTS)
