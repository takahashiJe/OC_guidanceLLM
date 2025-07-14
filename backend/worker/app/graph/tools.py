import json
from datetime import datetime

def get_current_schedule_info(lab_name: str) -> str:
    """
    指定された研究室のタイムテーブルを調べ、現在と次のイベント情報を返す。
    """
    # 1. タイムテーブルファイルを読み込む
    try:
        with open(f"timetable_{lab_name}.json", "r", encoding="utf-8") as f:
            schedule = json.load(f)
    except FileNotFoundError:
        return f"{lab_name}のスケジュール情報が見つかりません。"

    # 2. 現在時刻を取得する
    now = datetime.now().time()
    today = datetime.now().date()

    current_event = None
    next_event = None

    # 3. スケジュールをループして現在と次のイベントを探す
    for event in sorted(schedule, key=lambda x: x["start_time"]):
        start_time = datetime.strptime(event["start_time"], "%H:%M").time()
        end_time = datetime.strptime(event["end_time"], "%H:%M").time()

        if start_time <= now < end_time:
            current_event = event
        
        if start_time > now and next_event is None:
            next_event = event
            break
    
    # 4. 状況に応じた応答文を生成する
    if current_event:
        response = f"現在、{current_event['description']}（担当: {', '.join(current_event['presenters'])}）が行われています。"
        if next_event:
            response += f" 次は{next_event['start_time']}から、{next_event['description']}が予定されています。"
        return response
    
    if next_event:
        return f"次の予定は{next_event['start_time']}からの{next_event['description']}です。"

    return "本日の予定はすべて終了しました。"

def get_days_until_event() -> str:
    """
    イベント開催日までの残り日数を計算して、状況に応じた文字列を返す。
    """
    # 1. 設定ファイルを読み込む
    try:
        with open("event_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        event_date_str = config["eventDate"]
    except FileNotFoundError:
        return "イベント情報が見つかりません。"

    # 2. 日付を計算する
    event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
    today = datetime.now().date()
    delta = event_date - today
    days_remaining = delta.days

    # 3. 状況に応じた応答文を生成する
    if days_remaining > 0:
        return f"オープンキャンパス開催まで、あと{days_remaining}日です！"
    elif days_remaining == 0:
        return "オープンキャンパスは本日開催です！"
    else:
        return "今年のオープンキャンパスは終了しました。ご来場ありがとうございました。"