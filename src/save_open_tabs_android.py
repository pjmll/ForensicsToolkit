import datetime
import os
import requests
from pythoncommons.file_utils import FileUtils
from requests.exceptions import ConnectionError

# 远程调试端口与套接字名称
PORT = "9222"
ABSTRACT_SOCKET_NAME = "chrome_devtools_remote"

def main():
    """提取Android设备上Chrome浏览器当前打开的所有标签页"""
    
    # 1. 检查已连接的设备
    try:
        adb_out = os.popen("adb devices -l").read()
        if not adb_out or "List of devices attached" not in adb_out:
            print("错误：无法读取adb设备列表。请确保adb已正确安装且已加入环境变量。")
            return

        lines = [line for line in adb_out.splitlines() if line.strip() and "List of devices" not in line]
        if not lines:
            print("未发现已连接的Android设备！请检查USB调试是否开启。")
            exit(1)
        
        print(f"检测到设备连接信息: {lines[0]}")
    except Exception as e:
        print(f"执行ADB命令时出错: {e}")
        return

    # 2. 管理端口转发
    try:
        forward_list = os.popen("adb forward --list").read().strip()
        if not forward_list:
            print(f"未检测到端口转发。正在开启TCP端口 {PORT} 到本地抽象套接字的转发...")
            os.system(f"adb forward tcp:{PORT} localabstract:{ABSTRACT_SOCKET_NAME}")
        
        forward_list = os.popen("adb forward --list").read().strip()
        if not forward_list:
            print(f"警告：无法创建端口转发（端口 {PORT}）。请检查是否有其他进程占用该端口。")
            exit(1)
        print(f"当前转发列表: {forward_list}")
    except Exception as e:
        print(f"配置端口转发时出错: {e}")

    # 3. 抓取标签页数据
    data = None
    try:
        data = load_json(f"http://localhost:{PORT}/json/list")
    except ConnectionError:
        print("错误：连接Android端Chrome失败。请确保手机上的Google Chrome浏览器已启动并处于前端。")
        exit(1)
    except Exception as e:
        print(f"数据抓取异常: {e}")
        exit(1)

    # 4. 解析并保存结果
    if not data:
        print("未发现已打开的网页标签页。程序退出...")
        return

    # 按原始 ID 排序以保持顺序
    ordered_data = sorted(data, key=lambda d: d.get('id', 0))
    urls = [d['url'] for d in ordered_data if 'url' in d]

    if not urls:
        print("解析到的URL列表为空。")
        return

    final_result = "\n".join(urls)
    file_name = "android_tabs_" + datetime.datetime.now().strftime('%Y%m%d_%H%M%S.txt')
    # 使用跨平台兼容的临时目录
    temp_dir = os.environ.get('TEMP') or os.environ.get('TMP') or "/tmp"
    file_path = os.path.join(temp_dir, file_name)
    
    try:
        FileUtils.write_to_file(file_path, final_result)
        print("=" * 50)
        print(f"成功！已保存 {len(urls)} 个标签页到文件：")
        print(f"路径: {file_path}")
        print("提示：你可以将此文件复制到下载目录查看。")
        print("=" * 50)
    except Exception as e:
        print(f"保存文件失败: {e}")

def load_json(url):
    """远程调用获取数据"""
    r = requests.get(url, timeout=5)
    return r.json()

if __name__ == '__main__':
    main()
