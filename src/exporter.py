import csv
import json
import logging
import enum
from typing import List, Dict, Any, Union
from pathlib import Path
from datetime import datetime

from chrome_database import BrowserHistoryRecord as HistoryRecord

class ExportFormat(enum.Enum):
    """支持的导出格式枚举类型"""
    TEXT = "text"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    ALL = "all"

class UniversalExporter:
    """
    通用取证结果导出器。
    支持多种工业标准格式，并包含HTML报告的可视化封装。
    """
    
    REPORT_STYLE = """
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 30px; background-color: #f5f7f9; color: #333; }
        .container { max-width: 1200px; margin: auto; }
        .header { text-align: center; margin-bottom: 40px; }
        h1 { color: #2c3e50; font-size: 2.2em; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 30px; }
        h2 { color: #34495e; border-left: 5px solid #3498db; padding-left: 15px; margin-bottom: 20px; font-size: 1.5em; }
        
        /* 统计柱状图样式 */
        .chart-row { margin-bottom: 12px; display: flex; align-items: center; }
        .chart-label { width: 200px; font-size: 0.9em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .chart-bar-container { flex-grow: 1; background: #ecf0f1; height: 20px; border-radius: 10px; margin: 0 15px; overflow: hidden; }
        .chart-bar { background: linear-gradient(90deg, #3498db, #2980b9); height: 100%; border-radius: 10px; transition: width 0.5s ease; }
        .chart-value { width: 60px; font-weight: bold; font-size: 0.9em; color: #2980b9; }

        /* 表格样式 */
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th { background-color: #f8f9fa; color: #7f8c8d; font-weight: 600; text-align: left; padding: 12px; border-bottom: 2px solid #eee; }
        td { padding: 12px; border-bottom: 1px solid #f1f1f1; font-size: 0.95em; }
        tr:hover { background-color: #fcfcfc; }
        .url-link { color: #3498db; text-decoration: none; word-break: break-all; }
        
        .keyword-tag { display: inline-block; background: #e1f5fe; color: #0277bd; padding: 5px 12px; border-radius: 20px; margin: 5px; font-size: 0.9em; }
        .meta { color: #95a5a6; font-size: 0.85em; margin-top: 40px; text-align: center; border-top: 1px solid #ddd; padding-top: 20px; }
    </style>
    """

    def __init__(self, output_dir: str = None):
        self.output_path = Path(output_dir) if output_dir else Path.cwd()
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("ForensicsExporter")

    def export(self, records: List[HistoryRecord], filename: str, format: ExportFormat):
        if format == ExportFormat.CSV:
            return self.save_as_csv(records, f"{filename}.csv")
        elif format == ExportFormat.JSON:
            data = {"entries": [r.__dict__ if hasattr(r, '__dict__') else r for r in records]}
            return self.save_as_json(data, f"{filename}.json")
        elif format == ExportFormat.TEXT:
            return self.save_as_text(records, f"{filename}.txt")
        elif format == ExportFormat.ALL:
            for fmt in [ExportFormat.CSV, ExportFormat.JSON, ExportFormat.TEXT]:
                self.export(records, filename, fmt)
        return str(self.output_path)

    def save_as_csv(self, records: List[HistoryRecord], filename: str):
        dest = self.output_path / filename
        try:
            with open(dest, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['标题', 'URL', '访问时间', '访问次数'])
                for r in records:
                    writer.writerow([getattr(r, 'title', ''), getattr(r, 'url', ''), getattr(r, 'last_visit_time', ''), getattr(r, 'visit_count', 0)])
        except Exception as e:
            self.logger.error(f"CSV 导出失败: {e}")

    def save_as_json(self, analysis_data: Dict[str, Any], filename: str):
        dest = self.output_path / filename
        try:
            with open(dest, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"JSON 导出失败: {e}")

    def save_as_text(self, records: List[HistoryRecord], filename: str):
        dest = self.output_path / filename
        try:
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(f"浏览器取证报告 - {datetime.now()}\n" + "="*60 + "\n")
                for r in records[:100]:
                    f.write(f"[{getattr(r, 'last_visit_time', '未知')}] {getattr(r, 'title', '无标题')}\n")
        except Exception as e:
            self.logger.error(f"TEXT 导出失败: {e}")

    def save_as_html(self, analysis: Dict[str, Any], filename: str):
        dest = self.output_path / filename
        rankings = analysis.get('domain_ranking', [])
        keywords = analysis.get('frequent_searches', [])
        timeline = analysis.get('timeline_summary', [])
        
        # 计算比例用的最大值
        max_visit = rankings[0][1] if rankings else 1

        chart_html = ""
        for domain, count in rankings[:10]:
            width = (count / max_visit) * 100
            chart_html += f"""
            <div class="chart-row">
                <div class="chart-label" title="{domain}">{domain}</div>
                <div class="chart-bar-container">
                    <div class="chart-bar" style="width: {width}%"></div>
                </div>
                <div class="chart-value">{count} 次</div>
            </div>"""

        keyword_html = "".join([f'<span class="keyword-tag">{word} ({count})</span>' for word, count in keywords[:15]])

        table_html = "".join([f'<tr><td>{getattr(r, "last_visit_time", "未知")}</td><td>{getattr(r, "title", "无标题")[:60]}...</td><td><a class="url-link" href="{getattr(r, "url", "#")}" target="_blank">点击跳转</a></td></tr>' for r in timeline[:30]])

        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <title>可视化取证分析报告</title>
            {self.REPORT_STYLE}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>网页浏览历史取证分析报告</h1>
                    <p>报告编号: Forensic-{datetime.now().strftime('%Y%m%d%H%M')}</p>
                </div>
                
                <div class="card">
                    <h2>1. 域名访问频率统计 (Top 10)</h2>
                    <div style="padding: 10px 0;">
                        {chart_html if chart_html else "<p>暂无统计数据</p>"}
                    </div>
                </div>

                <div class="card">
                    <h2>2. 搜索关键词分布</h2>
                    <div style="padding: 10px 0;">
                        {keyword_html if keyword_html else "<p>暂无搜索记录</p>"}
                    </div>
                </div>

                <div class="card">
                    <h2>3. 最近浏览足迹 (Timeline)</h2>
                    <table>
                        <tr><th>最后访问时间</th><th>页面标题</th><th>操作</th></tr>
                        {table_html}
                    </table>
                </div>
                
                <div class="meta">
                    证据校验和已生成 | 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
            </div>
        </body>
        </html>
        """
        try:
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            self.logger.error(f"HTML 导出失败: {e}")

