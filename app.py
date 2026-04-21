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
/* 壓掉 label_visibility=collapsed 留下的空白 */
</style>
<h1 style='text-align:center; font-size:48px; margin-bottom:8px; font-family:"LXGW WenKai TC",sans-serif;'>今天吃什麼</h1>
""", unsafe_allow_html=True)

# 初始化 session state
if "restaurants" not in st.session_state:
    st.session_state.restaurants = []
if "animating" not in st.session_state:
    st.session_state.animating = False
if "last_choice" not in st.session_state:
    st.session_state.last_choice = None
if "filtered_pool" not in st.session_state:
    st.session_state.filtered_pool = []
if "reject_count" not in st.session_state:
    st.session_state.reject_count = 0
if "del_generation" not in st.session_state:
    st.session_state.del_generation = 0
if "prefetched_roast" not in st.session_state:
    st.session_state.prefetched_roast = ""
if "pool_exhausted" not in st.session_state:
    st.session_state.pool_exhausted = False
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
                st.session_state.filtered_pool = list(st.session_state.restaurants)  # 重置篩選池
                st.session_state.pool_exhausted = False  # 重置空池子標記
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
        
        if st.session_state.pool_exhausted:
            text_area.markdown(
                "<div style='background:#fff3cd; padding:16px; border-radius:10px; margin-top:12px; text-align:center; font-size:22px; font-weight:bold; color:#856404;'>篩選後沒有餐廳了！</div>",
                unsafe_allow_html=True,
            )
        elif st.session_state.last_choice:
            if st.session_state.reject_count >= 3:
                # AI 嘴砲顯示：拒絕 3 次後，顯示 AI 產生的嘴砲
                roast = st.session_state.prefetched_roast or get_roast(st.session_state.reject_count)
                st.session_state.prefetched_roast = roast  # 快取避免重複呼叫
                text_area.markdown(
                    f"<div style='background:#fff6f6; padding:16px; border-radius:10px; margin-top:12px; text-align:center; font-size:28px; font-weight:bold; color:#ff4b4b;'>{roast}</div>",
                    unsafe_allow_html=True,
                )
            else:
                # 正常顯示：把「吃...好嗎？」與拒絕按鈕放在 text_area 容器內
                with text_area.container():
                    choice = st.session_state.last_choice
                    rc = st.session_state.reject_count
                    can_filter_dist = choice.get("distance") is not None
                    can_filter_price = choice.get("price") is not None

                    st.markdown(f"<p style='font-size:18px;font-weight:500;margin:0;padding-top:10px;'>吃 <b>{choice['name']}</b> 好嗎？</p>", unsafe_allow_html=True)

                    # 拒絕按鈕灰色
                    st.markdown("""
                    <style>
                    button[data-testid="stBaseButton-tertiary"] {
                        color: #999 !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    btn1, btn2, btn3, spacer = st.columns([1, 1, 1, 3])
                    with btn1:
                        if st.button("不要", key=f"reject_btn_{rc}", type="tertiary"):
                            # 從篩選池移除剛才選的選項，避免重複抽到
                            st.session_state.filtered_pool = [
                                r for r in st.session_state.filtered_pool
                                if r["name"] != choice["name"]
                            ]
                            st.session_state.reject_count += 1
                            if not st.session_state.filtered_pool:
                                st.session_state.last_choice = None
                                st.session_state.pool_exhausted = True
                            elif st.session_state.reject_count < 3:
                                st.session_state.animating = True
                            st.rerun()
                    with btn2:
                        if st.button("太遠", key=f"too_far_{rc}", disabled=not can_filter_dist, type="tertiary"):
                            threshold = choice["distance"]
                            st.session_state.filtered_pool = [
                                r for r in st.session_state.filtered_pool
                                if r.get("distance") is None or r["distance"] < threshold
                            ]
                            st.session_state.reject_count += 1
                            if not st.session_state.filtered_pool:
                                st.session_state.last_choice = None
                                st.session_state.pool_exhausted = True
                            elif st.session_state.reject_count < 3:
                                st.session_state.animating = True
                            st.rerun()
                    with btn3:
                        if st.button("太貴", key=f"too_exp_{rc}", disabled=not can_filter_price, type="tertiary"):
                            threshold = choice["price"]
                            st.session_state.filtered_pool = [
                                r for r in st.session_state.filtered_pool
                                if r.get("price") is None or r["price"] < threshold
                            ]
                            st.session_state.reject_count += 1
                            if not st.session_state.filtered_pool:
                                st.session_state.last_choice = None
                                st.session_state.pool_exhausted = True
                            elif st.session_state.reject_count < 3:
                                st.session_state.animating = True
                            st.rerun()

with col_right:
    st.markdown("<div style='height:110px'></div>", unsafe_allow_html=True)

    def add_restaurant():
        name = st.session_state.restaurant_input
        if name:
            # 取得距離和價格（空字串轉為 None）
            dist_val = st.session_state.get("distance_input")
            price_val = st.session_state.get("price_input")
            distance = int(dist_val) if dist_val else None
            price = int(price_val) if price_val else None

            added = db.add_restaurant(name, distance=distance, price=price)
            if added:
                st.session_state.restaurants = db.get_restaurants()
                st.session_state.restaurant_input = ""
                st.session_state.distance_input = ""
                st.session_state.price_input = ""
            else:
                st.warning("重複了啦!!!")

    st.markdown("<p style='font-size:1.2rem;margin-bottom:2px;margin-top:0;'>餐廳名稱</p>", unsafe_allow_html=True)
    st.text_input("餐廳名稱", key="restaurant_input", label_visibility="collapsed")

    dist_col, price_col = st.columns(2)
    with dist_col:
        st.text_input("距離（公尺）", key="distance_input", label_visibility="visible")
    with price_col:
        st.text_input("價格（元）", key="price_input", label_visibility="visible")

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
                # 組合顯示：名稱 + 距離/價格
                details = []
                if r.get("distance") is not None:
                    details.append(f"{r['distance']}m")
                if r.get("price") is not None:
                    details.append(f"${r['price']}")
                detail_str = f" <span style='color:#888;font-size:12px;'>（{'／'.join(details)}）</span>" if details else ""
                st.markdown(
                    f"<div style='background:#f0f2f6;padding:8px 12px;border-radius:8px;"
                    f"border-left:4px solid #4CAF50;font-size:14px;line-height:1.4;'>"
                    f"{idx}. {r['name']}{detail_str}</div>",
                    unsafe_allow_html=True,
                )
            with btn_col:
                if st.button("❌", key=f"del_{st.session_state.del_generation}_{idx}"):
                    db.remove_restaurant(r["name"])
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

    # 使用篩選後的池子抽選（若為空則用全部餐廳）
    pool = st.session_state.filtered_pool or st.session_state.restaurants

    for _ in range(iterations):
        temp_choice = random.choice(pool)
        text_area.markdown(
            f"<div style='text-align:center; margin-top:12px; font-size:22px; font-weight:600;'>{temp_choice['name']}</div>",
            unsafe_allow_html=True,
        )
        time.sleep(interval)

    # 動畫結束，收集預取結果
    if prefetch_future:
        try:
            st.session_state.prefetched_roast = prefetch_future.result(timeout=10)
        except Exception:
            pass

    final_choice = random.choice(pool)
    st.session_state.last_choice = final_choice

    # 動畫結束，回到靜態圖並顯示結果
    try:
        image_area.image("assets/lot.png", width=640)
    except Exception:
        pass

    st.session_state.animating = False
    st.rerun()
