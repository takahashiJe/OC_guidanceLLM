# backend/worker/app/graph/tools.py

import json
import os
from datetime import datetime, time, timedelta
from typing import List, Dict, Any


# スクリプト自身の絶対パスを取得し、それを基準にknowledgeディレクトリへのパスを構築
_current_file_path = os.path.abspath(__file__)
_graph_dir = os.path.dirname(_current_file_path)
_app_dir = os.path.dirname(_graph_dir)
_worker_root = os.path.dirname(_app_dir)
KNOWLEDGE_BASE_DIR = "backend/worker/data/knowledge"


def get_event_context() -> str:
    """
    イベントの開催日を基準に、現在の状況を判断します。
    """

    try:
        # 修正点: "00_イベント概要" ディレクトリをパスから削除
        config_path = os.path.join(KNOWLEDGE_BASE_DIR, "event_config.json")
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

def get_current_schedule_info(context_topic: str) -> str | None:
    """
    現在の時刻とユーザーの質問の文脈（トピック）に基づいて、
    関連するタイムテーブルJSONからリアルタイムのイベント情報を生成する。
    """
    print(f"---TOOL[get_current_schedule_info]: リアルタイム情報を検索中 (トピック: {context_topic})---")
    
    # 1. 文脈に応じて参照するJSONファイルを決定
    if "山口研" in context_topic or "サイバーフィジカル" in context_topic:
        json_path = os.path.join(KNOWLEDGE_BASE_DIR, "03_学部学科/システム科学技術学部/05_経営システム工学科/研究室/サイバーフィジカルシステム研究室_山口研/timetable_yamaguchi_lab.json")
    elif "経営システム工学科" in context_topic:
        json_path = os.path.join(KNOWLEDGE_BASE_DIR, "03_学部学科/システム科学技術学部/05_経営システム工学科/timetable_keiei_system.json")
    else: # デフォルトはオープンキャンパス全体
        json_path = os.path.join(KNOWLEDGE_BASE_DIR, "00_イベント概要/timetable_main_event.json")

    if not os.path.exists(json_path):
        print(f"  - タイムテーブルファイルが見つかりません: {json_path}")
        return None

    # 2. JSONファイルを読み込み、現在の時刻を取得
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            schedule = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"  - タイムテーブルファイルの読み込みに失敗: {json_path}")
        return None

    now = datetime.now().time()
    
    # 3. 現在開催中・次のイベントを探す
    ongoing_events = []
    next_events = []
    
    for event in schedule:
        try:
            start_time = time.fromisoformat(event["start_time"])
            end_time = time.fromisoformat(event["end_time"])

            if start_time <= now <= end_time:
                ongoing_events.append(f"「{event['event_name']}」（〜{event['end_time']} @ {event['location']}）")
            elif now < start_time:
                next_events.append((start_time, f"「{event['event_name']}」（{event['start_time']}〜 @ {event['location']}）"))
        except (ValueError, KeyError):
            continue # 時刻フォーマットが不正なデータはスキップ

    # 4. 状況に応じたメッセージを生成
    message_parts = []
    if ongoing_events:
        message_parts.append(f"現在、{' と '.join(ongoing_events)} が開催中です。")

    # 次のイベントを時間順にソートして、直近のものだけ表示
    if next_events:
        next_events.sort()
        # 1時間以内に始まるイベントをリストアップ
        upcoming_events_str = [evt_str for t, evt_str in next_events if t <= (datetime.combine(datetime.today(), now) + timedelta(hours=1)).time()]
        if upcoming_events_str:
            message_parts.append(f"まもなく、{'、'.join(upcoming_events_str)} が始まります。")

    if not message_parts:
        return "現在開催中、またはまもなく開始される予定の関連イベントはありません。"
        
    final_message = "\n".join(message_parts)
    print(f"  - 生成されたリアルタイム情報: {final_message}")
    return final_message


def get_days_until_event_message() -> str:
    """
    イベント開催日までの残り日数を計算し、回答に添えるメッセージを生成します。
    """
    try:
        # 修正点: "00_イベント概要" ディレクトリをパスから削除
        config_path = os.path.join(KNOWLEDGE_BASE_DIR, "event_config.json")
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
