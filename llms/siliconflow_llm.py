"""
硅基流动LLM实现
使用硅基流动API进行文本生成
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI
from langchain_openai import ChatOpenAI
from .base import BaseLLM


class SiliconFlowLLM(BaseLLM):
    """硅基流动LLM实现类"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        初始化硅基流动客户端
        
        Args:
            api_key: 硅基流动API密钥，如果不提供则从环境变量或setting.json读取
            model_name: 模型名称，默认使用deepseek-chat
        """
        if api_key is None:
            api_key = os.getenv("SILICONFLOW_API_KEY")
            # 如果环境变量中没有，尝试从 setting.json 读取
            if not api_key:
                try:
                    from config.settings_loader import load_settings_from_json
                    settings = load_settings_from_json()
                    api_key = settings.get("SILICONFLOW_API_KEY")
                except:
                    pass
            if not api_key:
                raise ValueError("硅基流动API Key未找到！请设置SILICONFLOW_API_KEY环境变量或在setting.json中配置")
        
        super().__init__(api_key, model_name)
        
        # 从 setting.json 读取 base_url，如果没有则使用默认值
        base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        if base_url == "https://api.siliconflow.cn/v1":
            try:
                from config.settings_loader import load_settings_from_json
                settings = load_settings_from_json()
                base_url = settings.get("SILICONFLOW_BASE_URL", base_url)
            except:
                pass
        
        # 初始化OpenAI客户端，使用硅基流动的endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        
        self.default_model = model_name or self.get_default_model()
    
    def get_default_model(self) -> str:
        """获取默认模型名称"""
        # 优先使用环境变量中的模型配置
        model = os.getenv("SILICONFLOW_MODEL")
        if model:
            return model
        # 如果没有环境变量，尝试从 setting.json 读取
        try:
            from config.settings_loader import load_settings_from_json
            settings = load_settings_from_json()
            return settings.get("SILICONFLOW_CHAT_MODEL", "deepseek-ai/DeepSeek-V3")
        except:
            # 如果都失败，使用默认值
            return "deepseek-ai/DeepSeek-V3"
    
    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        调用硅基流动API生成回复
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户输入
            **kwargs: 其他参数，如temperature、max_tokens等
            
        Returns:
            硅基流动生成的回复文本
        """
        try:
            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 设置默认参数
            params = {
                "model": self.default_model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4000),
                "stream": False
            }
            
            # 调用API
            response = self.client.chat.completions.create(**params)
            
            # 提取回复内容
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                return self.validate_response(content)
            else:
                return ""
                
        except Exception as e:
            print(f"硅基流动API调用错误: {str(e)}")
            raise e
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取当前模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "provider": "SiliconFlow",
            "model": self.default_model,
            "api_base": "https://api.siliconflow.cn/v1"
        }


def get_chat_model() -> ChatOpenAI:
    """
    获取LangChain兼容的聊天模型（使用硅基流动）
    
    Returns:
        ChatOpenAI实例
    """
    # 优先从环境变量读取 API Key
    api_key = os.getenv("SILICONFLOW_API_KEY")
    
    # 如果环境变量中没有，尝试从 setting.json 读取
    if not api_key:
        try:
            from config.settings_loader import load_settings_from_json
            settings = load_settings_from_json()
            api_key = settings.get("SILICONFLOW_API_KEY")
        except:
            pass
    
    if not api_key:
        raise ValueError("硅基流动API Key未找到！请设置SILICONFLOW_API_KEY环境变量或在setting.json中配置")
    
    # 优先使用环境变量中的模型配置
    model_name = os.getenv("SILICONFLOW_MODEL")
    
    # 如果环境变量中没有，尝试从 setting.json 读取
    if not model_name:
        try:
            from config.settings_loader import load_settings_from_json
            settings = load_settings_from_json()
            model_name = settings.get("SILICONFLOW_CHAT_MODEL")
        except:
            pass
    
    # 如果还是没有，使用默认值
    if not model_name:
        model_name = "deepseek-ai/DeepSeek-V3"
    
    # 从 setting.json 读取 base_url，如果没有则使用默认值
    base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    if base_url == "https://api.siliconflow.cn/v1":
        try:
            from config.settings_loader import load_settings_from_json
            settings = load_settings_from_json()
            base_url = settings.get("SILICONFLOW_BASE_URL", base_url)
        except:
            pass
    
    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model_name,
        temperature=0.7,
        max_tokens=4000
    )

