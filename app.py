# 스트림릿
import streamlit as st

# 기타 라이브러리
import requests
import pandas as pd
from bs4 import BeautifulSoup

st.set_page_config(layout="centered", page_icon="🔔", page_title="[전략금융] 더벨 모니터링")
st.subheader("[전략금융] 더벨 모니터링")

# 선택 키워드 기반 url 생성
options = st.multiselect("Keywords", ["LS", "엘에스", "이링크", "Essex", "에식스", "SPSX", "예스코", "E1", "LS일렉트릭", "LS전선", "LS에코에너지", "LS엠엔엠", "LS엠트론", "LS머트리얼즈", "EV코리아", "LS증권", "LS마린솔루션", "LS전선아시아"],["LS", "엘에스", "이링크", "Essex", "에식스", "SPSX"], label_visibility="hidden")
period = st.select_slider(
    "period",
    options=["7일", "30일", "60일", "180일", "360일"],
    label_visibility="hidden"
)
# 선택 키워드 기사 취합
total_lst = []
options.extend(["예스코", "E1", "LS일렉트릭", "LS전선", "LS에코에너지", "LS엠엔엠", "LS엠트론", "LS머트리얼즈", "EV코리아", "LS증권", "LS마린솔루션", "LS전선아시아", "디에이링크","디엔에이링크","와이제이링크"])
for key in options:
    url=(f"http://www.thebell.co.kr/free/content/Search.asp?page=&sdt=&period={period[:-1]}&part=A&keyword={key}")
    # response 받아와 파싱 (일단 1개)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    listbox = soup.find("div", "listBox")
    li_lst = listbox.find_all("li")
    for i in range(len(li_lst)):
    # 기사 리스트
        # 기사 요약
        li_lst_a = li_lst[i].find("a")
        # 기사 원본링크
        li_lst_url = "https://www.thebell.co.kr/free/content/"+li_lst_a["href"]
        # 기사 타이틀
        li_lst_title = li_lst_a["title"]
        # 기사 요약
        li_lst_summ = li_lst_a.dd.text.replace("\r\n"," ")
        # 기자 이름
        journalist = listbox.find_all("li")[i].find("span", "user").text.replace("\xa0"," ").strip()
        # 작성 일시
        date = listbox.find_all("li")[i].find("span", "date").text
        # 전체 리스트
        total_lst.append([li_lst_title, li_lst_summ, li_lst_url, journalist, date, key])
        
        
total_df = pd.DataFrame(total_lst, columns=["title","summary", "url", "journalist","date","key"])
total_df = total_df.groupby('url').agg({'title': 'first', 'summary':'first', 'journalist': 'first', 'date': 'first', 'key': lambda x: list(x)}).sort_values("date", ascending=False).reset_index()
total_df = total_df[~total_df['key'].apply(lambda x: '와이제이링크' in x or '디에이링크' in x or '디엔에이링크' in x)].reset_index(drop=True)
###########################################################
total_df["date_dt"] = total_df["date"].str.replace("오전","AM").str.replace("오후","PM")
total_df["date_dt"] = pd.to_datetime(total_df["date_dt"], format='%Y-%m-%d %p %I:%M:%S')

# 날짜별로 행의 개수 세기
date_counts = total_df.groupby(total_df['date_dt'].dt.date).size()

#st.divider()
###########################################################

# 날짜별 행의 개수 시각화
st.caption("※ Beta버전 언급량 시각화는 7일까지만 제공")
st.area_chart(date_counts, color='#FF4B4B', height=130)

# 또는 바 차트를 사용하고 싶다면 아래 코드를 사용
# st.bar_chart(date_counts)

# Custom CSS for pill styling
pill_css = """
<style>
.pill {
    display: inline-block;
    padding: 0.3em 0.9em;
    margin-top: 0em;    /* 위쪽 마진 */
    margin-right: 0.2em;    /* 오른쪽 마진 */
    margin-bottom: 0em; /* 아래쪽 마진 */
    margin-left: 0.2em;     /* 왼쪽 마진 */
    border-radius: 9999px;
    background-color: #FF4B4B;
    color: white;
    font-size: 0.8em;
    font-weight: 700;
}
</style>
"""

# Inject the custom CSS
st.markdown(pill_css, unsafe_allow_html=True)

# Function to create a pill
def create_pill(label):
    return f'<span class="pill">{label}</span>'

# 취합 기사
for x in range(len(total_df)):
    with st.container(height=255, border=True):
        title = total_df["title"][x]
        journalist = total_df["journalist"][x]
        date = total_df["date"][x]
        summary = total_df["summary"][x]
        url = total_df["url"][x]
        keywords = total_df["key"][x]
        st.markdown(
    """<style>
    a {text-decoration: none; color: black !important;}
    a:hover {text-decoration: underline;  /* 마우스를 올리면 밑줄 추가 */}</style>
    """,
    unsafe_allow_html=True)
        st.markdown(f"##### <a href='{url}'>{title}</a>", unsafe_allow_html=True)
        st.caption(journalist+" | "+date)
        st.markdown(f"<a href='{url}'>{summary}</a>", unsafe_allow_html=True)
        pills = [create_pill(label) for label in keywords]
        st.markdown(' '.join(pills), unsafe_allow_html=True)
       


