import logging
import asyncio
from typing import Dict, Any, Optional, List

from open_webui.models.fact_extractor import fact_extractor, Fact
from open_webui.models.memories import Memories, AutoMemorySettings

logger = logging.getLogger(__name__)

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
            self._user_settings[user_id] = AutoMemorySettings(enabled=False, min_confidence=0.7)
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
            user_id = message.get("user_id")
            content = message.get("content")
            message_id = message.get("id")
            
            # 必要な情報がない場合は処理しない
            if not all([user_id, content]):
                return []
                
            # ユーザーの設定を取得
            settings = self.get_user_settings(user_id)
            
            # 自動抽出が無効な場合は処理しない
            if not settings.enabled:
                return []
                
            # 事実を抽出
            facts = await fact_extractor.extract_facts(content)

            if facts:
                # 抽出された事実をメモリに保存
                await self._save_facts(user_id, facts, settings.min_confidence, message_id)
                
            return facts
            
        except Exception as e:
            logger.error(f"Error processing message for facts: {str(e)}")
            return []
            
    def _save_facts(
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
        try:
            facts_to_save = [fact for fact in facts if fact.confidence >= min_confidence]
            
            for fact in facts_to_save:
                Memories.insert_new_memory(
                    user_id=user_id,
                    content=fact.content
                )
                
            if facts_to_save:
                logger.info(f"Saved {len(facts_to_save)} facts for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error saving facts to database: {str(e)}")
            
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