import logging
import sqlite3
import dataclasses
import os
import shutil
import tempfile
from typing import List, Optional
from datetime import datetime

from pythoncommons.date_utils import DateUtils

# 定义简单的取证记录数据模型
@dataclasses.dataclass
class BrowserHistoryRecord:
    """统一的历史记录数据容器模型"""
    title: str
    url: str
    last_visit_time: Optional[datetime]
    visit_count: int

class ChromeDataHandler:
    """
    针对Chromium系列数据库的数据解析处理器。
    负责底层SQL交互及专有的Windows Epoch时间戳解析。
    使用临时文件备份策略解决数据库锁定问题。
    """
    def __init__(self, source_path: str):
        self.source = source_path
        self._temp_dir = tempfile.mkdtemp()
        self._temp_db = os.path.join(self._temp_dir, "History_backup")
        
        # 为了应对数据库被浏览器占用的情况，使用shutil.copy2复制一份到临时目录
        # 即使浏览器未关闭，通常也允许读取该文件
        try:
            shutil.copy2(source_path, self._temp_db)
            # 使用URI模式以只读模式打开，进一步增加成功率
            self._connector = sqlite3.connect(f"file:{self._temp_db}?mode=ro", uri=True)
        except Exception as e:
            logging.getLogger(__name__).warning(f"无法创建数据库备份: {e}")
            # 备选方案：尝试直接连接
            self._connector = sqlite3.connect(source_path)

    def fetch_all_history(self) -> List[BrowserHistoryRecord]:
        """批量拉取所有已排序的历史记录轨迹"""
        
        def _parse_chrome_time(val: int) -> datetime:
            return DateUtils.add_microseconds_to_win_epoch(val or 0)

        cursor = self._connector.cursor()
        sql_script = "SELECT title, url, last_visit_time, visit_count FROM urls ORDER BY last_visit_time DESC"
        
        try:
            cursor.execute(sql_script)
            dataset = cursor.fetchall()
            
            return [
                BrowserHistoryRecord(
                    title=row[0] or "无标题", 
                    url=row[1], 
                    last_visit_time=_parse_chrome_time(row[2]), 
                    visit_count=row[3] or 0
                ) for row in dataset
            ]
        except Exception as err:
            logging.getLogger(__name__).error(f"提取数据失败: {err}")
            return []
        finally:
            cursor.close()

    def __del__(self):
        """析构时清理临时文件"""
        try:
            if hasattr(self, '_connector'):
                self._connector.close()
            if os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir, ignore_errors=True)
        except:
            pass

