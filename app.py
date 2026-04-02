import streamlit as st
import random
import time
# import io

from pathlib import Path
from lib import db

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
    try:
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
                if st.session_state.last_choice == "吃土啦":
                    # 特殊顯示：只有「吃土啦」三個大字，改用柔和背景並移除外框
                    text_area.markdown(
                        "<div style='background:#fff6f6; padding:12px; border-radius:10px; margin-top:12px; text-align:center; font-size:28px; font-weight:bold; color:#ff4b4b;'>吃土啦</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    # 正常顯示：有對齊好的「吃...好嗎？」與「不要」按鈕
                    st.markdown("""
                    <style>
                    .result-text {
                        font-size: 18px;
                        font-weight: 500;
                        margin: 0;
                    }
                    /* 隱藏 streamlit 預設按鈕邊框，透過 div 包裹來美化 */
                    div[data-testid="stButton"] > button[kind="secondary"] {
                        border: 1px solid #ff4b4b !important;
                        color: #ff4b4b !important;
                        background-color: white !important;
                        border-radius: 20px !important;
                        height: 32px !important;
                        line-height: 32px !important;
                        padding: 0 15px !important;
                    }
                    div[data-testid="stButton"] > button[kind="secondary"]:hover {
                        background-color: #ff4b4b !important;
                        color: white !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    res_col, btn_col_no = text_area.columns([4, 1])
                    with res_col:
                        st.markdown(f"<div style='height:10px'></div><p class='result-text'>吃 {st.session_state.last_choice} 好嗎？</p>", unsafe_allow_html=True)
                    with btn_col_no:
                        if st.button("不要", key="reject_btn"):
                            st.session_state.reject_count += 1
                            if st.session_state.reject_count >= 3:
                                st.session_state.last_choice = "吃土啦"
                                st.rerun()
                            else:
                                st.session_state.animating = True
                                st.rerun()
    except Exception:
        image_area.markdown("<div style='text-align:center; padding:32px;'>🎋</div>")

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

    final_choice = random.choice(st.session_state.restaurants)
    st.session_state.last_choice = final_choice

    # 動畫結束，回到靜態圖並顯示結果
    try:
        image_area.image("assets/lot.png", width=640)
    except Exception:
        image_area.markdown("<div style='text-align:center; padding:32px;'>🎋</div>")

    st.session_state.animating = False
    st.rerun()
