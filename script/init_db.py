import os
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# backend.shared... からインポートするためにパスを追加
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.db.models import Base

def init_database():
    """
    データベースに接続し、テーブルが存在しない場合のみ作成する。
    DBが起動するまで最大10回リトライする。
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL is not set.")
        sys.exit(1)

    print(f"Connecting to database...")
    
    engine = create_engine(db_url)
    
    # データベースが接続を受け付けるまで待機
    max_retries = 10
    for i in range(max_retries):
        try:
            connection = engine.connect()
            connection.close()
            print("Database connection successful.")
            break
        except OperationalError as e:
            if i < max_retries - 1:
                print(f"Database not ready, retrying in 5 seconds... ({e})")
                time.sleep(5)
            else:
                print(f"Error: Could not connect to database after {max_retries} retries.")
                sys.exit(1)

    # テーブルを作成
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully (if they didn't exist).")
    except Exception as e:
        print(f"An error occurred during table creation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()