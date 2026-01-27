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

# 10년치 과거 데이터 자동 생성
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
            "납기일": f"{yr}-06-15", "상태": "Confirmed",
            "진행상태": "Store" 
        })
    return mock_data

if 'orders' not in st.session_state:
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
    if item["국가"] in usage_data and str(item.get('연도')) == str(datetime.now().year):
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

# --- 원가 등록 및 업체명 입력 ---
st.markdown("##### 💰 예상 원가 및 수행 업체 등록 (Cost & Vendors)")
st.caption("각 공정별 예상 단가(USD)와 수행할 업체명(Factory Name)을 입력하세요.")

rc1, rc2, rc3, rc4 = st.columns([1, 1.5, 1, 1.5])
with rc1: c_yarn = st.number_input("1.원사 ($)", min_value=0.0, format="%.2f", step=0.1)
with rc2: v_yarn = st.text_input("원사 업체명", placeholder="Yarn Supplier")
with rc3: c_fabric = st.number_input("2.원단 ($)", min_value=0.0, format="%.2f", step=0.1)
with rc4: v_fabric = st.text_input("원단 업체명", placeholder="Fabric Mill")

rc5, rc6, rc7, rc8 = st.columns([1, 1.5, 1, 1.5])
with rc5: c_proc = st.number_input("3.원단가공 ($)", min_value=0.0, format="%.2f", step=0.1)
with rc6: v_proc = st.text_input("가공 업체명", placeholder="Dyeing/Finishing")
with rc7: c_sew = st.number_input("4.봉제 ($)", min_value=0.0, format="%.2f", step=0.1)
with rc8: v_sew = st.text_input("봉제 공장명", placeholder="Sewing Factory", value=detail_name if detail_name else "") 

rc9, rc10, rc11, rc12 = st.columns([1, 1.5, 1, 1.5])
with rc9: c_epw = st.number_input("5.EPW ($)", min_value=0.0, format="%.2f", step=0.1, help="Embroidery, Printing, Washing")
with rc10: v_epw = st.text_input("EPW 업체명", placeholder="Emb/Print/Wash")
with rc11: c_trans = st.number_input("6.운반비 ($)", min_value=0.0, format="%.2f", step=0.1)
with rc12: v_trans = st.text_input("운송 업체명", placeholder="Logistics")

rc13, rc14, rc15, rc16 = st.columns([1, 1.5, 1, 1.5])
with rc13: c_over = st.number_input("7.배부비용 ($)", min_value=0.0, format="%.2f", step=0.1)
with rc14: st.markdown("*(Internal Cost)*")
with rc15: c_sga = st.number_input("➕ 추가 판관비 ($)", min_value=0.0, format="%.2f", step=0.1)
with rc16: st.markdown("*(SG&A)*")

# 수익성 계산
est_revenue = qty * unit_price
total_mfg_cost_unit = c_yarn + c_fabric + c_proc + c_sew + c_epw + c_trans + c_over
total_mfg_cost = total_mfg_cost_unit * qty
total_sga = c_sga * qty
op_profit = est_revenue - total_mfg_cost - total_sga
op_margin = (op_profit / est_revenue * 100) if est_revenue > 0 else 0

st.markdown("---")

# --- [UPDATED] 1. 오더 진행 현황 (물류 추적 링크 추가) ---
st.subheader("🚀 오더 진행 현황 (Progress Tracking)")

progress_steps = [
    "Planning", "Yarn", "Fabric", "Processing", "Sewing", "EPW", "Inspection", 
    "Ex-Factory", "Shipping Port", "Shipped", "Destination Port", 
    "In-land Trucking", "Warehouse", "Store (Remained Days)"
]

current_stage = st.selectbox("현재 진행 공정을 선택하세요:", progress_steps, index=0)

# 단계별 추적 입력창 (동적 표시)
logistics_info_col1, logistics_info_col2 = st.columns([3, 1])
tracking_url = ""

# 물류 단계일 경우 입력창 활성화
if current_stage in ["Ex-Factory", "Shipping Port", "Shipped", "Destination Port", "In-land Trucking", "Warehouse"]:
    with logistics_info_col1:
        track_no = st.text_input("🚢 운송장 번호 / 선박명 / B/L No (Tracking Info)", placeholder="Tracking Number or Vessel Name")
    
    with logistics_info_col2:
        st.write("")
        st.write("") # 줄맞춤
        
        # 단계별 링크 분기
        if current_stage == "Shipped":
            # MarineTraffic (선박 추적) 예시
            tracking_url = f"https://www.marinetraffic.com/en/ais/home/search:{track_no if track_no else ''}"
            st.link_button("🚢 선박 위치 추적 (MarineTraffic)", tracking_url, use_container_width=True)
            
        elif current_stage in ["Shipping Port", "Destination Port"]:
            # 포트 스케줄 예시 (구글 검색)
            tracking_url = f"https://www.google.com/search?q={track_no}+port+schedule"
            st.link_button("⚓ 항만 스케줄 조회", tracking_url, use_container_width=True)
            
        elif current_stage == "In-land Trucking":
            # 일반 화물 추적 예시
            tracking_url = f"https://www.google.com/search?q={track_no}+tracking"
            st.link_button("🚛 화물 위치 추적", tracking_url, use_container_width=True)

        elif current_stage in ["Ex-Factory", "Warehouse"]:
             # 창고/공장 출고 조회 (예시)
            st.button("🏭 입출고 현황 조회 (WMS)", disabled=True, use_container_width=True)


