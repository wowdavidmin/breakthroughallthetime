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

# 6-1. 바이어 및 기업정보
col_buyer, col_link1, col_link2, col_link3, col_link4 = st.columns([2, 1, 1, 1, 1], vertical_alignment="bottom")

with col_buyer:
    buyer = st.text_input("바이어 (Buyer)", placeholder="기업명을 입력하세요")
with col_link1:
    if buyer:
        st.link_button("신용도(구글)", f"https://www.google.com/search?q={buyer}+기업+실적+신용도", use_container_width=True)
    else:
        st.button("신용도(구글)", disabled=True, use_container_width=True)
with col_link2:
    if buyer:
        st.link_button("신용도(Gemini)", "https://gemini.google.com/app", use_container_width=True)
    else:
        st.button("신용도(Gemini)", disabled=True, use_container_width=True)
with col_link3:
    st.link_button("Oritain(TBD)", "https://oritain.com", use_container_width=True)
with col_link4:
    st.link_button("Altana 플랫폼", "https://www.altana.ai", use_container_width=True)

if buyer:
    st.caption(f"Tip: Gemini 버튼 클릭 후 **'{buyer} 실적과 신용도 알려줘'** 라고 질문하세요.")

# --- [입력 폼] ---
st.markdown("##### 👕 스타일 기준 정보 입력")
s1, s2, s3, s4, s5, s6, s7 = st.columns(7)
s_name = s1.text_input("1.오더명", placeholder="ex) O-123")
s_year = s2.selectbox("2.연도", [str(y) for y in range(2025, 2031)])
s_season = s3.selectbox("3.시즌", ["C1", "C2", "C3", "C4"])
s_fabric = s4.selectbox("4.복종", ["Woven", "Knit", "Synthetic", "Other"])
s_cat = s5.selectbox("5.카테고리", ["Ladies", "Men", "Adult", "Kids", "Girls", "Boys", "Toddler"])
s_prod = s6.selectbox("6.생산국가", ["VNM", "IDN", "MMR", "GTM", "NIC", "HTI", "ETC"])
s_dest = s7.selectbox("7.수출국가", ["USA", "Europe", "Japan", "Korea", "Other"])

st.markdown("---")

# [수량, 단가, 공장 배정]
c1, c2, c3, c4 = st.columns(4)
qty = c1.number_input("수량 (Q'ty)", min_value=0, step=100)
unit_price = c2.number_input("단가 ($ Unit Price)", min_value=0.0, step=0.1, format="%.2f")
del_date = c3.date_input("납기일", datetime.now())
country = c4.selectbox("🏭 배정 공장", list(st.session_state.factory_info.keys()))

c5, c6, c7 = st.columns([1, 2, 1])
prod_type = c5.selectbox("생산 구분", ["Main", "Outsourced"])
detail_name = c6.text_input("상세 공장명", placeholder="공장/라인 이름 입력")
lines = c7.number_input("필요 라인", min_value=1, value=1)

st.markdown("---")

# [원가 등록 및 수익성 분석]
st.markdown("##### 💰 예상 원가 등록 (Unit: USD)")

# 원가 입력
cost_c1, cost_c2, cost_c3, cost_c4 = st.columns(4)
c_yarn = cost_c1.number_input("1.원사 (Yarn)", min_value=0.0, format="%.2f", step=0.1)
c_fabric = cost_c2.number_input("2.원단 (Fabric)", min_value=0.0, format="%.2f", step=0.1)
c_proc = cost_c3.number_input("3.원단가공", min_value=0.0, format="%.2f", step=0.1)
c_sew = cost_c4.number_input("4.봉제 (Sewing)", min_value=0.0, format="%.2f", step=0.1)

cost_c5, cost_c6, cost_c7, cost_c8 = st.columns(4)
# [수정된 부분] 괄호 안 텍스트 변경
c_epw = cost_c5.number_input("5.EPW (Embroidery, Printing, Washing)", min_value=0.0, format="%.2f", step=0.1)
c_trans = cost_c6.number_input("6.운반비", min_value=0.0, format="%.2f", step=0.1)
c_over = cost_c7.number_input("7.원가성 배부비용", min_value=0.0, format="%.2f", step=0.1, help="공장관리비, 감가상각 등")
c_sga = cost_c8.number_input("➕ 추가 판관비", min_value=0.0, format="%.2f", step=0.1, help="본사 관리비 등 영업비용")

