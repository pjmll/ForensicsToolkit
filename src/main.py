import argparse
import logging
import sys
import os
from pathlib import Path

from constants import (
    BROWSER_META,
    BANNER_TEXT,
    VERSION,
    EXPORT_DIR_DEFAULT
)
from chrome_database import ChromeDataHandler
from firefox_database import FirefoxDataHandler
from exporter import UniversalExporter, ExportFormat
from forensics import HistoryAnalyzer
from menu import run_interactive_menu
# 配置全局日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
LOG = logging.getLogger("ForensicsMain")

class ForensicsApp:
    """取证程序主控制类"""
    
    def __init__(self, args):
        self.args = args
        self.exporter = UniversalExporter(args.output or EXPORT_DIR_DEFAULT)
        self.analyzer = HistoryAnalyzer()

    def _process_browser(self, browser_id: str, meta: dict):
        """处理单个浏览器的取证逻辑"""
        db_path = meta.get('path')
        if not db_path or not os.path.exists(db_path):
            LOG.warning(f"跳过 {browser_id}: 未找到数据库文件 {db_path}")
            return

        LOG.info(f"正在分析 {browser_id} ...")
        
        # 根据类型选择加载器
        try:
            if meta['type'] == 'chrome':
                db = ChromeDataHandler(db_path)
            else:
                db = FirefoxDataHandler(db_path)

            # 获取数据
            records = db.fetch_all_history()
            if not records:
                LOG.info(f"{browser_id} 无历史记录。")
                return

            # 执行取证分析
            analysis_report = self.analyzer.generate_forensics_report(records)
            
            # 导出结果
            fmt_map = {
                'json': ExportFormat.JSON,
                'csv': ExportFormat.CSV,
                'html': ExportFormat.HTML,
                'text': ExportFormat.TEXT,
                'txt': ExportFormat.TEXT,
                'all': ExportFormat.ALL
            }
            target_fmt = fmt_map.get(self.args.format.lower(), ExportFormat.CSV)
            
            # 使用父目录名（Profile名）增加区分度
            prefix = f"{browser_id}_forensics"
            self.exporter.export(records, prefix, target_fmt)
            
            # 针对HTML，传入完整的分析报告
            if target_fmt in [ExportFormat.HTML, ExportFormat.ALL]:
                self.exporter.save_as_html(analysis_report, f"{prefix}_report.html")
                
            LOG.info(f"{browser_id} 取证完成。")
            
        except Exception as e:
            LOG.error(f"处理 {browser_id} 时发生错误: {e}")

    def run(self):
        """启动取证流程"""
        print(BANNER_TEXT)
        LOG.info(f"版本: {VERSION} 启动")

        target_browsers = self.args.browser.lower().split(',')
        
        found_any = False
        for b_id, meta in BROWSER_META.items():
            if 'all' in target_browsers or b_id.lower() in target_browsers:
                self._process_browser(b_id, meta)
                found_any = True
        
        if not found_any:
            LOG.error(f"未匹配到任何有效的浏览器目标: {self.args.browser}")

def main():
    parser = argparse.ArgumentParser(description="浏览器历史记录取证工具")
    parser.add_argument("-b", "--browser", choices=['chrome', 'firefox', 'all'], help="目标浏览器 (chrome, firefox, all)")
    parser.add_argument("-o", "--output", help="导出目录")
    parser.add_argument("-f", "--format", choices=['json', 'csv', 'html', 'text', 'all'], help="导出格式")
    parser.add_argument("-i", "--interactive", action="store_true", help="开启交互模式菜单")
    
    args = parser.parse_args()

    # 如果指定了 -i 或者没有任何命令行参数，则进入交互菜单
    if args.interactive or (not args.browser and not args.format and not args.output):
        def start_app_with_args(interactive_args):
            # 将交互式 Args 对象模拟成 argparse.Namespace
            forensics = ForensicsApp(interactive_args)
            forensics.run()
        
        run_interactive_menu(start_app_with_args)
    else:
        # 设置默认值（如果命令行没传的话）
        if not args.browser: args.browser = "all"
        if not args.format: args.format = "csv"
        
        app = ForensicsApp(args)
        app.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] 用户中断。")
        sys.exit(0)
