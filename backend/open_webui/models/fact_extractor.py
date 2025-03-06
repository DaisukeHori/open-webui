import json
import logging
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

# LLMクライアントとの連携
from open_webui.utils.completion import get_llm_completion

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 

class Fact(BaseModel):
    """抽出された事実"""
    content: str
    confidence: float = Field(ge=0.0, le=1.0)

class FactExtractor:
    """ユーザーメッセージから事実を抽出するクラス"""
    
    # 事実抽出のためのシステムプロンプト
    SYSTEM_PROMPT = """あなたはメッセージからユーザーに関する事実を高精度で抽出する専門家です。
以下のルールに従ってください：

1. ユーザーが「私」「僕」「俺」などの一人称で述べている場合、そこから個人情報を積極的に抽出してください
2. 抽出すべき情報カテゴリ：
   - 名前、年齢、性別、住所
   - 職業、勤務先、職位、専門分野
   - 家族構成（配偶者、子供、親など）
   - 趣味、好きな食べ物、嫌いなもの
   - 所有物（車、ペット、住居など）
   - 習慣、ルーティンなど

3. 信頼度スコアのガイドライン：
   - 1.0: 明示的に「私の名前は太郎です」「私は東京に住んでいます」などと述べられている
   - 0.9: 強く示唆されている「太郎と申します」「東京から来ました」
   - 0.7-0.8: 文脈から明らかな事実「この前、会社の上司と...」（会社員である）
   - 0.5-0.6: ある程度確実な推測「子供の学校の送り迎え」（子供がいる）
   - 0.4以下: 不確かな推測は避ける

4. 事実は「ユーザーは〜」または「〜である」という形で簡潔に記述してください
5. 回答は必ずJSON形式で返してください
6. 確実な事実が見つからない場合は空のリストを返してください

出力形式:
{
  "facts": [
    {"fact": "ユーザーの名前は田中太郎である", "confidence": 0.95},
    {"fact": "ユーザーは東京に住んでいる", "confidence": 0.90},
    ...
  ]
}"""

    def __init__(self, model_id: str = "gpt-4o"):
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
        # 詳細なデバッグ情報: 入力メッセージの完全な内容を記録
        print(f"[Fact Extractor] DEBUG: Full input message: '{message_content}'")
        print(f"[Fact Extractor] DEBUG: Input message length: {len(message_content)} chars")
        print(f"[Fact Extractor] DEBUG: Input message byte size: {len(message_content.encode('utf-8'))} bytes")
        try:
            print(f"[Fact Extractor] Extracting facts from message: '{message_content[:50]}...'")
            # LLMに事実抽出のリクエストを送信
            print(f"[Fact Extractor] DEBUG: Using model: {self.model_id}")
            print(f"[Fact Extractor] DEBUG: Sending request to LLM with system prompt: '{self.SYSTEM_PROMPT[:100]}...'")
            response = await get_llm_completion(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": message_content}
                ],
                temperature=0.0,  # 完全に決定論的な回答を得る
                max_tokens=1000,
            )
            
            print(f"[Fact Extractor] DEBUG: Raw response structure: {response.keys()}")
            
            # レスポンスからコンテンツを取得
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"[Fact Extractor] DEBUG: Full raw LLM response: '{content}'")
            print(f"[Fact Extractor] DEBUG: Response length: {len(content)} chars")
            
            # JSONを抽出して解析
            try:
                # JSONが直接返されるケース
                print("[Fact Extractor] Attempting to parse direct JSON response")
                facts_data = json.loads(content)
                print(f"[Fact Extractor] DEBUG: Parsed JSON data: {facts_data}")
                facts = []
                
                for fact_item in facts_data.get("facts", []):
                    fact_content = fact_item.get("fact", "")
                    confidence = fact_item.get("confidence", 0.0)
                    print(f"[Fact Extractor] Extracted fact: '{fact_content}' with confidence {confidence}")
                    # 名前に関する事実かどうかを確認
                    name_related = any(keyword in fact_content.lower() for keyword in ["名前", "name", "なまえ"])
                    if name_related:
                        print(f"[Fact Extractor] DEBUG: Detected name-related fact: '{fact_content}'")
                    facts.append(
                        Fact(
                            content=fact_content,
                            confidence=confidence
                        )
                    )
                print(f"[Fact Extractor] Successfully extracted {len(facts)} facts")
                print(f"[Fact Extractor] DEBUG: All extracted facts: {[f.content for f in facts]}")
                return facts
                
            except json.JSONDecodeError:
                print(f"[Fact Extractor] DEBUG: JSON decode error, attempting to extract JSON from text")
                # JSONが直接返されない場合、コンテンツからJSONを抽出
                json_start = content.find("{")
                json_end = content.rfind("}")
                
                print(f"[Fact Extractor] Direct JSON parsing failed, attempting to extract JSON from content")
                if json_start >= 0 and json_end >= 0:
                    json_str = content[json_start:json_end+1]
                    print(f"[Fact Extractor] DEBUG: Extracted JSON string: '{json_str}'")
                    facts_data = json.loads(json_str)
                    print(f"[Fact Extractor] DEBUG: Parsed JSON data from extraction: {facts_data}")
                    facts = []
                    print(f"[Fact Extractor] Found JSON object in content between positions {json_start} and {json_end}")
                    for fact_item in facts_data.get("facts", []):
                        fact_content = fact_item.get("fact", "")
                        confidence = fact_item.get("confidence", 0.0)
                        print(f"[Fact Extractor] Extracted fact from embedded JSON: '{fact_content}' with confidence {confidence}")
                        # 名前に関する事実かどうかを確認
                        name_related = any(keyword in fact_content.lower() for keyword in ["名前", "name", "なまえ"])
                        if name_related:
                            print(f"[Fact Extractor] DEBUG: Detected name-related fact from JSON extraction: '{fact_content}'")
                        facts.append(
                            Fact(
                                content=fact_content,
                                confidence=confidence
                            )
                        )
                    print(f"[Fact Extractor] Extracted {len(facts)} facts from embedded JSON")
                    print(f"[Fact Extractor] DEBUG: All extracted facts from embedded JSON: {[f.content for f in facts]}")
                    return facts
                
                print(f"[Fact Extractor] WARNING: Failed to extract JSON from LLM response: '{content[:100]}...'")
                print(f"[Fact Extractor] DEBUG: No valid JSON could be extracted, returning empty facts list")
                return []
                
        except Exception as e:
            print(f"[Fact Extractor] ERROR extracting facts: {str(e)}")
            import traceback
            print(f"[Fact Extractor] DEBUG: Exception traceback: {traceback.format_exc()}")
            return []

# シングルトンインスタンス
fact_extractor = FactExtractor()
