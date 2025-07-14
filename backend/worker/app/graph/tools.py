# backend/worker/app/graph/tools.py

import json
import os
from datetime import datetime
from typing import List, Dict, Any

# Workerコンテナのルートから見たknowledgeディレクトリの相対パス
# Dockerコンテナ内での実行を想定しています。
APP_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KNOWLEDGE_BASE_PATH = os.path.join(APP_ROOT_PATH, "data", "knowledge")

# --- Step 1: コンテキスト判断 (Contextualizer) で使用 ---
def get_event_context() -> str:
    """
    イベントの開催日を基準に、現在の状況を判断します。
    これが思考パイプラインの最初のステップとなります。

    Returns:
        str: "BEFORE_EVENT", "DURING_EVENT", "AFTER_EVENT" のいずれか。
    """
    try:
        config_path = os.path.join(KNOWLEDGE_BASE_PATH, "00_イベント概要", "event_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        event_date_str = config["eventDate"]
    except (FileNotFoundError, KeyError):
        # 設定ファイルがない場合は、常に「イベント前」として扱うなど、
        # フォールバックの挙動を定義できます。
        return "CONTEXT_ERROR"

    event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
    today = datetime.now().date()

    if today < event_date:
        return "BEFORE_EVENT"
    elif today == event_date:
        return "DURING_EVENT"
    else:
        return "AFTER_EVENT"

# --- Step 3: 条件付き情報拡充 (Conditional Augmentation) で使用 ---
def get_current_schedule_info(timetable_path: str) -> str:
    """
    指定されたタイムテーブルファイルのパスを元に、現在と次のイベント情報を生成します。
    この関数は「イベント当日」にのみ呼び出されます。

    Args:
        timetable_path (str): 読み込むべきタイムテーブルJSONファイルのフルパス。

    Returns:
        str: 現在のスケジュール状況を説明する文字列。
    """
    try:
        with open(timetable_path, "r", encoding="utf-8") as f:
            schedule = json.load(f)
    except FileNotFoundError:
        return "" # ファイルが見つからない場合は空文字を返し、後続の処理に影響を与えない

    now = datetime.now().time()
    current_event = None
    next_event = None

    for event in sorted(schedule, key=lambda x: x["start_time"]):
        start_time = datetime.strptime(event["start_time"], "%H:%M").time()
        end_time = datetime.strptime(event["end_time"], "%H:%M").time()

        if start_time <= now < end_time:
            current_event = event
        
        if start_time > now and next_event is None:
            next_event = event
            # current_eventが見つかったら、次のイベントも見つけた時点でループを抜けても良い
            if current_event:
                break
    
    response_parts = []
    if current_event:
        presenters = ', '.join(current_event.get('presenters', []))
        response_parts.append(f"現在、{current_event.get('description', 'イベント')}（担当: {presenters}）が行われています。")
    
    if next_event:
        next_event_desc = f"次は{next_event['start_time']}から、{next_event.get('description', '次のイベント')}が予定されています。"
        response_parts.append(next_event_desc)
    
    if not current_event and not next_event:
        return "本日のタイムテーブルに記載されたイベントはすべて終了しました。"

    return " ".join(response_parts)

# --- Step 4: 最終応答生成 (Generate) の最後の味付けで使用 ---
def get_days_until_event_message() -> str:
    """
    イベント開催日までの残り日数を計算し、回答に添えるメッセージを生成します。
    この関数は「イベント前」にのみ呼び出されます。

    Returns:
        str: 「オープンキャンパス開催まで、あと〇日です！」という文字列。
    """
    try:
        config_path = os.path.join(KNOWLEDGE_BASE_PATH, "00_イベント概要", "event_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        event_date_str = config["eventDate"]
    except (FileNotFoundError, KeyError):
        return "" # 設定ファイルがない場合は何も追加しない

    event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
    today = datetime.now().date()
    days_remaining = (event_date - today).days

    # この関数はイベント前にしか呼ばれない想定だが、念のため分岐
    if days_remaining > 0:
        return f"オープンキャンパス開催まで、あと{days_remaining}日です！"
    
    return ""
