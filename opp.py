import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Global Production Manager", layout="wide")

# --- 2. 데이터 초기화 (Session State) ---
if 'factory_info' not in st.session_state:
    st.session_state.factory_info = {
        "베트남(VNM)":      {"Region": "Asia", "Main": 30, "Outsourced": 20, "Currency": "VND"},
        "인도네시아(IDN)":   {"Region": "Asia", "Main": 25, "Outsourced": 15, "Currency": "IDR"},
        "미얀마(MMR-내수)":  {"Region": "Asia", "Main": 20, "Outsourced": 10, "Currency": "MMK"},
        "과테말라(GTM)":     {"Region": "Central America", "Main": 20, "Outsourced": 10, "Currency": "GTQ"},
        "니카라과(NIC)":     {"Region": "Central America", "Main": 20, "Outsourced": 5, "Currency": "NIO"},
        "아이티(HTI)":       {"Region": "Central America", "Main": 10, "Outsourced": 5, "Currency": "HTG"}
    }

if 'orders' not in st.session_state:
    st.session_state.orders = []

if 'history_log' not in st.session_state:
    st.session_state.history_log = []

# --- 3. 사이드바 (관리자 & 환율 정보) ---
with st.sidebar:
    st.header("⚙️ 관리자 설정")
    admin_pw = st.text_input("관리자 비밀번호", type="password")
    
    if admin_pw == "1234":
        st.success("인증 성공")
        tab1, tab2 = st.tabs(["Capa 설정", "수정 이력"])
        
        with tab1:
            st.subheader("라인 수(Capa) 수정")
            for factory, info in st.session_state.factory_info.items():
                st.markdown(f"**{factory}**")
                col_m, col_o = st.columns(2)
                new_m = col_m.number_input(f"{factory} 본공장", value=info['Main'], key=f"{factory}_m")
                new_o = col_o.number_input(f"{factory} 외주", value=info['Outsourced'], key=f"{factory}_o")
                
                if new_m != info['Main']:
                    st.session_state.history_log.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "factory": factory, "type": "Main", "old": info['Main'], "new": new_m
                    })
                    st.session_state.factory_info[factory]['Main'] = new_m
                    st.rerun()

                if new_o != info['Outsourced']:
                    st.session_state.history_log.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "factory": factory, "type": "Outsourced", "old": info['Outsourced'], "new": new_o
                    })
                    st.session_state.factory_info[factory]['Outsourced'] = new_o
                    st.rerun()
        
        with tab2:
            st.subheader("수정 이력 로그")
            if st.session_state.history_log:
                st.dataframe(st.session_state.history_log)
            else:
                st.info("수정 이력이 없습니다.")

    st.markdown("---")
    
    # [섹션 2] 환율 정보 대시보드
    st.header("💱 국가별 환율 (USD 기준)")
    st.caption("※ 최근 30일 추이 (Simulation Data)")

    def get_dummy_exchange_data(currency_code):
        dates = pd.date_range(end=datetime.now(), periods=30)
        base_rates = {
            "KRW": 1430, "VND": 25400, "IDR": 16200, "MMK": 2100, 
            "GTQ": 7.8, "NIO": 36.8, "HTG": 132.5
        }
        base = base_rates.get(currency_code, 1000)
        volatility = base * 0.02 
        values = base + np.random.randn(30).cumsum() * (volatility * 0.1)
        return pd.DataFrame({"Rate": values}, index=dates), values[-1], values[-1] - values[-2]

    with st.expander("🇰🇷 대한민국 (KRW)", expanded=True):
        df_krw, cur_krw, del_krw = get_dummy_exchange_data("KRW")
        st.metric(label="USD to KRW", value=f"{cur_krw:,.2f}", delta=f"{del_krw:,.2f}")
        st.line_chart(df_krw, height=100)
        st.link_button("🔍 Google 환율 (KRW)", "https://www.google.com/search?q=USD+to+KRW", use_container_width=True)

    st.markdown("---")

    for factory, info in st.session_state.factory_info.items():
        currency = info.get("Currency", "USD")
        with st.expander(f"{factory} - {currency}", expanded=False):
            df_rate, current_rate, delta = get_dummy_exchange_data(currency)
            st.metric(label=f"USD to {currency}", value=f"{current_rate:,.2f}", delta=f"{delta:,.2f}")
            st.line_chart(df_rate, height=100)
            url = f"https://www.google.com/search?q=USD+to+{currency}+exchange+rate"
            st.link_button(f"🔍 Google 환율 ({currency})", url, use_container_width=True)

