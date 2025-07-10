# backend/shared/state.py

from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    LangGraphの各ノード間で受け渡される状態を定義するクラス。
    """
    user_input: str
    # これまでの会話履歴（短期記憶＋長期記憶）
    messages: Annotated[list, lambda x, y: x + y]
    # RAGで取得した知識文書
    knowledge_docs: List[str]
    # LLMが生成した最終的な応答
    llm_response: str
