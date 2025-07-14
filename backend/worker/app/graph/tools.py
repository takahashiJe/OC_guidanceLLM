# backend/worker/app/graph/tools.py

import json
import os
from datetime import datetime
from typing import List, Dict, Any

# スクリプト自身の絶対パスを取得し、それを基準にknowledgeディレクトリへのパスを構築
_current_file_path = os.path.abspath(__file__)
_graph_dir = os.path.dirname(_current_file_path)
_app_dir = os.path.dirname(_graph_dir)
_worker_root = os.path.dirname(_app_dir)
KNOWLEDGE_BASE_PATH = os.path.join(_worker_root, "data", "knowledge")


def get_event_context() -> str:
    """
    イベントの開催日を基準に、現在の状況を判断します。
    """
    try:
        # 修正点: "00_イベント概要" ディレクトリをパスから削除
        config_path = os.path.join(KNOWLEDGE_BASE_PATH, "event_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        event_date_str = config["eventDate"]
    except (FileNotFoundError, KeyError) as e:
        print(f"ERROR: event_config.jsonの読み込みに失敗しました。Path: {config_path}, Error: {e}")
        return "CONTEXT_ERROR"

    event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
    today = datetime.now().date()

    if today < event_date:
        return "BEFORE_EVENT"
    elif today == event_date:
        return "DURING_EVENT"
    else:
        return "AFTER_EVENT"

def get_current_schedule_info(timetable_path: str) -> str:
    """
    指定されたタイムテーブルファイルのパスを元に、現在と次のイベント情報を生成します。
    """
    try:
        with open(timetable_path, "r", encoding="utf-8") as f:
            schedule = json.load(f)
    except FileNotFoundError:
        return "" 

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


def get_days_until_event_message() -> str:
    """
    イベント開催日までの残り日数を計算し、回答に添えるメッセージを生成します。
    """
    try:
        # 修正点: "00_イベント概要" ディレクトリをパスから削除
        config_path = os.path.join(KNOWLEDGE_BASE_PATH, "event_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        event_date_str = config["eventDate"]
    except (FileNotFoundError, KeyError):
        return ""

    event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
    today = datetime.now().date()
    days_remaining = (event_date - today).days

    if days_remaining > 0:
        return f"オープンキャンパス開催まで、あと{days_remaining}日です！"
    
    return ""
