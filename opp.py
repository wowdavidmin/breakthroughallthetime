import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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
        "아이티(HTI)":       {"Region": "Central America", "Main": 10, "Outsourced": 5, "Currency": "HTG"}
    }

# 10년치 과거 오더 데이터
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
        
        # [수정됨] 바이어를 먼저 선택하여 변수에 저장
        selected_buyer = random.choice(buyers)

        # 저장된 바이어 변수를 사용하여 URL 생성
        demo_3d_url = f"https://www.google.com/search?q={selected_buyer}+{style_no}+3D+View"

        mock_data.append({
            "바이어": selected_buyer, # 위에서 선택한 바이어 사용
            "스타일": style_no,
            "연도": yr, "시즌": random.choice(["C1","C2","C3"]), 
            "복종": fab, "카테고리": cat, "생산국가": ctry.split('(')[0], "수출국가": dest,
            "수량": qty, "단가": round(price, 2),
            "매출($)": round(revenue, 2),
            "영업이익($)": round(profit, 2),
            "이익률(%)": round((profit/revenue)*100, 1),
            "국가": ctry, "생산구분": random.choice(["Main", "Outsourced"]),
            "납기일": f"{yr}-06-15", "상태": "Confirmed",
            "진행상태": "Store",
            "3D_URL": demo_3d_url
        })
    return mock_data

# 10년치 매장 판매 데이터
def generate_mock_sales():
    mock_sales = []
    years = range(2016, 2026)
    buyers = ["Target", "Walmart", "Zara", "Gap", "Uniqlo"]
    categories = ["Ladies", "Men", "Kids", "Toddler"]
    regions = ["North America", "Europe", "Asia Pacific", "Latin America"]
    
    for _ in range(300):
        yr = str(random.choice(years))
        buy = random.choice(buyers)
        cat = random.choice(categories)
        reg = random.choice(regions)
        sold_qty = random.randint(500, 40000)
        retail_price = random.uniform(15.0, 60.0) 
        sales_amt = sold_qty * retail_price
        mock_sales.append({
            "연도": yr, "바이어": buy, "카테고리": cat, "판매지역": reg,
            "판매량(Qty)": sold_qty, "판매금액($)": round(sales_amt, 2),
            "정상가판매율(%)": round(random.uniform(40, 90), 1)
        })
    return mock_sales

if 'orders' not in st.session_state:
    st.session_state.orders = generate_mock_history()
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = generate_mock_sales()
if 'history_log' not in st.session_state:
    st.session_state.history_log = []

# --- 3. 사이드바 ---
with st.sidebar:
    st.header("⚙️ 관리자 설정")
    admin_pw = st.text_input("관리자 비밀번호", type="password")
    
    if admin_pw == "1452":
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
    
    # 환율 정보
    st.header("💱 국가별 환율 (USD 기준)")
    st.caption("※ 최근 30일 추이 (Simulation Data)")

    def get_dummy_exchange_data(currency_code):
        dates = pd.date_range(end=datetime.now(), periods=30)
        base_rates = {"KRW": 1430, "VND": 25400, "IDR": 16200, "MMK": 2100, "GTQ": 7.8, "NIO": 36.8, "HTG": 132.5}
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
            url = f
