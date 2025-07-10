# backend/worker/app/graph/tools.py

# このファイルは、将来的にLLMが直接呼び出すツールを定義するために予約されています。
# (例: 天気予報APIを呼び出すツール、電卓ツールなど)
# 今回のアーキテクチャでは必須ではありません。

def example_tool(query: str) -> str:
    """
    これはツールの例です。
    """
    return f"'{query}'に対するツールの実行結果です。"

