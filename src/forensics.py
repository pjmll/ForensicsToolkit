import logging
import collections
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse, parse_qs

# 启动日志审计器
LOGGER = logging.getLogger("ForensicsEngine")

class HistoryAnalyzer:
    """
    电子数据取证分析核心引擎类。
    """
    
    SEARCH_PARAMS = {
        'google': 'q', 'bing': 'q', 'duckduckgo': 'q',
        'baidu': ['wd', 'word'], 'sogou': 'query', '360': 'q'
    }

    def __init__(self, history_data: List[Any] = None):
        """
        初始化分析引擎。
        :param history_data: 初始历史记录列表，默认为None。
        """
        self.data_store = history_data if history_data is not None else []
        self._results = {}

    def set_data(self, history_data: List[Any]):
        """更新分析引擎的数据源"""
        self.data_store = history_data

    def _extract_query(self, link: str) -> str:
        """从URL解析并清洗搜索内容的关键词"""
        try:
            url_obj = urlparse(link)
            host = url_obj.netloc.lower()
            query_vals = parse_qs(url_obj.query)
            
            # 多引擎自动识别策略
            for engine, keys in self.SEARCH_PARAMS.items():
                if engine in host:
                    key_list = keys if isinstance(keys, list) else [keys]
                    for k in key_list:
                        if k in query_vals:
                            return query_vals[k][0]
            return ""
        except Exception as err:
            LOGGER.debug(f"关键词解析失败: {err}")
            return ""

    def generate_forensics_report(self, records: List[Any] = None, limit: int = 15) -> Dict[str, Any]:
        """
        全量执行取证分析：域名频度、检索词统计、时间流向分析。
        :param records: 可选的即时数据源。
        :param limit: 返回前N个结果。
        """
        data = records if records is not None else self.data_store
        
        host_counter = collections.Counter()
        query_counter = collections.Counter()
        timeline_summary = [] # 保持与exporter期望的key一致
        
        for record in data:
            # 1. 域名归集
            try:
                domain = urlparse(record.url).netloc
                if domain:
                    host_counter[domain] += 1
            except: pass
            
            # 2. 搜索轨迹聚合
            search_word = self._extract_query(record.url)
            if search_word:
                query_counter[search_word] += 1
                
        # 结果封装，确保key名与exporter.py对应
        self._results = {
            'domain_ranking': host_counter.most_common(limit),
            'frequent_searches': query_counter.most_common(limit),
            'timeline_summary': data[:50] # 最近50条记录用于展示
        }
        return self._results

def analyze_history(entries: List[Any], top_n: int = 10) -> Dict[str, Any]:
    """兼容性业务接口：调用分析类"""
    engine = HistoryAnalyzer(entries)
    report_data = engine.generate_forensics_report(limit=top_n)
    return report_data
