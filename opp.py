import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import random

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Global Production Manager", layout="wide")

# --- 2. 데이터 초기화 및 10년치 시뮬레이션 데이터 생성 ---
if 'factory_info' not in st.session_state:
    st.session_state.factory_info = {
        "베트남(VNM)":      {"Region": "Asia", "Main": 30, "Outsourced": 20, "Currency": "VND"},
        "인도네시아(IDN)":   {"Region": "Asia", "Main": 25, "Outsourced": 15, "Currency": "IDR"},
        "미얀마(MMR-내수)":  {"Region": "Asia", "Main": 20, "Outsourced": 10, "Currency": "MMK"},
        "과테말라(GTM)":     {"Region": "Central America", "Main": 20, "Outsourced": 10, "Currency": "GTQ"},
        "니카라과(NIC)":     {"Region": "Central America", "Main": 20, "Outsourced": 5, "Currency": "NIO"},
        "아이티(HTI)":       {"Region": "Central America", "Main": 10, "Outsourced": 5, "Currency": "HTG"}
    }

# [기능 추가] 10년치 과거 데이터 자동 생성 (분석 시각화용)
def generate_mock_history():
    mock_data = []
    years = range(2016, 2026) # 10년치
    buyers = ["Target", "Walmart", "Zara", "Gap", "Uniqlo"]
    fabrics = ["Woven", "Knit", "Synthetic", "Other"]
    categories = ["Ladies", "Men", "Kids", "Toddler"]
    destinations = ["USA", "Europe", "Korea", "Japan"]
    
    for _ in range(200): # 200개의 과거 데이터 생성
        yr = str(random.choice(years))
        fab = random.choice(fabrics)
        cat = random.choice(categories)
        ctry = random.choice(list(st.session_state.factory_info.keys()))
        dest = random.choice(destinations)
        qty = random.randint(1000, 50000)
        price = random.uniform(5.0, 25.0)
        
        # 수익성 랜덤 로직
        revenue = qty * price
        cost_ratio = random.uniform(0.7, 0.9) # 원가율 70~90%
        profit = revenue * (1 - cost_ratio)
        
        mock_data.append({
            "바이어": random.choice(buyers),
            "스타일": f"H-{yr}-{random.randint(100,999)}",
            "연도": yr, "시즌": random.choice(["C1","C2","C3"]), 
            "복종": fab, "카테고리": cat, "생산국가": ctry.split('(')[0], "수출국가": dest,
            "수량": qty, "단가": round(price, 2),
            "매출($)": round(revenue, 2),
            "영업이익($)": round(profit, 2),
            "이익률(%)": round((profit/revenue)*100, 1),
            "국가": ctry, "생산구분": random.choice(["Main", "Outsourced"]),
            "납기일": f"{yr}-06-15", "상태": "Confirmed"
        })
    return mock_data

if 'orders' not in st.session_state:
    # 초기 실행 시 시뮬레이션 데이터 로드
    st.session_state.orders = generate_mock_history()

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
    if item["국가"] in usage_data and str(item.get('연도')) == str(datetime.now().year): # 현재 연도 기준 가동률
        usage_data[item["국가"]][item["생산구분"]] += int(item.get("사용라인", 0))

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

# --- 5-1. 실시간 CCTV ---
st.markdown("---")
st.subheader("🎥 실시간 공장 CCTV 모니터링 (Live Feed)")
cctv_cols = st.columns(3)
dummy_video_url = "https://www.youtube.com/watch?v=Fj0X7c3_9n4" 

for idx, factory in enumerate(st.session_state.factory_info.keys()):
    with cctv_cols[idx % 3]:
        with st.container(border=True):
            st.markdown(f"**{factory}** &nbsp; :red[● REC]", unsafe_allow_html=True)
            st.video(dummy_video_url)
            st.caption(f"📍 Location: {factory} Main Line")

st.markdown("---")

# --- 6. 생산 오더 입력 ---
st.subheader("📝 생산 오더 입력")

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

st.markdown("##### 💰 예상 원가 등록 (Unit: USD)")
cost_c1, cost_c2, cost_c3, cost_c4 = st.columns(4)
c_yarn = cost_c1.number_input("1.원사 (Yarn)", min_value=0.0, format="%.2f", step=0.1)
c_fabric = cost_c2.number_input("2.원단 (Fabric)", min_value=0.0, format="%.2f", step=0.1)
c_proc = cost_c3.number_input("3.원단가공", min_value=0.0, format="%.2f", step=0.1)
c_sew = cost_c4.number_input("4.봉제 (Sewing)", min_value=0.0, format="%.2f", step=0.1)

cost_c5, cost_c6, cost_c7, cost_c8 = st.columns(4)
c_epw = cost_c5.number_input("5.EPW (Embroidery, Printing, Washing)", min_value=0.0, format="%.2f", step=0.1)
c_trans = cost_c6.number_input("6.운반비", min_value=0.0, format="%.2f", step=0.1)
c_over = cost_c7.number_input("7.원가성 배부비용", min_value=0.0, format="%.2f", step=0.1)
c_sga = cost_c8.number_input("➕ 추가 판관비", min_value=0.0, format="%.2f", step=0.1)

