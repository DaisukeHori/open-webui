import json
import logging
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

# LLMクライアントとの連携
from open_webui.utils.completion import get_llm_completion

logger = logging.getLogger(__name__)

class Fact(BaseModel):
    """抽出された事実"""
    content: str
    confidence: float = Field(ge=0.0, le=1.0)

class FactExtractor:
    """ユーザーメッセージから事実を抽出するクラス"""
    
    # 事実抽出のためのシステムプロンプト
    SYSTEM_PROMPT = """あなたはメッセージからユーザーに関する事実を抽出する専門家です。
以下のルールに従ってください：

1. ユーザーのメッセージから、彼/彼女に関する具体的な事実を抽出してください
2. 名前、好み、嗜好、仕事、家族、趣味など個人的な情報に焦点を当ててください
3. 抽出した各事実に0.0〜1.0の信頼度スコアを付けてください（1.0が最も確実）
4. 明示的に述べられている事実は信頼度が高くなります
5. 暗示的または不確かな事実は信頼度が低くなります
6. 事実は簡潔で具体的な文として表現してください
7. 回答は必ずJSON形式で返してください
8. 事実がない場合は空のリストを返してください

出力形式:
{
  "facts": [
    {"fact": "事実1", "confidence": 0.9},
    {"fact": "事実2", "confidence": 0.7},
    ...
  ]
}"""

    def __init__(self, model_id: str = "gpt-3.5-turbo"):
        """
        Args:
            model_id: 使用するLLMのモデルID
        """
        self.model_id = model_id

    async def extract_facts(self, message_content: str) -> List[Fact]:
        """ユーザーメッセージから事実を抽出する
        
        Args:
            message_content: 解析するメッセージの内容
            
        Returns:
            抽出された事実のリスト
        """
        try:
            # LLMに事実抽出のリクエストを送信
            response = await get_llm_completion(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": message_content}
                ],
                temperature=0.1,  # 低い温度で決定論的な回答を得る
                max_tokens=1000,
            )
            
            # レスポンスからコンテンツを取得
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # JSONを抽出して解析
            try:
                # JSONが直接返されるケース
                facts_data = json.loads(content)
                facts = []
                
                for fact_item in facts_data.get("facts", []):
                    facts.append(
                        Fact(
                            content=fact_item.get("fact", ""),
                            confidence=fact_item.get("confidence", 0.0)
                        )
                    )
                return facts
                
            except json.JSONDecodeError:
                # JSONが直接返されない場合、コンテンツからJSONを抽出
                json_start = content.find("{")
                json_end = content.rfind("}")
                
                if json_start >= 0 and json_end >= 0:
                    json_str = content[json_start:json_end+1]
                    facts_data = json.loads(json_str)
                    
                    facts = []
                    for fact_item in facts_data.get("facts", []):
                        facts.append(
                            Fact(
                                content=fact_item.get("fact", ""),
                                confidence=fact_item.get("confidence", 0.0)
                            )
                        )
                    return facts
                
                logger.warning(f"Failed to extract JSON from LLM response: {content}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting facts: {str(e)}")
            return []

# シングルトンインスタンス
fact_extractor = FactExtractor()