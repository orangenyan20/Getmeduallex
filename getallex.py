import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from io import StringIO

st.title("medu4 問題番号と単元名まとめ表 自動取得ツール")

# 検索するセクションリスト
sections = [f"100{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"101{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"102{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"103{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"104{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"105{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"106{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"107{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"108{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"109{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"110{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"111{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"112{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"113{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"114{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"115{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"116{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"117{chr(c)}" for c in range(ord('A'), ord('I')+1)] + \
           [f"118{chr(c)}" for c in range(ord('A'), ord('I')+1)]

# 実行ボタン
if st.button("問題番号と単元名を取得開始"):
    result = []

    progress_text = st.empty()
    bar = st.progress(0)

    for i, sec in enumerate(sections):
        progress_text.text(f"\u2B06 {sec} セクションを取得中...")
        consecutive_miss = 0
        page = 1

        while True:
            url = f"https://medu4.com/quizzes/result?page={page}&q={sec}&st=all"
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            
            cards = soup.find_all("a", href=re.compile(r"^/" + sec[:3]))
            if not cards:
                break

            for card in cards:
                href = card.get("href")
                match = re.search(r"(\d{3}[A-Z]\d+)", href)
                if not match:
                    continue

                question_number = match.group(1)
                div_text = card.get_text("\n").split("\n")
                topic = next((x for x in div_text if re.match(r"^\d+\..+", x)), "不明")

                if question_number.startswith(sec):
                    result.append((question_number, topic))
                    consecutive_miss = 0
                else:
                    consecutive_miss += 1
                    if consecutive_miss >= 3:
                        break

            if consecutive_miss >= 3:
                break

            page += 1
            time.sleep(0.5)

        bar.progress((i + 1) / len(sections))

    progress_text.text("\u2705 完了！")
    df = pd.DataFrame(result, columns=["問題番号", "単元名"])

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button("CSVをダウンロード", data=csv_buffer.getvalue(), file_name="medu4_topics.csv", mime="text/csv")
