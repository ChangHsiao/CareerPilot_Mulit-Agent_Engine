import streamlit as st

st.set_page_config(
    page_title="AI 職涯發展系統 Demo",
    page_icon="🤖",
    layout="wide"
)

st.title("🚀 AI 職涯系統 - 前端展示 (無痕模式)")
st.markdown("""
歡迎來到本系統的展示頁面！這裡專為 **本地純前端展示** 設計。

### 🌟 特色
- **完全無痕**：所有的輸入資料與分析報告僅存在您的瀏覽器中。
- **不碰資料庫**：利用前端介面與 Python 運行時期的 Monkey-Patching 技術，將表單輸入直接餵給 CrewAI 代理人，取代原先對 Supabase 的內部查詢。
- **保證安全**：即使您輸入機密履歷資料，在重整網頁或關閉瀏覽器後，便會立刻被銷毀，絕不留痕。

### 👉 如何開始？
請從左側的 **[側邊欄 / Sidebar]** 點選您想要測試的模組。
目前我們已優先為您開放 **「📄 4. 求職信生成」** 模組供您體驗！
""")
