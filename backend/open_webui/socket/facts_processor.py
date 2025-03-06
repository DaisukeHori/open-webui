import logging
import asyncio
from typing import Dict, Any, Optional, List

from open_webui.models.fact_extractor import fact_extractor, Fact
from open_webui.models.memories import Memories, AutoMemorySettings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class FactsProcessor:
    """
    WebSocketを通じてリアルタイムでメッセージを監視し、
    ユーザーに関する事実を抽出して保存するクラス
    """
    
    def __init__(self):
        # ユーザーIDごとの設定を保持
        self._user_settings: Dict[str, AutoMemorySettings] = {}
        
    def get_user_settings(self, user_id: str) -> AutoMemorySettings:
        """ユーザーの自動メモリ抽出設定を取得する"""
        if user_id not in self._user_settings:
            # デフォルト設定
            self._user_settings[user_id] = AutoMemorySettings(enabled=True, min_confidence=0.7)
        return self._user_settings[user_id]
    
    async def update_user_settings(self, user_id: str, settings: AutoMemorySettings) -> None:
        """ユーザーの自動メモリ抽出設定を更新する"""
        self._user_settings[user_id] = settings
    
    async def process_message(self, message: Dict[str, Any]) -> List[Fact]:
        """
        メッセージを処理し、もし対象であれば事実を抽出する
        
        Args:
            message: WebSocketから受け取ったメッセージオブジェクト
            
        Returns:
            抽出された事実のリスト
        """
        try:
            # メッセージからユーザーIDと内容を取得
            print(f"[Auto Memory] Processing message: {message.get('id')}")
            user_id = message.get("user_id")
            content = message.get("content")
            message_id = message.get("id")
            
            # 必要な情報がない場合は処理しない
            if not all([user_id, content]):
                print(f"[Auto Memory] Skipping message due to missing information: {message}")
                return []
                
            # ユーザーの設定を取得
            settings = self.get_user_settings(user_id)
            print(f"[Auto Memory] User {user_id} settings: enabled={settings.enabled}, min_confidence={settings.min_confidence}")
            
            # 自動抽出が無効な場合は処理しない
            if not settings.enabled:
                print(f"[Auto Memory] Automatic fact extraction disabled for user {user_id}")
                return []
                
            print(f"[Auto Memory] Extracting facts from message content: {content[:50]}...")
            facts = await fact_extractor.extract_facts(content)

            if facts:
                # 抽出された事実をメモリに保存
                await self._save_facts(user_id, facts, settings.min_confidence, message_id)
                
            return facts
            
        except Exception as e:
            print(f"[Auto Memory] ERROR processing message for facts: {str(e)}")
            return []
            
    async def _save_facts(
        self, 
        user_id: str, 
        facts: List[Fact],
        min_confidence: float,
        message_id: Optional[str] = None
    ) -> None:
        """
        抽出された事実をデータベースに保存する
        
        Args:
            user_id: ユーザーID
            facts: 抽出された事実のリスト
            min_confidence: 保存する最小確信度
            message_id: ソースとなったメッセージID
        """
        facts_to_save = []
        try:
            print(f"[Auto Memory] Processing {len(facts)} extracted facts for user {user_id}")
            # 確信度が閾値以上の事実をフィルタリング
            filtered_facts = [fact for fact in facts if fact.confidence >= min_confidence]
            print(f"[Auto Memory] {len(filtered_facts)}/{len(facts)} facts passed the confidence threshold of {min_confidence}")
            
            # メモリに保存
            for i, fact in enumerate(filtered_facts):
                print(f"[Auto Memory] Saving fact {i+1}/{len(filtered_facts)}: '{fact.content}' (confidence: {fact.confidence})")
                memory = Memories.insert_new_memory(
                    user_id=user_id,
                    content=f"{fact.content} (確信度: {fact.confidence})"
                )
                if memory:
                    facts_to_save.append(memory)
                
            logger.info(f"Saved {len(facts_to_save)} facts for user {user_id} from message {message_id}")
        except Exception as e:
            logger.error(f"Error saving facts to database: {str(e)} for user {user_id}")
            
    async def manual_extract_facts(self, user_id: str, content: str, min_confidence: float = 0.5) -> List[Fact]:
        """
        指定されたテキストから手動で事実を抽出する
        
        Args:
            user_id: ユーザーID
            content: 分析するテキスト
            min_confidence: 返す事実の最小確信度
            
        Returns:
            抽出された事実のリスト
        """
        try:
            facts = await fact_extractor.extract_facts(content)
            filtered_facts = [fact for fact in facts if fact.confidence >= min_confidence]
            return filtered_facts
        
        except Exception as e:
            logger.error(f"Error manually extracting facts: {str(e)}")
            return []

# シングルトンインスタンス
facts_processor = FactsProcessor()