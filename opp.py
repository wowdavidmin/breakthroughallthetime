import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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
    # [섹션 1] 관리자 설정
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
    
    # [섹션 2] 환율 정보 대시보드 (New)
    st.header("💱 국가별 환율 (USD 기준)")
    st.caption("※ 최근 30일 추이 (Simulation Data)")

    # 환율 데이터 생성 함수 (실제 API 대신 데모용 데이터 생성)
    def get_dummy_exchange_data(currency_code):
        dates = pd.date_range(end=datetime.now(), periods=30)
        # 국가별 대략적인 환율 기준값
        base_rates = {
            "VND": 25400, "IDR": 16200, "MMK": 2100, 
            "GTQ": 7.8, "NIO": 36.8, "HTG": 132.5
        }
        base = base_rates.get(currency_code, 1000)
        # 랜덤 변동폭 생성
        volatility = base * 0.02 
        values = base + np.random.randn(30).cumsum() * (volatility * 0.1)
        
        return pd.DataFrame({"Rate": values}, index=dates), values[-1], values[-1] - values[-2]

    # 각 국가별 환율 카드 생성
    for factory, info in st.session_state.factory_info.items():
        currency = info.get("Currency", "USD")
        
        # 아코디언 형태로 국가별 환율 정보 표시
        with st.expander(f"{factory} - {currency}", expanded=False):
            df_rate, current_rate, delta = get_dummy_exchange_data(currency)
            
            # 1. 현재 환율 지표
            st.metric(
                label=f"USD to {currency}",
                value=f"{current_rate:,.2f}",
                delta=f"{delta:,.2f}"
            )
            
            # 2. 추이 그래프
            st.line_chart(df_rate, height=100)
            
            # 3. 구글 검색 링크
            url = f"https://www.google.com/search?q=USD+to+{currency}+exchange+rate"
            st.link_button(f"🔍 Google 환율 확인 ({currency})", url, use_container_width=True)

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

col_buyer, col_link1, col_link2 = st.columns([2, 1, 1], vertical_alignment="bottom")

with col_buyer:
    buyer = st.text_input("바이어 (Buyer)", placeholder="기업명을 입력하세요")

with col_link1:
    if buyer:
        google_url = f"https://www.google.com/search?q={buyer}+기업+실적+신용도"
        st.link_button("기업 신용도(구글)", google_url, use_container_width=True)
    else:
        st.button("기업 신용도(구글)", disabled=True, use_container_width=True)

with col_link2:
    if buyer:
        gemini_url = "https://gemini.google.com/app"
        st.link_button("기업 신용도(gemini)", gemini_url, use_container_width=True)
    else:
        st.button("기업 신용도(gemini)", disabled=True, use_container_width=True)

if buyer:
    st.caption(f"Tip: Gemini 버튼 클릭 후 입력창에 **'{buyer} 실적과 신용도 알려줘'** 라고 질문하세요.")

with st.form("order_form"):
    c1, c2, c3 = st.columns(3)
    style = c1.text_input("스타일 (Style)")
    qty = c2.number_input("수량 (Q'ty)", min_value=0, step=100)
    del_date = c3.date_input("납기일", datetime.now())

    c4, c5, c6, c7 = st.columns([1.5, 1, 1.5, 1])
    country = c4.selectbox("국가 선택", list(st.session_state.factory_info.keys()))
    prod_type = c5.selectbox("생산 구분", ["Main", "Outsourced"])
    detail_name = c6.text_input("상세 공장명", "공장 이름 입력")
    lines = c7.number_input("필요 라인", min_value=1, value=1)

    submitted = st.form_submit_button("오더 등록 (Add Order)", use_container_width=True)

    if submitted:
        if not buyer or not style or qty == 0:
            st.error("바이어, 스타일, 수량을 정확히 입력해주세요.")
        else:
            current_u = usage_data[country][prod_type]
            limit = st.session_state.factory_info[country][prod_type]
            
            if current_u + lines > limit:
                st.warning(f"⚠️ 용량 초과 경고! (잔여: {limit - current_u} / 필요: {lines}) 하지만 등록은 진행됩니다.")
            
            new_order = {
                "바이어": buyer, "스타일": style, "수량": qty,
                "납기일": str(del_date), "국가": country, "생산구분": prod_type,
                "상세공장명": detail_name, "사용라인": lines
            }
            st.session_state.orders.append(new_order)
            st.success(f"'{buyer}' 오더가 성공적으로 등록되었습니다.")
            st.rerun()

# --- 7. 리스트 및 엑셀 다운로드 ---
st.markdown("---")
c_list, c_down = st.columns([4, 1])
c_list.subheader("📋 오더 리스트")

if st.session_state.orders:
    df = pd.DataFrame(st.session_state.orders)
    st.dataframe(df, use_container_width=True)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    excel_data = output.getvalue()
    
    c_down.download_button(
        label="📥 엑셀로 저장하기",
        data=excel_data,
        file_name="production_schedule_web.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("등록된 오더가 없습니다.")
