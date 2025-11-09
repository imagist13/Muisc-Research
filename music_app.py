"""
音乐推荐Agent的Streamlit前端界面
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, List

# 在导入其他模块之前加载配置
try:
    from config.settings_loader import load_and_setup_settings
    load_and_setup_settings()
except Exception as e:
    # 如果加载配置失败，继续运行（可能使用环境变量）
    print(f"警告: 无法从 setting.json 加载配置: {e}")

import streamlit as st

from music_agent import MusicRecommendationAgent


def _format_song_card(song: Dict[str, Any], show_reason: bool = False, reason: str = "") -> None:
    """格式化歌曲卡片显示"""
    title = song.get("title", "未知")
    artist = song.get("artist", "未知")
    album = song.get("album", "")
    genre = song.get("genre", "")
    year = song.get("year", "")
    popularity = song.get("popularity", 0)
    
    # 显示歌曲信息
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### 🎵 {title}")
        st.markdown(f"**艺术家**: {artist}")
        if album:
            st.markdown(f"**专辑**: {album}")
        
        # 标签
        tags = []
        if genre:
            tags.append(f"🎸 {genre}")
        if year:
            tags.append(f"📅 {year}")
        if tags:
            st.markdown(" · ".join(tags))
    
    with col2:
        if popularity:
            st.metric("流行度", f"{popularity}/100")
    
    # 显示推荐理由
    if show_reason and reason:
        st.info(f"💡 {reason}")
    
    st.divider()


def _render_recommendations(recommendations: List[Dict[str, Any]]) -> None:
    """渲染推荐结果"""
    if not recommendations:
        st.warning("没有找到合适的推荐")
        return
    
    st.subheader(f"🎼 为你推荐 {len(recommendations)} 首歌曲")
    
    for i, rec in enumerate(recommendations, 1):
        with st.expander(f"推荐 {i}", expanded=(i == 1)):
            song = rec.get("song", rec)  # 兼容不同格式
            reason = rec.get("reason", "")
            similarity = rec.get("similarity_score", 0)
            
            _format_song_card(song, show_reason=True, reason=reason)
            
            if similarity > 0:
                st.progress(similarity, text=f"匹配度: {int(similarity * 100)}%")


def _render_search_results(results: List[Dict[str, Any]]) -> None:
    """渲染搜索结果"""
    if not results:
        st.warning("没有找到相关歌曲")
        return
    
    st.subheader(f"🔍 找到 {len(results)} 首歌曲")
    
    for i, song in enumerate(results, 1):
        with st.expander(f"{i}. {song.get('title', '未知')} - {song.get('artist', '未知')}", 
                        expanded=(i == 1)):
            _format_song_card(song)


def _init_agent() -> None:
    """初始化Agent"""
    if "music_agent" in st.session_state:
        return
    
    try:
        st.session_state.music_agent = MusicRecommendationAgent()
        st.session_state.agent_error = None
    except Exception as exc:
        st.session_state.music_agent = None
        st.session_state.agent_error = str(exc)
    
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("last_result", None)
    st.session_state.setdefault("favorite_songs", [])


def _run_agent(query: str) -> Dict[str, Any]:
    """运行Agent"""
    agent: MusicRecommendationAgent | None = st.session_state.get("music_agent")
    chat_history: List[Dict[str, Any]] = st.session_state.get("chat_history", [])
    
    if agent is None:
        raise RuntimeError(st.session_state.get("agent_error") or "智能体未正确初始化。")
    
    result = asyncio.run(agent.get_recommendations(
        query=query,
        chat_history=chat_history
    ))
    
    if result.get("success"):
        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "assistant", "content": result.get("response", "")})
        st.session_state.chat_history = chat_history
    
    return result


def _sidebar() -> None:
    """侧边栏"""
    with st.sidebar:
        st.header("🎵 音乐推荐助手")
        
        # 系统状态
        st.subheader("系统状态")
        siliconflow_key = os.getenv("SILICONFLOW_API_KEY")
        
        if siliconflow_key:
            st.success("✓ SILICONFLOW_API_KEY 已设置")
        else:
            st.error("✗ 缺少 SILICONFLOW_API_KEY")
        
        if st.session_state.get("agent_error"):
            st.error(f"智能体初始化失败：{st.session_state.agent_error}")
            if st.button("重试初始化", use_container_width=True):
                st.session_state.pop("music_agent", None)
                _init_agent()
                st.rerun()
        
        st.divider()
        
        # 快捷功能
        st.subheader("快捷推荐")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("😊 开心", use_container_width=True):
                st.session_state.quick_query = "我现在心情很好，推荐一些开心的音乐"
                st.rerun()
            
            if st.button("😢 悲伤", use_container_width=True):
                st.session_state.quick_query = "推荐一些悲伤的音乐"
                st.rerun()
            
            if st.button("🏃 运动", use_container_width=True):
                st.session_state.quick_query = "适合运动时听的音乐"
                st.rerun()
        
        with col2:
            if st.button("😌 放松", use_container_width=True):
                st.session_state.quick_query = "推荐一些放松的音乐"
                st.rerun()
            
            if st.button("💼 工作", use_container_width=True):
                st.session_state.quick_query = "适合工作时听的音乐"
                st.rerun()
            
            if st.button("💤 睡觉", use_container_width=True):
                st.session_state.quick_query = "推荐一些助眠音乐"
                st.rerun()
        
        st.divider()
        
        # 对话历史
        st.subheader("对话历史")
        history = st.session_state.get("chat_history", [])
        if not history:
            st.caption("暂无历史记录")
        else:
            for entry in history[-6:]:
                role = "🙋 你" if entry.get("role") == "user" else "🤖 助手"
                with st.expander(f"{role}: {entry.get('content', '')[:30]}..."):
                    st.write(entry.get('content', ''))
        
        if st.button("清空历史", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.last_result = None
            st.rerun()
        
        st.divider()
        
        # 我的收藏
        st.subheader("我的收藏")
        favorites = st.session_state.get("favorite_songs", [])
        if favorites:
            for fav in favorites:
                st.text(f"♥ {fav['title']} - {fav['artist']}")
        else:
            st.caption("暂无收藏")


def main() -> None:
    """主函数"""
    st.set_page_config(
        page_title="音乐推荐助手",
        page_icon="🎵",
        layout="wide"
    )
    
    st.title("🎵 智能音乐推荐助手")
    st.caption("基于AI的个性化音乐推荐系统 · 发现你喜欢的音乐")
    
    _init_agent()
    _sidebar()
    
    if st.session_state.get("music_agent") is None:
        st.stop()
    
    # 主要交互区域
    tab1, tab2, tab3 = st.tabs(["💬 智能推荐", "🔍 音乐搜索", "ℹ️ 关于"])
    
    with tab1:
        st.subheader("告诉我你想听什么")
        
        # 处理快捷查询
        quick_query = st.session_state.pop("quick_query", "")
        
        with st.form("recommendation-form", clear_on_submit=False):
            query = st.text_area(
                "描述你的需求",
                value=quick_query,
                height=100,
                placeholder="例如：\n- 我现在心情很好，想听点开心的音乐\n- 推荐一些适合运动的歌\n- 有没有类似《晴天》的歌曲\n- 推荐周杰伦的经典歌曲"
            )
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                submitted = st.form_submit_button("🎼 获取推荐", type="primary", use_container_width=True)
        
        if submitted and query.strip():
            with st.spinner("正在为你寻找最合适的音乐..."):
                try:
                    result = _run_agent(query.strip())
                    st.session_state.last_result = result
                except Exception as exc:
                    st.error(f"处理请求时发生错误：{exc}")
        
        # 显示结果
        result = st.session_state.get("last_result")
        
        if result:
            if result.get("success"):
                st.success("✅ 推荐生成成功！")
                
                # 显示回复
                if result.get("response"):
                    st.markdown("### 🎤 推荐说明")
                    st.markdown(result["response"])
                
                # 显示推荐
                if result.get("recommendations"):
                    st.markdown("---")
                    _render_recommendations(result["recommendations"])
                
                # 显示搜索结果（如果有）
                elif result.get("search_results"):
                    st.markdown("---")
                    _render_search_results(result["search_results"])
            else:
                st.error(f"❌ 推荐失败：{result.get('error', '未知错误')}")
        else:
            # 欢迎信息
            st.info("👋 欢迎使用音乐推荐助手！告诉我你想听什么样的音乐，或者使用左侧的快捷按钮。")
            
            # 示例卡片
            st.markdown("### 💡 你可以这样问我")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                **根据心情推荐**
                - 心情好时想听的歌
                - 伤感的音乐
                - 浪漫的歌曲
                """)
            
            with col2:
                st.markdown("""
                **根据场景推荐**
                - 适合运动的音乐
                - 工作学习时听的歌
                - 睡前助眠音乐
                """)
            
            with col3:
                st.markdown("""
                **搜索和发现**
                - 搜索周杰伦的歌
                - 推荐民谣风格的歌
                - 类似《晴天》的歌
                """)
    
    with tab2:
        st.subheader("搜索音乐")
        
        with st.form("search-form"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                search_query = st.text_input(
                    "搜索关键词",
                    placeholder="歌曲名、艺术家或专辑"
                )
            
            with col2:
                genre_filter = st.selectbox(
                    "流派",
                    ["全部", "流行", "摇滚", "民谣", "电子", "说唱", "抒情", "古风", "爵士"]
                )
            
            search_submitted = st.form_submit_button("🔍 搜索", use_container_width=True)
        
        if search_submitted and search_query.strip():
            with st.spinner("搜索中..."):
                try:
                    agent = st.session_state.music_agent
                    genre = None if genre_filter == "全部" else genre_filter
                    search_result = asyncio.run(agent.search_music(search_query, genre, limit=20))
                    
                    if search_result["success"]:
                        _render_search_results(search_result["results"])
                    else:
                        st.error(f"搜索失败：{search_result['error']}")
                except Exception as exc:
                    st.error(f"搜索时发生错误：{exc}")
    
    with tab3:
        st.subheader("关于音乐推荐助手")
        
        st.markdown("""
        ### 🎵 功能特色
        
        这是一个基于AI的智能音乐推荐系统，提供以下功能：
        
        1. **智能推荐** - 根据你的心情、场景、喜好推荐音乐
        2. **音乐搜索** - 快速搜索歌曲、艺术家和专辑
        3. **相似推荐** - 找到与你喜欢的歌曲风格相似的音乐
        4. **个性化对话** - 像朋友一样和你聊音乐
        
        ### 🎸 支持的音乐流派
        
        流行 · 摇滚 · 民谣 · 电子 · 说唱 · 抒情 · 古风 · 爵士
        
        ### 🚀 使用技巧
        
        - 详细描述你的需求，推荐会更准确
        - 使用左侧快捷按钮快速开始
        - 可以询问音乐知识和歌曲信息
        - 支持中文对话，自然交流
        
        ### 💡 技术栈
        
        - **LangGraph** - 工作流编排
        - **DeepSeek** - 大语言模型
        - **Streamlit** - Web界面
        - **Python** - 后端开发
        
        ---
        
        💬 有问题或建议？随时在聊天中告诉我！
        """)
        
        # 显示Agent状态
        if st.session_state.get("music_agent"):
            status = st.session_state.music_agent.get_status()
            
            with st.expander("系统状态详情"):
                st.json(status)


if __name__ == "__main__":
    main()