current_idx = progress_steps.index(current_stage)
progress_value = (current_idx + 1) / len(progress_steps)
st.progress(progress_value)

step_html = ""
for i, step in enumerate(progress_steps):
    color = "blue" if i <= current_idx else "gray"
    weight = "bold" if i == current_idx else "normal"
    marker = "🔵" if i <= current_idx else "⚪"
    display_step = step
    step_html += f"<span style='color:{color}; font-weight:{weight}; font-size:14px'>{marker} {display_step}</span>"
    if i < len(progress_steps) - 1:
        step_html += " &rarr; "
st.markdown(step_html, unsafe_allow_html=True)

if current_stage == "Store (Remained Days)":
    st.write("")
    remained_days = st.number_input("매장 도착까지 남은 일수 (D-Day)", min_value=0, value=7)
    st.info(f"🚚 매장 입고까지 약 **{remained_days}일** 남았습니다.")

st.markdown("---")

# --- 2. 지속가능경영 (ESG) ---
st.subheader("🌿 지속가능경영 (Sustainability)")
sus1, sus2, sus3 = st.columns(3)
with sus1:
    sus_power = st.number_input("전력 (kw)", min_value=0.0, step=100.0)
with sus2:
    sus_water = st.number_input("물 절감 (리터)", min_value=0.0, step=100.0)
with sus3:
    sus_carbon = st.number_input("기타 자원/탄소절감 (kg)", min_value=0.0, step=50.0)

st.caption("*전력, 물 및 기타 자원 절감량을 탄소절감량으로 환산 가능함")

st.markdown("---")

# --- 3. 영업 수익성 분석 ---
st.subheader("📊 영업 수익성 분석")
col_est, col_act = st.columns(2)
with col_est:
    st.info("**[예상 영업수익성] (Pre-shipment)**")
    st.write(f"매출: ${est_revenue:,.2f} / 원가: ${total_mfg_cost:,.2f}")
    st.write(f"**영업이익: ${op_profit:,.2f} ({op_margin:.1f}%)**")

with col_act:
    st.success("**[확정 영업수익성] (Post-shipment)**")
    st.write(f"매출: ${est_revenue:,.2f} / 원가: ${total_mfg_cost:,.2f}")
    st.write(f"**영업이익: ${op_profit:,.2f} ({op_margin:.1f}%)**")

st.write("") 

# --- 버튼 및 저장 로직 ---
btn_col1, btn_col2 = st.columns([1, 1])

current_u = usage_data[country][prod_type]
limit = st.session_state.factory_info[country][prod_type]
is_capa_full = (current_u + lines > limit)

def save_order(status):
    full_style_code = f"{s_name}_{s_year}_{s_season}_{s_fabric}_{s_cat}_{s_prod}_{s_dest}"
    new_order = {
        "바이어": buyer, 
        "스타일": full_style_code, 
        "오더명": s_name, "연도": s_year, "시즌": s_season, 
        "복종": s_fabric, "카테고리": s_cat, "생산국가": s_prod, "수출국가": s_dest,
        "수량": qty, "단가": unit_price,
        "납기일": str(del_date), "국가": country, "생산구분": prod_type,
        "상세공장명": detail_name, "사용라인": lines,
        "상태": status, "진행상태": current_stage,
        "매출($)": round(est_revenue, 2),
        "영업이익($)": round(op_profit, 2),
        "이익률(%)": round(op_margin, 1),
        "V_Yarn": v_yarn, "V_Fabric": v_fabric, "V_Proc": v_proc, 
        "V_Sew": v_sew, "V_EPW": v_epw, "V_Trans": v_trans,
        "ESG_Power": sus_power, "ESG_Water": sus_water, "ESG_Carbon": sus_carbon
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
    cols_order = ["상태", "진행상태", "연도", "바이어", "스타일", "수량", "매출($)", "영업이익($)", "ESG_Carbon", "국가", "납기일"]
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

# --- 8. 오더 분석 및 시각화 ---
st.markdown("---")
st.subheader("📈 오더 분석 및 시각화(최대 10년치)")

if st.session_state.orders:
    df_anal = pd.DataFrame(st.session_state.orders)
    
    anal_col1, anal_col2, anal_col3 = st.columns([1, 1, 2])
    criteria = anal_col1.selectbox("📊 분석 기준 선택", ["바이어", "복종", "카테고리", "생산국가", "수출국가", "시즌"])
    metric = anal_col2.selectbox("📈 시각화 지표", ["매출($)", "영업이익($)", "수량"])
    
    try:
        pivot_df = df_anal.pivot_table(index="연도", columns=criteria, values=metric, aggfunc="sum", fill_value=0)
        
        st.line_chart(pivot_df)
        
        st.markdown("##### 📄 분석 데이터 상세 (Table)")
        st.dataframe(pivot_df.style.format("{:,.0f}"), use_container_width=True)
        
        output_anal = io.BytesIO()
        with pd.ExcelWriter(output_anal, engine='xlsxwriter') as writer:
            pivot_df.to_excel(writer, sheet_name='Analytics')
        excel_anal_data = output_anal.getvalue()
        
        anal_col3.download_button(
            label=f"📥 '{criteria}'별 분석 데이터 엑셀 저장",
            data=excel_anal_data,
            file_name=f"trend_analysis_{criteria}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"데이터 분석 중 오류가 발생했습니다: {e}")
else:
    st.info("분석할 데이터가 없습니다.")
