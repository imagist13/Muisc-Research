"""
快速启动API服务器的便捷脚本
在项目根目录运行此脚本
"""

import os
import sys
from pathlib import Path

# 确保在项目根目录
project_root = Path(__file__).parent
os.chdir(project_root)

# 添加项目根目录到Python路径
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入并运行启动脚本
from api.start_server import main

if __name__ == "__main__":
    main()