# 수익성 계산
est_revenue = qty * unit_price
total_mfg_cost_unit = c_yarn + c_fabric + c_proc + c_sew + c_epw + c_trans + c_over
total_mfg_cost = total_mfg_cost_unit * qty
total_sga = c_sga * qty
op_profit = est_revenue - total_mfg_cost - total_sga
op_margin = (op_profit / est_revenue * 100) if est_revenue > 0 else 0

st.markdown("---")

st.subheader("📊 영업 수익성 분석 (Profitability)")
col_est, col_act = st.columns(2)
with col_est:
    st.info("**[예상 영업수익성] (Pre-shipment)**")
    st.markdown(f"""
    - **예상 매출**: :blue[${est_revenue:,.2f}] ({qty:,} pcs × ${unit_price})
    - **예상 원가**: :red[${total_mfg_cost:,.2f}] (Unit: ${total_mfg_cost_unit:.2f})
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

btn_col1, btn_col2 = st.columns([1, 1])

# [중요] 스타일 코드 대신 개별 데이터로 저장하기 위해 로직 변경
current_u = usage_data[country][prod_type]
limit = st.session_state.factory_info[country][prod_type]
is_capa_full = (current_u + lines > limit)

# 오더 저장 함수
def save_order(status):
    full_style_code = f"{s_name}_{s_year}_{s_season}_{s_fabric}_{s_cat}_{s_prod}_{s_dest}"
    new_order = {
        "바이어": buyer, 
        "스타일": full_style_code, # 화면 표시용
        "오더명": s_name, "연도": s_year, "시즌": s_season, 
        "복종": s_fabric, "카테고리": s_cat, "생산국가": s_prod, "수출국가": s_dest,
        "수량": qty, "단가": unit_price,
        "납기일": str(del_date), "국가": country, "생산구분": prod_type,
        "상세공장명": detail_name, "사용라인": lines,
        "상태": status,
        "매출($)": round(est_revenue, 2),
        "영업이익($)": round(op_profit, 2),
        "이익률(%)": round(op_margin, 1)
    }
    st.session_state.orders.append(new_order)

if btn_col1.button("📝 오더 등록 (Estimated Order)", use_container_width=True):
    if not buyer or not s_name or qty == 0:
        st.error("필수 정보를 입력해주세요.")
    else:
        if is_capa_full: st.warning("Capa 초과 상태입니다.")
        save_order("Estimated")
        st.success("예상 오더 등록 완료!")
        st.rerun()

if btn_col2.button("✅ 오더 확정 (Confirm Order)", type="primary", use_container_width=True):
    if not buyer or not s_name or qty == 0:
        st.error("필수 정보를 입력해주세요.")
    else:
        save_order("Confirmed")
        st.balloons()
        st.success("오더 확정 완료!")
        st.rerun()

# --- 7. 오더 리스트 ---
st.markdown("---")
c_list, c_down = st.columns([4, 1])
c_list.subheader("📋 오더 리스트")

if st.session_state.orders:
    df = pd.DataFrame(st.session_state.orders)
    # 표시할 컬럼 정의
    cols_order = ["상태", "연도", "바이어", "스타일", "수량", "매출($)", "영업이익($)", "이익률(%)", "국가", "납기일"]
    display_cols = [c for c in cols_order if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    excel_data = output.getvalue()
    
    c_down.download_button(
        label="📥 리스트 엑셀 저장",
        data=excel_data,
        file_name="order_list.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("등록된 오더가 없습니다.")

# --- [NEW] 8. 10년치 고급 분석 대시보드 ---
st.markdown("---")
st.subheader("📈 10년치 오더 분석 및 시각화 (Analytics)")

if st.session_state.orders:
    df_anal = pd.DataFrame(st.session_state.orders)
    
    # 8-1. 분석 기준 선택
    anal_col1, anal_col2, anal_col3 = st.columns([1, 1, 2])
    criteria = anal_col1.selectbox("📊 분석 기준 선택", ["바이어", "복종", "카테고리", "생산국가", "수출국가", "시즌"])
    metric = anal_col2.selectbox("📈 시각화 지표", ["매출($)", "영업이익($)", "수량"])
    
    # 8-2. 데이터 가공 (Pivot)
    # 연도별, 기준별로 데이터를 합산(sum)합니다.
    try:
        pivot_df = df_anal.pivot_table(index="연도", columns=criteria, values=metric, aggfunc="sum", fill_value=0)
        
        # 8-3. 꺾은선 그래프 시각화
        st.line_chart(pivot_df)
        
        # 8-4. 분석 데이터 엑셀 다운로드
        st.markdown("##### 📄 분석 데이터 상세 (Table)")
        st.dataframe(pivot_df.style.format("{:,.0f}"), use_container_width=True)
        
        output_anal = io.BytesIO()
        with pd.ExcelWriter(output_anal, engine='xlsxwriter') as writer:
            pivot_df.to_excel(writer, sheet_name='Analytics')
        excel_anal_data = output_anal.getvalue()
        
        anal_col3.download_button(
            label=f"📥 '{criteria}'별 10년치 분석 데이터 엑셀 저장",
            data=excel_anal_data,
            file_name=f"10year_trend_{criteria}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"데이터 분석 중 오류가 발생했습니다: {e}")
        st.caption("충분한 데이터가 쌓여야 분석이 가능합니다.")
else:
    st.info("분석할 데이터가 없습니다.")