# --- 실시간 수익성 계산 로직 ---
est_revenue = qty * unit_price
total_mfg_cost_unit = c_yarn + c_fabric + c_proc + c_sew + c_epw + c_trans + c_over
total_mfg_cost = total_mfg_cost_unit * qty
total_sga = c_sga * qty
op_profit = est_revenue - total_mfg_cost - total_sga
op_margin = (op_profit / est_revenue * 100) if est_revenue > 0 else 0

st.markdown("---")

# [수익성 분석 대시보드]
st.subheader("📊 영업 수익성 분석 (Profitability)")

col_est, col_act = st.columns(2)

with col_est:
    st.info("**[예상 영업수익성] (Pre-shipment)**")
    st.markdown(f"""
    - **예상 매출**: :blue[${est_revenue:,.2f}] ({qty:,} pcs × ${unit_price})
    - **예상 원가**: :red[${total_mfg_cost:,.2f}] (Unit: ${total_mfg_cost_unit:.2f})
    - **예상 판관비**: :orange[${total_sga:,.2f}]
    - **예상 영업이익**: **${op_profit:,.2f}** ({op_margin:.1f}%)
    """)

with col_act:
    st.success("**[확정 영업수익성] (Post-shipment)**")
    st.caption("※ 오더 확정 버튼 클릭 시, 현재 입력값이 확정치로 저장됩니다.")
    st.markdown(f"""
    - **확정 매출**: :blue[${est_revenue:,.2f}]
    - **확정 원가**: :red[${total_mfg_cost:,.2f}]
    - **확정 영업이익**: **${op_profit:,.2f}** ({op_margin:.1f}%)
    """)

st.write("") 

# [하단 버튼 액션]
btn_col1, btn_col2 = st.columns([1, 1])

full_style_code = f"{s_name}_{s_year}_{s_season}_{s_fabric}_{s_cat}_{s_prod}_{s_dest}"
current_u = usage_data[country][prod_type]
limit = st.session_state.factory_info[country][prod_type]
is_capa_full = (current_u + lines > limit)

# 버튼 1: 예상 오더 등록
if btn_col1.button("📝 오더 등록 (Estimated Order)", use_container_width=True):
    if not buyer or not s_name or qty == 0:
        st.error("바이어, 오더명, 수량은 필수 입력 항목입니다.")
    else:
        if is_capa_full:
            st.warning(f"⚠️ Capa 초과 상태로 등록됩니다. (잔여: {limit - current_u})")
        
        new_order = {
            "바이어": buyer, "스타일": full_style_code, "수량": qty, "단가": unit_price,
            "납기일": str(del_date), "국가": country, "생산구분": prod_type,
            "상세공장명": detail_name, "사용라인": lines,
            "상태": "Estimated",
            "매출($)": round(est_revenue, 2),
            "영업이익($)": round(op_profit, 2),
            "이익률(%)": round(op_margin, 1)
        }
        st.session_state.orders.append(new_order)
        st.success(f"예상 오더 등록 완료! (Profit: ${op_profit:,.0f})")
        st.rerun()

# 버튼 2: 오더 확정
if btn_col2.button("✅ 오더 확정 (Confirm Order)", type="primary", use_container_width=True):
    if not buyer or not s_name or qty == 0:
        st.error("확정할 오더 정보를 정확히 입력해주세요.")
    else:
        new_order = {
            "바이어": buyer, "스타일": full_style_code, "수량": qty, "단가": unit_price,
            "납기일": str(del_date), "국가": country, "생산구분": prod_type,
            "상세공장명": detail_name, "사용라인": lines,
            "상태": "Confirmed",
            "매출($)": round(est_revenue, 2),
            "영업이익($)": round(op_profit, 2),
            "이익률(%)": round(op_margin, 1)
        }
        st.session_state.orders.append(new_order)
        st.balloons()
        st.success(f"오더가 확정되었습니다! (Confirmed Profit: ${op_profit:,.0f})")
        st.rerun()

# --- 7. 리스트 및 엑셀 다운로드 ---
st.markdown("---")
c_list, c_down = st.columns([4, 1])
c_list.subheader("📋 오더 리스트")

if st.session_state.orders:
    df = pd.DataFrame(st.session_state.orders)
    cols_order = ["상태", "바이어", "스타일", "수량", "단가", "매출($)", "영업이익($)", "이익률(%)", "국가", "생산구분", "납기일"]
    display_cols = [c for c in cols_order if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True)
    
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
