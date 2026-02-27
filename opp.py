import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import random

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Global Supply Chain Manager", layout="wide")

# --- 2. 데이터 초기화 로직 ---
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
    for _ in range(200):
        yr = str(random.choice(years))
        selected_buyer = random.choice(buyers)
        style_no = f"H-{yr}-{random.randint(100,999)}"
        ctry = random.choice(list(st.session_state.factory_info.keys()))
        qty = random.randint(1000, 50000)
        price = random.uniform(5.0, 25.0)
        revenue = qty * price
        profit = revenue * (1 - random.uniform(0.7, 0.9))
        
        mock_data.append({
            "바이어": selected_buyer, "스타일": style_no, "연도": yr, "시즌": random.choice(["C1","C2","C3"]),
            "복종": random.choice(["Woven", "Knit"]), "카테고리": random.choice(["Ladies", "Men"]),
            "생산국가": ctry.split('(')[0], "수출국가": random.choice(["USA", "Europe"]),
            "수량": qty, "단가": round(price, 2), "매출($)": round(revenue, 2), "영업이익($)": round(profit, 2),
            "이익률(%)": round((profit/revenue)*100, 1), "국가": ctry, "생산구분": random.choice(["Main", "Outsourced"]),
            "사용라인": random.randint(1, 5), "납기일": f"{yr}-06-15", "상태": "Confirmed", "진행상태": "Store",
            "3D_URL": f"https://www.google.com/search?q={selected_buyer}+{style_no}+3D",
            "ESG_Carbon": random.randint(10, 100)
        })
    return mock_data

if 'orders' not in st.session_state:
    st.session_state.orders = generate_mock_history()
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = [] # 판매 데이터 시뮬레이션 생략 가능

# --- 3. 사이드바: 관리자 및 환율 ---
with st.sidebar:
    st.header("⚙️ 관리자 설정")
    admin_pw = st.text_input("비밀번호", type="password")
    if admin_pw == "1452":
        st.success("인증 성공")
        # Capa 수정 로직
    
    st.markdown("---")
    st.header("💱 국가별 환율")
    # 환율 그래프 시뮬레이션 (기존 코드와 동일)
    st.metric("USD to KRW", "1,430.50", delta="2.10")

# --- 4. 메인: 가동 현황 & CCTV ---
st.title("🌐 글로벌 공급망 통합 관리 시스템")
st.markdown("---")

# 가동 현황 레이아웃
st.subheader("🏭 국가별 공장 가동 현황")
usage_data = {f: {"Main": 0, "Outsourced": 0} for f in st.session_state.factory_info}
for item in st.session_state.orders:
    if item["국가"] in usage_data and str(item.get('연도')) == "2025":
        usage_data[item["국가"]][item["생산구분"]] += item.get("사용라인", 0)

cols = st.columns(3)
for idx, (factory, info) in enumerate(st.session_state.factory_info.items()):
    with cols[idx % 3]:
        with st.container(border=True):
            st.markdown(f"**{factory}**")
            m_used, m_total = usage_data[factory]["Main"], info['Main']
            o_used, o_total = usage_data[factory]["Outsourced"], info['Outsourced']
            st.write(f"본공장: {m_used}/{m_total} | 외주: {o_used}/{o_total}")
            st.progress(min(m_used/m_total, 1.0) if m_total > 0 else 0)

# CCTV 모니터링 섹션
st.markdown("---")
st.subheader("🎥 실시간 공장 CCTV (Live)")
cctv_cols = st.columns(3)
for idx, factory in enumerate(st.session_state.factory_info.keys()):
    with cctv_cols[idx % 3]:
        with st.container(border=True):
            st.markdown(f"**{factory}** :red[● LIVE]")
            st.video("https://www.youtube.com/watch?v=Fj0X7c3_9n4") # Dummy Video

# --- 5. 상세 오더 입력 및 원가 계산 ---
st.markdown("---")
st.subheader("📝 생산 오더 및 원가 등록")
with st.expander("신규 오더 상세 입력창", expanded=False):
    # 바이어 및 링크
    b_col1, b_col2 = st.columns([2, 2])
    buyer = b_col1.text_input("바이어 명")
    s_3d_url = b_col2.text_input("3D 이미지 URL (Repository)")
    
    # 세부 정보
    s1, s2, s3, s4, s5 = st.columns(5)
    s_name = s1.text_input("오더명")
    s_year = s2.selectbox("연도", ["2025", "2026"])
    qty = s3.number_input("수량", min_value=0)
    u_price = s4.number_input("단가($)", min_value=0.0)
    lines = s5.number_input("필요 라인", min_value=1)

    st.markdown("##### 💰 세부 원가 구성 (Costing)")
    r1, r2, r3 = st.columns(3)
    c_yarn = r1.number_input("원사비($)", min_value=0.0)
    c_fabric = r2.number_input("원단비($)", min_value=0.0)
    c_sew = r3.number_input("봉제공임($)", min_value=0.0)
    
    # 계산 로직
    est_rev = qty * u_price
    total_cost = (c_yarn + c_fabric + c_sew) * qty
    op_profit = est_rev - total_cost

    # 물류 프로세스 선택
    st.markdown("##### 🚀 물류 진행 단계")
    progress_steps = ["Planning", "Yarn", "Fabric", "Sewing", "Inspection", "Ex-Factory", "Shipped", "Store"]
    current_stage = st.select_slider("현재 공정", options=progress_steps)

    if st.button("🚀 오더 확정 및 시스템 등록", type="primary", use_container_width=True):
        new_order = {
            "바이어": buyer, "스타일": s_name, "연도": s_year, "수량": qty, "단가": u_price,
            "매출($)": est_rev, "영업이익($)": op_profit, "이익률(%)": (op_profit/est_rev*100) if est_rev>0 else 0,
            "국가": "베트남(VNM)", "생산구분": "Main", "사용라인": lines, "상태": "Confirmed", 
            "진행상태": current_stage, "3D_URL": s_3d_url, "ESG_Carbon": qty * 0.05
        }
        st.session_state.orders.append(new_order)
        st.balloons()
        st.rerun()

# --- 6. 데이터 리스트 및 분석 ---
st.markdown("---")
st.subheader("📋 오더 마스터 리스트")
df_final = pd.DataFrame(st.session_state.orders)
st.dataframe(
    df_final,
    column_config={"3D_URL": st.column_config.LinkColumn("3D Look", display_text="🧊 View 3D")},
    use_container_width=True
)

# M365 Copilot 가이드 (1월 업데이트 핵심)
st.markdown("---")
with st.expander("🤖 M365 Copilot 분석용 프롬프트 복사"):
    st.info("엑셀 다운로드 후 아래 프롬프트를 Copilot에 붙여넣으세요.")
    st.code(f"이 엑셀의 {s_year}년도 데이터를 분석해서 바이어별 영업이익 기여도를 차트로 그려줘.", language="text")
