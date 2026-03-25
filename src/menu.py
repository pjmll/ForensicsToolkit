import os
import sys
from datetime import datetime
from typing import Any

def run_interactive_menu(execute_callback):
    """交互式数字选择界面"""
    while True:
        print("\n" + "="*45)
        print("      取证工具 - 交互配置菜单 (Interactive)")
        print("="*45)
        print("1. [一键扫描] 自动处理所有浏览器 (Chrome+Firefox)")
        print("2. [选择浏览器] 精确扫描 Chrome/Firefox")
        print("3. [手动模式] 指定特定数据库文件路径")
        print("4. [高级配置] 设置日期筛选、关键词过滤、导出格式")
        print("5. [退出程序]")
        print("-" * 45)
        
        if not hasattr(run_interactive_menu, 'config'):
            run_interactive_menu.config = {
                'format': 'json',
                'output': './browser_history_exports',
                'start_date': None,
                'end_date': None,
                'url_filter': None,
                'verbose': False
            }
        
        cfg = run_interactive_menu.config
        choice = input("请选择功能序列号 (1-5): ").strip()
        
        if choice == '5':
            print("退出程序。")
            sys.exit(0)
            
        class Args:
            pass
        args = Args()
        for k, v in cfg.items(): setattr(args, k, v)
        args.log_file = None

        if choice == '1':
            args.mode = 'auto'
            args.browser = 'both'
            args.chrome_dir = args.firefox_dir = None
        elif choice == '2':
            args.mode = 'auto'
            b_choice = input("请输入浏览器类型 (1.Chrome / 2.Firefox / 3.Both): ").strip()
            args.browser = {'1': 'chrome', '2': 'firefox', '3': 'both'}.get(b_choice, 'both')
            args.chrome_dir = args.firefox_dir = None
        elif choice == '3':
            args.mode = 'file'
            path = input("请输入数据库文件路径: ").strip().strip('"').strip("'")
            if not os.path.exists(path):
                print(f"错误: 文件不存在 {path}")
                continue
            args.db_files = [path]
            args.browser_type = 'auto'
        elif choice == '4':
            print("\n--- 高级配置修改 (留空表示不修改当前值) ---")
            print(f"[1] 导出格式 (当前: {cfg['format']}): ", end='')
            fmt = input().strip()
            if fmt: cfg['format'] = fmt
            
            print(f"[2] 开始日期 (YYYY-MM-DD, 当前: {cfg['start_date']}): ", end='')
            sd = input().strip()
            if sd: 
                try: cfg['start_date'] = datetime.strptime(sd, '%Y-%m-%d')
                except: print("日期格式错误，未修改")
            
            print(f"[3] 结束日期 (YYYY-MM-DD, 当前: {cfg['end_date']}): ", end='')
            ed = input().strip()
            if ed: 
                try: cfg['end_date'] = datetime.strptime(ed, '%Y-%m-%d')
                except: print("日期格式错误，未修改")
                
            print(f"[4] URL 关键词过滤 (当前: {cfg['url_filter']}): ", end='')
            uf = input().strip()
            if uf: cfg['url_filter'] = uf
            
            print("配置已更新。")
            continue
        else:
            print("无效输入，请重新选择。")
            continue

        print("\n--- 正在执行取证任务 ---")
        execute_callback(args)
        input("\n任务结束，按回车键返回主菜单...")
