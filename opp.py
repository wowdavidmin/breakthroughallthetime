import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import random

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Global Supply Chain Manager", layout="wide")

# --- 2. 데이터 초기화 ---
if 'factory_info' not in st.session_state:
    st.session_state.factory_info = {
        "베트남(VNM)":      {"Region": "Asia", "Main": 30, "Outsourced": 20, "Currency": "VND"},
        "인도네시아(IDN)":   {"Region": "Asia", "Main": 25, "Outsourced": 15, "Currency": "IDR"},
        "미얀마(MMR-내수)":  {"Region": "Asia", "Main": 20, "Outsourced": 10, "Currency": "MMK"},
        "과테말라(GTM)":     {"Region": "Central America", "Main": 20, "Outsourced": 10, "Currency": "GTQ"},
        "니카라과(NIC)":     {"Region": "Central America", "Main": 20, "Outsourced": 5, "Currency": "NIO"},
        "아이티(HTI)":        {"Region": "Central America", "Main": 10, "Outsourced": 5, "Currency": "HTG"}
    }

def generate_mock_history():
    mock_data = []
    years = range(2016, 2026) 
    buyers = ["Target", "Walmart", "Zara", "Gap", "Uniqlo"]
    fabrics = ["Woven", "Knit", "Synthetic", "Other"]
    categories = ["Ladies", "Men", "Kids", "Toddler"]
    destinations = ["USA", "Europe", "Korea", "Japan"]
    
    for _ in range(200): 
        yr = str(random.choice(years))
        style_no = f"H-{yr}-{random.randint(100,999)}"
        selected_buyer = random.choice(buyers)
        ctry = random.choice(list(st.session_state.factory_info.keys()))
        qty = random.randint(1000, 50000)
        price = random.uniform(5.0, 25.0)
        revenue = qty * price
        profit = revenue * (1 - random.uniform(0.7, 0.9))

        mock_data.append({
            "바이어": selected_buyer, "스타일": style_no, "연도": yr, 
            "시즌": random.choice(["C1","C2","C3"]), "복종": random.choice(fabrics),
            "카테고리": random.choice(categories), "생산국가": ctry.split('(')[0], "수출국가": random.choice(destinations),
            "수량": qty, "단가": round(price, 2), "매출($)": round(revenue, 2), "영업이익($)": round(profit, 2),
            "이익률(%)": round((profit/revenue)*100, 1), "국가": ctry, 
            "생산구분": random.choice(["Main", "Outsourced"]), "사용라인": random.randint(1, 4), # 에러 방지 필수 필드
            "납기일": f"{yr}-06-15", "상태": "Confirmed", "진행상태": "Store",
            "3D_URL": f"https://www.google.com/search?q={selected_buyer}+{style_no}+3D+View"
        })
    return mock_data

if 'orders' not in st.session_state:
    st.session_state.orders = generate_mock_history()
if 'history_log' not in st.session_state:
    st.session_state.history_log = []

# --- 3. 사이드바 (Capa & Exchange) ---
with st.sidebar:
    st.header("⚙️ 관리자 설정")
    admin_pw = st.text_input("비밀번호", type="password")
    if admin_pw == "1452":
        st.success("인증 성공")
        for factory, info in st.session_state.factory_info.items():
            st.session_state.factory_info[factory]['Main'] = st.number_input(f"{factory} 본", value=info['Main'])
    
    st.markdown("---")
    st.header("💱 실시간 환율 (Simulation)")
    st.metric("USD to KRW", "1,430.50", delta="2.10")

# --- 4. 메인 대시보드 ---
st.title("🌐 글로벌 공급망 관리 시스템")
st.markdown("---")

# 가동 현황 섹션
st.subheader("🏭 국가별 공장 가동 현황")
this_year = str(datetime.now().year)
usage_data = {f: {"Main": 0, "Outsourced": 0} for f in st.session_state.factory_info}
for item in st.session_state.orders:
    if item["국가"] in usage_data and str(item.get('연도')) == this_year:
        usage_data[item["국가"]][item["생산구분"]] += item.get("사용라인", 0)

cols = st.columns(3)
for idx, (factory, info) in enumerate(st.session_state.factory_info.items()):
    with cols[idx % 3]:
        with st.container(border=True):
            st.markdown(f"**{factory}**")
            m_used, m_total = usage_data[factory]["Main"], info['Main']
            st.write(f"본공장: {m_used} / {m_total}")
            st.progress(min(m_used/m_total, 1.0) if m_total > 0 else 0)

# --- 5. 오더 입력 섹션 ---
st.markdown("---")
st.subheader("📝 생산 오더 입력")
with st.expander("신규 오더 정보 입력", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    buyer = c1.text_input("바이어")
    s_name = c2.text_input("오더명")
    qty = c3.number_input("수량", min_value=0)
    u_price = c4.number_input("단가($)", min_value=0.0)
    s_3d_url = st.text_input("3D 이미지 URL")

    if st.button("✅ 오더 확정 등록", type="primary"):
        new_order = {
            "바이어": buyer, "스타일": s_name, "연도": this_year, "수량": qty, "단가": u_price,
            "매출($)": qty * u_price, "영업이익($)": (qty * u_price) * 0.1, "국가": "베트남(VNM)",
            "생산구분": "Main", "사용라인": 1, "상태": "Confirmed", "진행상태": "Planning", "3D_URL": s_3d_url
        }
        st.session_state.orders.append(new_order)
        st.success("등록되었습니다!")
        st.rerun()

# --- 6. 오더 리스트 & 분석 ---
st.markdown("---")
st.subheader("📋 오더 리스트")
df = pd.DataFrame(st.session_state.orders)
st.dataframe(
    df[["상태", "진행상태", "바이어", "스타일", "3D_URL", "수량", "매출($)", "국가"]],
    column_config={"3D_URL": st.column_config.LinkColumn("3D Look", display_text="🧊 View 3D")},
    use_container_width=True, hide_index=True
)

# M365 Copilot 가이드
with st.expander("🤖 M365 Copilot 활용 프롬프트"):
    st.code("이 엑셀 파일에서 '매출($)'이 가장 높은 상위 3개 바이어를 분석하고 보고서 초안을 작성해줘.", language="text")

# (이후 오더 입력 및 리스트 출력 코드는 동일하되 '사용라인' 데이터를 확인하며 진행)

