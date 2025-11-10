#!/usr/bin/env python3
"""
验证 Claude Desktop MCP 配置
"""

import os
import json
from pathlib import Path

def verify_config():
    """验证配置是否正确"""
    print("=" * 60)
    print("Claude Desktop MCP 配置验证")
    print("=" * 60)
    
    # 检查配置文件
    config_file = Path("claude_desktop_config.json")
    if not config_file.exists():
        print("❌ 错误: 找不到 claude_desktop_config.json")
        return False
    
    print(f"✅ 找到配置文件: {config_file.absolute()}")
    
    # 读取配置
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ 错误: 无法读取配置文件: {e}")
        return False
    
    # 检查 MCP 服务器配置
    if "mcpServers" not in config:
        print("❌ 错误: 配置文件中没有 mcpServers")
        return False
    
    mcp_servers = config["mcpServers"]
    
    # 检查 siliconflow-server
    if "siliconflow-server" not in mcp_servers:
        print("❌ 错误: 配置文件中没有 siliconflow-server")
        return False
    
    server_config = mcp_servers["siliconflow-server"]
    print(f"\n✅ 找到 siliconflow-server 配置")
    
    # 检查命令
    if "command" not in server_config:
        print("❌ 错误: 缺少 command 配置")
        return False
    
    command = server_config["command"]
    print(f"   命令: {command}")
    
    # 检查参数
    if "args" not in server_config or not server_config["args"]:
        print("❌ 错误: 缺少 args 配置")
        return False
    
    args = server_config["args"]
    script_path = args[0] if args else None
    
    if script_path:
        # 检查路径是否为绝对路径
        if not os.path.isabs(script_path):
            print(f"⚠️  警告: 路径不是绝对路径: {script_path}")
            print(f"   建议使用绝对路径以确保 Claude Desktop 能正确找到脚本")
        else:
            print(f"✅ 使用绝对路径: {script_path}")
        
        # 检查文件是否存在
        if os.path.exists(script_path):
            print(f"✅ 脚本文件存在: {script_path}")
        else:
            print(f"❌ 错误: 脚本文件不存在: {script_path}")
            return False
    
    # 检查环境变量
    if "env" not in server_config:
        print("⚠️  警告: 没有配置环境变量")
    else:
        env = server_config["env"]
        if "SILICONFLOW_API_KEY" in env:
            api_key = env["SILICONFLOW_API_KEY"]
            if api_key and api_key != "your_siliconflow_api_key_here":
                print(f"✅ API 密钥已配置: {api_key[:10]}...{api_key[-4:]}")
            else:
                print("⚠️  警告: API 密钥未设置或使用占位符")
        else:
            print("⚠️  警告: 未配置 SILICONFLOW_API_KEY")
    
    # 检查 Python 环境
    print(f"\n检查 Python 环境...")
    try:
        import sys
        python_path = sys.executable
        print(f"✅ Python 路径: {python_path}")
        print(f"   Python 版本: {sys.version.split()[0]}")
    except Exception as e:
        print(f"❌ 错误: 无法获取 Python 信息: {e}")
    
    # 检查依赖
    print(f"\n检查依赖...")
    dependencies = {
        "requests": "requests",
        "mcp": "mcp",
        "dotenv": "python-dotenv"
    }
    
    all_ok = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装，请运行: pip install {package}")
            all_ok = False
    
    # 总结
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ 配置验证通过！")
        print("\n下一步:")
        print("1. 将配置复制到 Claude Desktop 配置文件:")
        print("   Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
        print("2. 确保路径是绝对路径")
        print("3. 完全重启 Claude Desktop")
        print("4. 在 Claude Desktop 中尝试使用工具")
    else:
        print("⚠️  配置存在问题，请根据上述提示修复")
    print("=" * 60)
    
    return all_ok

if __name__ == "__main__":
    verify_config()

