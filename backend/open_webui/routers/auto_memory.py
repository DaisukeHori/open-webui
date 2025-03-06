import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel

from open_webui.models.memories import Memories, MemoryModel, AutoMemorySettings
from open_webui.models.fact_extractor import Fact
# 循環インポートを避けるため、facts_processorへの直接参照をコメントアウト
# 必要なときに動的にインポートする
from open_webui.routers.auths import get_current_user, get_current_admin

router = APIRouter(prefix="/api/v1/auto-memory", tags=["auto-memory"])
logger = logging.getLogger(__name__)

class MessageContent(BaseModel):
    content: str

class FactResponse(BaseModel):
    fact: str
    confidence: float
    
class FactExtractionResponse(BaseModel):
    facts: List[FactResponse]


# 自動メモリ抽出設定のエンドポイント
@router.get("/settings")
async def get_auto_memory_settings(current_user = Depends(get_current_user)):
    """ユーザーの自動メモリ抽出設定を取得する"""
    try:
        user_id = current_user.id
        from open_webui.socket.facts_processor import facts_processor
        settings = facts_processor.get_user_settings(user_id)
        return {"enabled": settings.enabled, "min_confidence": settings.min_confidence}
    except Exception as e:
        logger.error(f"Error getting auto memory settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting auto memory settings: {str(e)}")

@router.post("/settings")
async def update_auto_memory_settings(
    settings: AutoMemorySettings, 
    current_user = Depends(get_current_user)
):
    """ユーザーの自動メモリ抽出設定を更新する"""
    try:
        user_id = current_user.id
        from open_webui.socket.facts_processor import facts_processor
        await facts_processor.update_user_settings(user_id, settings)
        return {"status": "success", "message": "Settings updated successfully"}
    except Exception as e:
        logger.error(f"Error updating auto memory settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating auto memory settings: {str(e)}")


# メモリの操作エンドポイント
@router.get("")
async def get_memories(current_user = Depends(get_current_user)):
    """ユーザーのメモリ一覧を取得する"""
    try:
        user_id = current_user.id
        memories = Memories.get_memories_by_user_id(user_id)
        if memories is None:
            memories = []
        
        # フロントエンド用にフォーマット
        formatted_memories = [
            {
                "id": memory.id,
                "user_id": memory.user_id,
                "fact": memory.content,
                "created_at": memory.created_at,
                "updated_at": memory.updated_at
            }
            for memory in memories
        ]
        
        return {"memories": formatted_memories}
    except Exception as e:
        logger.error(f"Error getting memories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting memories: {str(e)}")

@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, current_user = Depends(get_current_user)):
    """特定のメモリを削除する"""
    try:
        user_id = current_user.id
        success = Memories.delete_memory_by_id_and_user_id(memory_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
            
        return {"status": "success", "message": "Memory deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting memory: {str(e)}")

@router.post("/manual-extract")
async def manual_extract_facts(
    message: MessageContent,
    current_user = Depends(get_current_user)
):
    """テキストから手動で事実を抽出する"""
    try:
        user_id = current_user.id
        from open_webui.socket.facts_processor import facts_processor
        facts = await facts_processor.manual_extract_facts(
            user_id=user_id,
            content=message.content,
            min_confidence=0.0  # 手動抽出では確信度にかかわらずすべての事実を返す
        )
        
        response_facts = [
            FactResponse(fact=fact.content, confidence=fact.confidence)
            for fact in facts
        ]
        
        return FactExtractionResponse(facts=response_facts)
    except Exception as e:
        logger.error(f"Error manually extracting facts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error manually extracting facts: {str(e)}")