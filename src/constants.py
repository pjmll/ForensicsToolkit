import os
import glob
from os.path import expanduser, join, exists

# 定义浏览器类型及其对应的资源描述映射
BROWSER_META_CONFIG = {
    'chrome': {
        'type': 'chrome',
        'desc': "Google Chrome",
        'db_name': 'History'
    },
    'firefox': {
        'type': 'firefox',
        'desc': "Mozilla Firefox",
        'db_name': 'places.sqlite'
    }
}

def _resolve_browser_paths():
    """
    解析各操作系统的浏览器数据根目录及具体Profile路径。
    """
    home = expanduser("~")
    paths = {'chrome': [], 'firefox': []}
    
    if os.name == 'nt':
        local = join(home, 'AppData', 'Local')
        roaming = join(home, 'AppData', 'Roaming')
        # Chrome路径
        paths['chrome'] = [join(local, 'Google', 'Chrome', 'User Data', 'Default', 'History')]
        # Firefox路径 (需要递归搜索profiles)
        ff_base = join(roaming, 'Mozilla', 'Firefox', 'Profiles')
        if exists(ff_base):
            paths['firefox'] = glob.glob(join(ff_base, '*', 'places.sqlite'))
            
    elif os.name == 'posix':
        # macOS/Linux兼容逻辑
        import platform
        is_mac = platform.system() == 'Darwin'
        if is_mac:
            lib = join(home, 'Library', 'Application Support')
            paths['chrome'] = [join(lib, 'Google', 'Chrome', 'Default', 'History')]
            ff_p = join(home, 'Library', 'Mozilla', 'Firefox', 'Profiles')
            paths['firefox'] = glob.glob(join(ff_p, '*', 'places.sqlite'))
        else:
            # Linux
            paths['chrome'] = [join(home, '.config', 'google-chrome', 'Default', 'History')]
            paths['firefox'] = glob.glob(join(home, '.mozilla', 'firefox', '*', 'places.sqlite'))
            
    return paths

_PATHS = _resolve_browser_paths()

# 全局浏览器元数据定义
BROWSER_META = {}
for key, cfg in BROWSER_META_CONFIG.items():
    found_paths = _PATHS.get(key, [])
    # 如果找到了多个路径（如Firefox多个Profile），我们取第一个或在main中处理
    #此处为简化逻辑，取第一个有效路径
    actual_path = next((p for p in found_paths if exists(p)), "")
    BROWSER_META[key] = {
        'type': cfg['type'],
        'desc': cfg['desc'],
        'db_name': cfg['db_name'],
        'path': actual_path
    }

# --- 取证工具辅助常量 ---
VERSION = "3.1.5"
EXPORT_DIR_DEFAULT = "browser_history_exports"
BANNER_TEXT = """
#######################################################
#                                                     #
#            浏览器历史记录取证分析工具                 #
#       Forensics Toolkit for Chrome & Firefox        #
#                                                     #
#######################################################
"""
