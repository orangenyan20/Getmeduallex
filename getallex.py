import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import unicodedata

st.title("medu4 問題番号と単元名まとめ")

# 検索対象のセクション一覧（例：100A〜101I）
sections = [
    f"{year}{alpha}"
    for year in range(100, 102)  # ←ここを range(100, 119) にすると100A〜118Iになる
    for alpha in "ABCDEFGHI"
]

# セクション選択
selected_sections = st.multiselect("取得するセクションを選んでね（例：100A, 100B...）", sections, default=sections[:3])

if st.button("取得してCSV出力！"):
    
    data = []

    for sec_idx, sec in enumerate(selected_sections):
        st.write(f"\n### ▶ {sec} セクションを取得中...")
        sec_bar = st.progress(0)

        page = 1
        consecutive_miss = 0

        while True:
            url = f"https://medu4.com/quizzes/result?page={page}&q={sec}&st=all"
            res = requests.get(url)
            soup = BeautifulSoup(res.text, "html.parser")
            questions = soup.select("a[href^='/{0}']".format(sec[:3]))

            if not questions:
                break

            found_in_sec = False

            for q in questions:
                q_div = q.find("div", class_='table-list-td')
                if not q_div:
                    continue
                ps = q_div.find_all("p")
                if len(ps) < 3:
                    continue
                number = ps[0].text.strip()
                unit = ps[2].text.strip()

                if number.startswith(sec):
                    data.append([number, unit])
                    found_in_sec = True

            if not found_in_sec:
                consecutive_miss += 1
            else:
                consecutive_miss = 0

            if consecutive_miss >= 3:
                break

            page += 1
            sec_bar.progress(min(1.0, page / 10.0))
            time.sleep(0.5)

    if not data:
        st.warning("データが見つかりません")
    else:
        df = pd.DataFrame(data, columns=["問題番号", "単元名"])
        # 文字化け防止：UTF-8 (BOM付き)でエンコード
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        st.success("CSVファイルが完成したよ！")
        st.download_button("CSVをダウンロードする", data=csv, file_name="medu4_単元まとめ.csv", mime="text/csv")
