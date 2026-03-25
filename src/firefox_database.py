import logging
import sqlite3
import os
import shutil
import tempfile
from typing import List, Optional
from datetime import datetime

from chrome_database import BrowserHistoryRecord as HistoryRecord

LOG = logging.getLogger(__name__)

class FirefoxDataHandler:
    """
    针对Firefox(Gecko)数据库的取证处理器。
    解决places.sqlite被父进程锁定导致无法直接读取的问题。
    """
    def __init__(self, db_file_path: str):
        self.path = db_file_path
        self._temp_dir = tempfile.mkdtemp()
        self._temp_db = os.path.join(self._temp_dir, "places_backup.sqlite")
        
        try:
            # Firefox即使关闭后，父进程有时仍保持文件句柄，
            # 通过物理备份文件的形式强制读取
            shutil.copy2(db_file_path, self._temp_db)
            # 开启只读模式连接
            self._db = sqlite3.connect(f"file:{self._temp_db}?mode=ro", uri=True)
        except Exception as e:
            LOG.warning(f"数据克隆失败，尝试强制热连接: {e}")
            self._db = sqlite3.connect(db_file_path)

    def fetch_all_history(self) -> List[HistoryRecord]:
        """抓取流式点击历史并转换为标准模型"""
        
        def _epoch_to_dt(ts: int) -> Optional[datetime]:
            if not ts: return None
            try:
                return datetime.fromtimestamp(ts / 1000000)
            except: return None

        cursor = self._db.cursor()
        query = """
            SELECT DISTINCT
                h.title,
                h.url,
                MAX(v.visit_date) as last_visit_time,
                COUNT(v.id) as visit_count
            FROM moz_places h
            LEFT JOIN moz_historyvisits v ON h.id = v.place_id
            WHERE h.hidden = 0
            GROUP BY h.id
            ORDER BY last_visit_time DESC
        """
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                HistoryRecord(
                    title=item[0] if item[0] else "无标题",
                    url=item[1],
                    last_visit_time=_epoch_to_dt(item[2]),
                    visit_count=item[3] if item[3] else 0
                ) for item in rows
            ]
        except Exception as e:
            LOG.error(f"Firefox解析失败: {e}")
            return []
        finally:
            cursor.close()

    def __del__(self):
        """生命周期管理：清理临时副本"""
        try:
            if hasattr(self, '_db'): self._db.close()
            if os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir, ignore_errors=True)
        except: pass

