# 网页浏览历史电子数据取证分析系统

## 1. 工具名称和功能描述
**工具名称**：网页浏览历史电子数据取证分析系统 (Web Browser Forensics Analyzer)

**功能描述**：
本系统是一款针对电子数据取证（Electronic Discovery）设计的自动化工具，专门用于从终端设备（含 PC 端与移动端）中提取并分析主流浏览器的历史记录。

### 核心功能亮点：
- **全自动路径探测**：内置自适应库，能自动定位Windows系统下Chrome、Firefox的用户配置文件目录。
- **免冲突读取机制**：通过临时快照技术（Shadow Copy），针对被浏览器进程锁定的SQLite数据库提供非侵入式读取。
- **跨平台支持能力**：除传统的PC浏览器取证外，还扩展支持了通过ADB协议远程对Android设备上运行的Chrome 浏览器进行在线取证。
- **多格式可视化报告**：支持导出CSV、JSON及带有交互式统计图表的HTML报告。

## 2. 源代码文件作用说明
本系统采用模块化设计，各文件分工明确，便于二次开发与审计：

- **[src/main.py](src/main.py)**: **取证控制中心**。负责命令行参数解析、全局日志管理以及各取证模块的调度分发。
- **[src/forensics.py](src/forensics.py)**: **取证分析核心引擎**。负责对原始数据进行清洗，执行域名权重统计、搜索关键词提取等核心分析算法。
- **[src/database.py](src/database.py)**: **Chromium 引擎驱动**。专用处理Chrome浏览器的数据库连接、Windows Epoch时戳解析及Shadow Copy逻辑。
- **[src/firefox_database.py](src/firefox_database.py)**: **Gecko 引擎驱动**。专门针对Firefox的 `places.sqlite` 数据库进行深度解析与数据提取。
- **[src/exporter.py](src/exporter.py)**: **取证报告生成器**。支持多格式导出，内置HTML模板引擎用于生成可视化的取证统计图表。
- **[src/save_open_tabs_android.py](src/save_open_tabs_android.py)**: **移动端扩展工具**。通过ADB与Chrome DevTools协议，实时获取Android手机上当前打开的所有浏览器标签页URL。
- **[src/constants.py](src/constants.py)**: **系统配置仓库**。统一定义浏览器路径、分析算法参数及Banner文本，解耦硬编码。

## 3. 安装依赖
取证环境建议使用 Python 3.8+。

```bash
# 安装系统运行所需的第三方支持库
pip install -r requirements.txt
```

**关键组件说明：**
- `requests`: 用于移动端远程调试协议通讯。
- `python-commons`: 提供底层时戳转换支持。
- `adb` (外部工具): 若需使用Android取证功能，系统需安装ADB环境。

## 4. 使用方法（命令行参数说明）

### PC 取证命令：
`python src/main.py [-b BROWSER] [-f FORMAT] [-o OUTPUT]`
- `-b`: 目标 (chrome/firefox/all)
- `-f`: 格式 (html/csv/json/text)
- `-o`: 输出路径

### 移动端标签页提取命令：
`python src/save_open_tabs_android.py`
*(需确保 Android 手机已开启 USB 调试并连接至电脑)*

## 5. 示例输出
```text
19:55:00 [INFO] ForensicsMain: 正在探测浏览器配置...
19:55:01 [INFO] ForensicsMain: 发现 Firefox Profile: *.default-release
19:55:01 [INFO] ForensicsMain: 分析完成，HTML 报告已生成。
```

## 6. 适用场景和局限性
- **适用场景**：内控审计、电子证存、恶意行为溯源、Android设备在线取证。
- **局限性**：无法恢复无痕模式记录，无法直接提取受加密保护的个人敏感数据（如保存的密码）。
