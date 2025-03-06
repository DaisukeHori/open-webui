import logging
import json
from typing import Dict, List, Any, Optional

from open_webui.models.models import Models
# from open_webui.utils.models import get_all_models  # 循環インポートを修正するためコメントアウト
from open_webui.utils.chat import generate_chat_completion
from open_webui.env import OPENAI_API_KEY

logger = logging.getLogger(__name__)

async def get_llm_completion(
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
) -> Dict[str, Any]:
    """
    LLMから補完/チャット完了を取得する汎用関数
    
    Args:
        model: 使用するモデルID
        messages: チャットメッセージの配列
        temperature: 応答の創造性の度合い (0.0-1.0)
        max_tokens: 生成するトークンの最大数
        top_p: nucleus sampling用のパラメータ
        frequency_penalty: 単語の繰り返しを減らすペナルティ
        presence_penalty: 新しいトピックの導入を促すペナルティ
        
    Returns:
        LLMからのレスポンス
    """
    try:
        # リクエストの形成
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        # オプションパラメータの追加
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
            
        # モデルに応じてAPIを選択
        if "gpt" in model.lower() or model.startswith("openai/"):
            # OpenAI APIを使用
            return await _openai_completion(payload)
        elif model.startswith("ollama/") or any(model_prefix in model.lower() for model_prefix in ["llama", "mistral", "phi"]):
            # Ollama APIを使用
            return await _ollama_completion(payload)
        else:
            # デフォルトはOpenAI API
            return await _openai_completion(payload)
            
    except Exception as e:
        logger.error(f"Error getting LLM completion: {str(e)}")
        # エラー時は空のレスポンスを返す
        return {
            "choices": [
                {
                    "message": {
                        "content": f"エラーが発生しました: {str(e)}"
                    }
                }
            ]
        }

async def _openai_completion(payload: Dict[str, Any]) -> Dict[str, Any]:
    """OpenAI APIを使用した補完"""
    import httpx
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            raise Exception(f"OpenAI API error: {response.status_code}")

async def _ollama_completion(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Ollama APIを使用した補完"""
    import httpx
    
    # OllamaのAPIフォーマットに変換
    ollama_payload = {
        "model": payload["model"].replace("ollama/", ""),
        "prompt": payload["messages"][-1]["content"],
        "system": next((msg["content"] for msg in payload["messages"] if msg["role"] == "system"), ""),
        "options": {
            "temperature": payload.get("temperature", 0.7)
        }
    }
    
    if "max_tokens" in payload:
        ollama_payload["options"]["num_predict"] = payload["max_tokens"]
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json=ollama_payload,
            timeout=60.0
        )
        
        if response.status_code == 200:
            # Ollamaレスポンスを標準形式に変換
            resp_json = response.json()
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": resp_json.get("response", "")
                        }
                    }
                ]
            }
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            raise Exception(f"Ollama API error: {response.status_code}")