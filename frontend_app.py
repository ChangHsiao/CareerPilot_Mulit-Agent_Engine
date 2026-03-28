import streamlit as st
from PIL import Image

# 讀取圖片檔案
logo = Image.open("logo.png")

st.set_page_config(
    page_title="CareerPilot Demo",
    page_icon=logo,
    layout="wide"
)

# 1. 切割版面：建立兩個比例為 1:4 的欄位，並設定內容垂直置中對齊
col1, col2 = st.columns([1, 12], vertical_alignment="center")

# 2. 在第一個欄位 (左側) 放入 Logo
with col1:
    logo = Image.open("logo.png")
    # 設定固定寬度，確保 Logo 不會過度放大而模糊
    st.image(logo, width=80) 

# 3. 在第二個欄位 (右側) 放入專案標題
with col2:
    st.title("CareerPilot - LLM 應用 Demo")

st.markdown("""
### 👉 如何開始？
請從左側的 **[側邊欄 / Sidebar]** 點選您想要測試的模組。
""")
