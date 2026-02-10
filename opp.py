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
        fab = random.choice(fabrics)
        cat = random.choice(categories)
        ctry = random.choice(list(st.session_state.factory_info.keys()))
        dest = random.choice(destinations)
        qty = random.randint(1000, 50000)
        price = random.uniform(5.0, 25.0)
        revenue = qty * price
        cost_ratio = random.uniform(0.7, 0.9) 
        profit = revenue * (1 - cost_ratio)
        style_no = f"H-{yr}-{random.randint(100,999)}"
        selected_buyer = random.choice(buyers)
        demo_3d_url = f"https://www.google.com/search?q={selected_buyer}+{style_no}+3D+View"

        mock_data.append({
            "바이어": selected_buyer,
            "스타일": style_no,
            "연도": yr, "시즌": random.choice(["C1","C2","C3"]), 
            "복종": fab, "카테고리": cat, "생산국가": ctry.split('(')[0], "수출국가": dest,
            "수량": qty, "단가": round(price, 2),
            "매출($)": round(revenue, 2),
            "영업이익($)": round(profit, 2),
            "이익률(%)": round((profit/revenue)*100, 1),
            "국가": ctry, 
            "생산구분": random.choice(["Main", "Outsourced"]),
            "사용라인": random.randint(1, 5), # [수정] 이 필드가 누락되어 에러가 발생했음
            "납기일": f"{yr}-06-15", "상태": "Confirmed",
            "진행상태": "Store",
            "3D_URL": demo_3d_url
        })
    return mock_data

if 'orders' not in st.session_state:
    st.session_state.orders = generate_mock_history()
if 'history_log' not in st.session_state:
    st.session_state.history_log = []

# --- 3. 사이드바 (핵심 로직 수정) ---
with st.sidebar:
    st.header("⚙️ 관리자 설정")
    admin_pw = st.text_input("관리자 비밀번호", type="password")
    
    if admin_pw == "1452":
        st.success("인증 성공")
        tab1, tab2 = st.tabs(["Capa 설정", "수정 이력"])
        with tab1:
            for factory, info in st.session_state.factory_info.items():
                st.markdown(f"**{factory}**")
                col_m, col_o = st.columns(2)
                # value 변화를 감지하여 바로 session_state 업데이트 (rerun 없이도 반영되도록 설계)
                new_m = col_m.number_input(f"본공장", info['Main'], key=f"{factory}_m_in")
                new_o = col_o.number_input(f"외주", info['Outsourced'], key=f"{factory}_o_in")
                
                if new_m != info['Main']:
                    st.session_state.factory_info[factory]['Main'] = new_m
                if new_o != info['Outsourced']:
                    st.session_state.factory_info[factory]['Outsourced'] = new_o

# --- 4. 메인 대시보드 (KeyError 방지) ---
st.title("🏭 글로벌 공급망 관리 시스템")

st.subheader("📊 국가별 공장 가동 현황 (올해 기준)")
usage_data = {f: {"Main": 0, "Outsourced": 0} for f in st.session_state.factory_info}
this_year = str(datetime.now().year)

for item in st.session_state.orders:
    # item.get()을 사용하여 키가 없을 경우의 에러 방지
    f_name = item.get("국가")
    if f_name in usage_data and str(item.get('연도')) == this_year:
        p_type = item.get("생산구분")
        u_line = item.get("사용라인", 0)
        if p_type in usage_data[f_name]:
            usage_data[f_name][p_type] += u_line

cols = st.columns(3)
for idx, (factory, info) in enumerate(st.session_state.factory_info.items()):
    with cols[idx % 3]:
        with st.container(border=True):
            st.markdown(f"**{factory}**")
            m_used, m_total = usage_data[factory]["Main"], info['Main']
            o_used, o_total = usage_data[factory]["Outsourced"], info['Outsourced']
            
            st.write(f"본공장: {m_used} / {m_total}")
            st.progress(min(m_used/m_total, 1.0) if m_total > 0 else 0)
            st.write(f"외주: {o_used} / {o_total}")
            st.progress(min(o_used/o_total, 1.0) if o_total > 0 else 0)

# (이후 오더 입력 및 리스트 출력 코드는 동일하되 '사용라인' 데이터를 확인하며 진행)
