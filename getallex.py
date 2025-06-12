import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import io
from urllib.parse import urljoin

st.title("medu4 問題と単元名 抽出ツール")

# --- ユーザーオプション ---
section_range = st.radio("取得する範囲を選んでね2", ("100A〜101C", "100D〜118I", "全部（時間かかる）"))

start_button = st.button("🔍 抽出スタート")

# --- 設定 ---
HEADERS = {"User-Agent": "Mozilla/5.0"}
BASE_URL = "https://medu4.com"

section_list_all = [
    f"{year}{alpha}" for year in range(100, 119) for alpha in "ABCDEFGHI"
]

section_ranges = {
    "100A〜101C": [s for s in section_list_all if s.startswith("100") or s.startswith("101")],
    "100D〜118I": [s for s in section_list_all if not s.startswith("100") and not s.startswith("101")],
    "全部（時間かかる）": section_list_all
}

def get_quiz_items(section: str):
    quiz_data = []
    max_page = 20  # ページ数の上限（無限ループ防止）
    consecutive_miss = 0  # セクション外データ連続出現カウンタ

    for page in range(1, max_page + 1):
        url = f"https://medu4.com/quizzes/result?page={page}&q={section}&st=all"
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        cards = soup.select("a[href^='/{0}']".format(section))

        page_has_section = False

        for card in cards:
            div = card.find("div", class_="table-list-td")
            if not div:
                continue
            texts = div.find_all("p")
            if len(texts) < 4:
                continue
            q_num = texts[0].text.strip()
            q_section = texts[2].text.strip()

            if section in q_num:
                quiz_data.append({"問題番号": q_num, "単元名": q_section})
                page_has_section = True

        if not page_has_section:
            consecutive_miss += 1
            if consecutive_miss >= 3:
                break
        else:
            consecutive_miss = 0

        time.sleep(0.5)

    return quiz_data

if start_button:
    all_data = []
    sections = section_ranges[section_range]
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, sec in enumerate(sections):
        status_text.text(f"📘 {sec} を取得中...")
        result = get_quiz_items(sec)
        all_data.extend(result)
        progress_bar.progress((idx + 1) / len(sections))

    if all_data:
        df = pd.DataFrame(all_data)
        txt_buffer = io.StringIO()
        df.to_csv(txt_buffer, sep='\t', index=False, encoding='utf-8-sig')

        st.success("✅ 抽出完了！")
        st.download_button(
            label="📥 TXTファイルをダウンロード",
            data=txt_buffer.getvalue(),
            file_name="単元付き問題一覧.txt",
            mime="text/plain"
        )
    else:
        st.warning("⚠️ データが見つかりませんでした…")
