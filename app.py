import sys
import streamlit as st
import random
import time
# import io

from pathlib import Path
from dotenv import load_dotenv
from lib import db
from lib.ai_roast import get_roast

# 載入 .env 中的 GITHUB_TOKEN
# PyInstaller EXE 模式下，也嘗試從 EXE 所在資料夾讀取 .env
if getattr(sys, "frozen", False):
    load_dotenv(Path(sys.executable).parent / ".env")
load_dotenv()

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=LXGW+WenKai+TC&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"], .stMarkdown, .stTextInput, .stButton, .stCaption, p, div, span, input, button, label {
    font-family: 'LXGW WenKai TC', sans-serif !important;
}
/* 壓掉 label_visibility=hidden 留下的空白 */
div[data-testid="stTextInput"] label[data-testid="stWidgetLabel"] {
    display: none !important;
}
div[data-testid="stTextInput"] {
    margin-top: 0 !important;
}
</style>
<h1 style='text-align:center; font-size:48px; margin-bottom:8px; font-family:"LXGW WenKai TC",sans-serif;'>今天吃什麼</h1>
""", unsafe_allow_html=True)

# 初始化 session state
if "restaurants" not in st.session_state:
    st.session_state.restaurants = []
if "animating" not in st.session_state:
    st.session_state.animating = False
if "last_choice" not in st.session_state:
    st.session_state.last_choice = ""
if "reject_count" not in st.session_state:
    st.session_state.reject_count = 0
if "del_generation" not in st.session_state:
    st.session_state.del_generation = 0
if "prefetched_roast" not in st.session_state:
    st.session_state.prefetched_roast = ""
# 初始化資料庫並載入已存的餐廳
db.init_db()
if not st.session_state.restaurants:
    st.session_state.restaurants = db.get_restaurants()
# if "input_counter" not in st.session_state:
#     st.session_state.input_counter = 0

# 版面：左右欄
col_left, col_right = st.columns([2, 1])

with col_left:
    btn_col, btn_spacer = st.columns([1, 1])
    with btn_col:
        if st.button("&&@$$%^$#！"):
            if not st.session_state.restaurants:
                st.warning("至少加入一家餐廳")
            elif not st.session_state.animating:
                st.session_state.reject_count = 0  # 正常點擊抽選時重置拒絕計數
                st.session_state.prefetched_roast = ""  # 重置預取嘴砲
                st.session_state.animating = True

    image_area = st.empty()
    text_area = st.empty()

    # 預先快取圖片 bytes，避免每次從硬碟重新讀取造成閃爍
    @st.cache_data
    def _load_bytes(path: str):
        p = Path(path)
        if not p.exists():
            return None
        return p.read_bytes()

    # 顯示：若正在動畫就顯示 GIF，否則顯示靜態圖與上次結果
    if st.session_state.animating:
        gif_bytes = _load_bytes("assets/lot.gif")
        if gif_bytes:
            image_area.image(gif_bytes, width=640)
        else:
            image_area.image("assets/lot.gif", width=640)
    else:
        png_bytes = _load_bytes("assets/lot.png")
        if png_bytes:
            image_area.image(png_bytes, width=640)
        else:
            image_area.image("assets/lot.png", width=640)
        
        if st.session_state.last_choice:
            if st.session_state.reject_count >= 3:
                # AI 嘴砲顯示：拒絕 3 次後，顯示 AI 產生的嘴砲
                roast = st.session_state.prefetched_roast or get_roast(st.session_state.reject_count)
                st.session_state.prefetched_roast = roast  # 快取避免重複呼叫
                text_area.markdown(
                    f"<div style='background:#fff6f6; padding:16px; border-radius:10px; margin-top:12px; text-align:center; font-size:28px; font-weight:bold; color:#ff4b4b;'>{roast}</div>",
                    unsafe_allow_html=True,
                )
            else:
                # 正常顯示：把「吃...好嗎？」與「不要」按鈕放在 text_area 容器內
                with text_area.container():
                    st.markdown("""
                    <style>
                    .result-text {
                        font-size: 18px;
                        font-weight: 500;
                        margin: 0;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    res_col, btn_col_no = st.columns([3, 1])
                    with res_col:
                        st.markdown(f"<div style='height:10px'></div><p class='result-text'>吃 <b>{st.session_state.last_choice}</b> 好嗎？</p>", unsafe_allow_html=True)
                    with btn_col_no:
                        if st.button("不要", key=f"reject_btn_{st.session_state.del_generation}"):
                            st.session_state.reject_count += 1
                            if st.session_state.reject_count < 3:
                                st.session_state.animating = True
                            st.rerun()

with col_right:
    st.markdown("<div style='height:110px'></div>", unsafe_allow_html=True)

    def add_restaurant():
        name = st.session_state.restaurant_input
        if name:
            # 儲存到 SQLite，若成功則重新載入列表並清空輸入框
            added = db.add_restaurant(name)
            if added:
                st.session_state.restaurants = db.get_restaurants()
                st.session_state.restaurant_input = ""  # callback 裡可以直接清空
            else:
                st.warning("重複了啦!!!")

    st.markdown("<p style='font-size:1.2rem;margin-bottom:2px;margin-top:0;'>餐廳名稱</p>", unsafe_allow_html=True)
    st.text_input("", key="restaurant_input", label_visibility="hidden")
    st.button("加入", on_click=add_restaurant)

    st.markdown(
        "<p style='margin-bottom:4px;font-size:14px;'>目前餐廳清單：</p>",
        unsafe_allow_html=True,
    )
    if st.session_state.restaurants:
        # CSS: make the delete button look like a clean icon (no box, no border)
        st.markdown(
            """
            <style>
            /* 只鎖定 col_right 內的巢狀 row 最後一欄的按鈕（刪除鈕），不影響「加入」 */
            div[data-testid="stColumn"] div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:last-child button {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: #bbb !important;
                padding: 10px 6px 6px 0px !important;
                min-height: 0 !important;
                font-size: 20px !important;
                line-height: 1 !important;
                border-radius: 4px !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        for idx, r in enumerate(st.session_state.restaurants, 1):
            item_col, btn_col = st.columns([1, 0.12])
            with item_col:
                st.markdown(
                    f"<div style='background:#f0f2f6;padding:8px 12px;border-radius:8px;"
                    f"border-left:4px solid #4CAF50;font-size:14px;line-height:1.4;'>"
                    f"{idx}. {r}</div>",
                    unsafe_allow_html=True,
                )
            with btn_col:
                if st.button("❌", key=f"del_{st.session_state.del_generation}_{idx}"):
                    db.remove_restaurant(r)
                    st.session_state.restaurants = db.get_restaurants()
                    st.session_state.del_generation += 1
                    st.rerun()
    else:
        st.caption("還沒有餐廳喔～")

# 若標記為 animating，則在伺服器端執行 5 秒的抽選動畫，之後顯示結果並回到靜態圖
if st.session_state.animating:
    # 背景線程預取 AI 嘴砲（跟動畫同時進行，不會延遲）
    from concurrent.futures import ThreadPoolExecutor
    prefetch_future = None
    if not st.session_state.prefetched_roast:
        executor = ThreadPoolExecutor(max_workers=1)
        prefetch_future = executor.submit(get_roast, 3)

    duration = 5.0
    interval = 0.12
    iterations = max(1, int(duration / interval))

    for _ in range(iterations):
        temp_choice = random.choice(st.session_state.restaurants)
        text_area.markdown(
            f"<div style='text-align:center; margin-top:12px; font-size:22px; font-weight:600;'>{temp_choice}</div>",
            unsafe_allow_html=True,
        )
        time.sleep(interval)

    # 動畫結束，收集預取結果
    if prefetch_future:
        try:
            st.session_state.prefetched_roast = prefetch_future.result(timeout=10)
        except Exception:
            pass

    final_choice = random.choice(st.session_state.restaurants)
    st.session_state.last_choice = final_choice

    # 動畫結束，回到靜態圖並顯示結果
    try:
        image_area.image("assets/lot.png", width=640)
    except Exception:
        pass

    st.session_state.animating = False
    st.rerun()