# --- 4. 메인 타이틀 ---
st.markdown("<h1 style='text-align: center; font-size: 24px; white-space: nowrap;'>글로벌 생산 관리 시스템</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- 5. 대시보드 (가동 현황) ---
st.subheader("🏭 국가별 공장 가동 현황")

usage_data = {f: {"Main": 0, "Outsourced": 0} for f in st.session_state.factory_info}
for item in st.session_state.orders:
    if item["국가"] in usage_data:
        usage_data[item["국가"]][item["생산구분"]] += item["사용라인"]

cols = st.columns(3)
for idx, (factory, info) in enumerate(st.session_state.factory_info.items()):
    with cols[idx % 3]:
        with st.container(border=True):
            st.markdown(f"**{factory}**")
            m_used = usage_data[factory]["Main"]
            m_total = info['Main']
            if m_used >= m_total and m_total > 0:
                st.markdown(f"본공장: :red[{m_used} / {m_total}]")
            else:
                st.markdown(f"본공장: {m_used} / {m_total}")
            
            o_used = usage_data[factory]["Outsourced"]
            o_total = info['Outsourced']
            if o_used >= o_total and o_total > 0:
                st.markdown(f"외주공장: :red[{o_used} / {o_total}]")
            else:
                st.markdown(f"외주공장: {o_used} / {o_total}")

st.markdown("---")

# --- 6. 생산 오더 입력 ---
st.subheader("📝 생산 오더 입력")

# 6-1. 바이어 및 기업정보 링크
col_buyer, col_link1, col_link2, col_link3, col_link4 = st.columns([2, 1, 1, 1, 1], vertical_alignment="bottom")

with col_buyer:
    buyer = st.text_input("바이어 (Buyer)", placeholder="기업명을 입력하세요")

# 버튼 1: 구글 신용도
with col_link1:
    if buyer:
        google_url = f"https://www.google.com/search?q={buyer}+기업+실적+신용도"
        st.link_button("신용도(구글)", google_url, use_container_width=True)
    else:
        st.button("신용도(구글)", disabled=True, use_container_width=True)

# 버튼 2: Gemini 신용도
with col_link2:
    if buyer:
        gemini_url = "https://gemini.google.com/app"
        st.link_button("신용도(Gemini)", gemini_url, use_container_width=True)
    else:
        st.button("신용도(Gemini)", disabled=True, use_container_width=True)

# 버튼 3: Oritain (TBD)
with col_link3:
    oritain_url = "https://oritain.com"
    st.link_button("Oritain(TBD)", oritain_url, use_container_width=True)

# 버튼 4: Altana 플랫폼
with col_link4:
    altana_url = "https://www.altana.ai"
    st.link_button("Altana 플랫폼", altana_url, use_container_width=True)

if buyer:
    st.caption(f"Tip: Gemini 버튼 클릭 후 **'{buyer} 실적과 신용도 알려줘'** 라고 질문하세요.")

# 6-2. 오더 상세 입력 폼 (원가 포함)
with st.form("order_form"):
    # [1] 스타일 기준 정보
    st.markdown("##### 👕 스타일 기준 정보 입력")
    s1, s2, s3, s4, s5, s6, s7 = st.columns(7)
    with s1: s_name = st.text_input("1.오더명", placeholder="ex) O-123")
    with s2: s_year = st.selectbox("2.연도", [str(y) for y in range(2025, 2031)])
    with s3: s_season = st.selectbox("3.시즌", ["C1", "C2", "C3", "C4"])
    with s4: s_fabric = st.selectbox("4.복종", ["Woven", "Knit", "Synthetic", "Other"])
    with s5: s_cat = st.selectbox("5.카테고리", ["Ladies", "Men", "Adult", "Kids", "Girls", "Boys", "Toddler"])
    with s6: s_prod = st.selectbox("6.생산국가", ["VNM", "IDN", "MMR", "GTM", "NIC", "HTI", "ETC"])
    with s7: s_dest = st.selectbox("7.수출국가", ["USA", "Europe", "Japan", "Korea", "Other"])

    st.markdown("---")
    
    # [2] 원가 등록 (NEW)
    st.markdown("##### 💰 예상 원가 등록 (Unit: USD)")
    cost1, cost2, cost3, cost4 = st.columns(4)
    with cost1: c_yarn = st.number_input("1.원사 (Yarn)", min_value=0.0, format="%.2f")
    with cost2: c_fabric = st.number_input("2.원단 (Fabric)", min_value=0.0, format="%.2f")
    with cost3: c_proc = st.number_input("3.원단가공 (Processing)", min_value=0.0, format="%.2f")
    with cost4: c_sew = st.number_input("4.봉제 (Sewing)", min_value=0.0, format="%.2f")
    
    cost5, cost6, cost7, cost_empty = st.columns(4)
    with cost5: c_epw = st.number_input("5.EPW (Washing)", min_value=0.0, format="%.2f")
    with cost6: c_trans = st.number_input("6.운반비 (Transport)", min_value=0.0, format="%.2f")
    with cost7: 
        c_over = st.number_input("7.원가성 배부비용", min_value=0.0, format="%.2f", help="공장관리자, 감가상각비, 수도광열비 등")
    with cost_empty:
        st.empty() # 빈 공간

    st.markdown("---")

    # [3] 수량 및 배정 정보
    c1, c2, c3, c4 = st.columns(4)
    qty = c1.number_input("수량 (Q'ty)", min_value=0, step=100)
    del_date = c2.date_input("납기일", datetime.now())
    country = c3.selectbox("🏭 배정 공장 (Capa 확인용)", list(st.session_state.factory_info.keys()))
    prod_type = c4.selectbox("생산 구분", ["Main", "Outsourced"])
    
    c5, c6 = st.columns([3, 1])
    detail_name = c5.text_input("상세 공장명 (라인 실배정)", placeholder="실제 생산할 공장/라인 이름 입력")
    lines = c6.number_input("필요 라인 수", min_value=1, value=1)

    submitted = st.form_submit_button("오더 등록 (Add Order)", use_container_width=True)

    if submitted:
        if not buyer or not s_name or qty == 0:
            st.error("바이어, 오더명, 수량은 필수 입력 항목입니다.")
        else:
            full_style_code = f"{s_name}_{s_year}_{s_season}_{s_fabric}_{s_cat}_{s_prod}_{s_dest}"
            
            # 원가 합계 계산
            total_cost = c_yarn + c_fabric + c_proc + c_sew + c_epw + c_trans + c_over

            current_u = usage_data[country][prod_type]
            limit = st.session_state.factory_info[country][prod_type]
            
            if current_u + lines > limit:
                st.warning(f"⚠️ 용량 초과 경고! ({country}-{prod_type} 잔여: {limit - current_u})")
            
            new_order = {
                "바이어": buyer, 
                "스타일": full_style_code, 
                "수량": qty,
                "납기일": str(del_date), 
                "국가": country, 
                "생산구분": prod_type,
                "상세공장명": detail_name, 
                "사용라인": lines,
                "원가합계($)": round(total_cost, 2), # 원가 합계 저장
                "원사": c_yarn, "원단": c_fabric, "봉제": c_sew # 주요 원가 정보도 저장
            }
            st.session_state.orders.append(new_order)
            st.success(f"오더 등록 완료! (Style: {full_style_code}, Cost: ${total_cost:.2f})")
            st.rerun()

# --- 7. 리스트 및 엑셀 다운로드 ---
