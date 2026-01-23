import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Global Production Manager", layout="wide")

# --- 2. 데이터 초기화 (Session State) ---
# 웹은 새로고침하면 데이터가 날아가므로, Session State에 저장해야 함
if 'factory_info' not in st.session_state:
    st.session_state.factory_info = {
        "베트남(VNM)":      {"Region": "Asia", "Main": 30, "Outsourced": 20},
        "인도네시아(IDN)":   {"Region": "Asia", "Main": 25, "Outsourced": 15},
        "미얀마(MMR-내수)":  {"Region": "Asia", "Main": 20, "Outsourced": 10},
        "과테말라(GTM)":     {"Region": "Central America", "Main": 20, "Outsourced": 10},
        "니카라과(NIC)":     {"Region": "Central America", "Main": 20, "Outsourced": 5},
        "아이티(HTI)":       {"Region": "Central America", "Main": 10, "Outsourced": 5}
    }

if 'orders' not in st.session_state:
    st.session_state.orders = []

if 'history_log' not in st.session_state:
    st.session_state.history_log = []

# --- 3. 사이드바 (관리자 모드) ---
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
                
                # Main Capa 수정
                new_m = col_m.number_input(f"{factory} 본공장", value=info['Main'], key=f"{factory}_m")
                # Outsourced Capa 수정
                new_o = col_o.number_input(f"{factory} 외주", value=info['Outsourced'], key=f"{factory}_o")
                
                # 변경 감지 및 저장
                if new_m != info['Main']:
                    st.session_state.history_log.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "factory": factory, "type": "Main", 
                        "old": info['Main'], "new": new_m
                    })
                    st.session_state.factory_info[factory]['Main'] = new_m
                    st.rerun()

                if new_o != info['Outsourced']:
                    st.session_state.history_log.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "factory": factory, "type": "Outsourced", 
                        "old": info['Outsourced'], "new": new_o
                    })
                    st.session_state.factory_info[factory]['Outsourced'] = new_o
                    st.rerun()
        
        with tab2:
            st.subheader("수정 이력 로그")
            if st.session_state.history_log:
                st.dataframe(st.session_state.history_log)
            else:
                st.info("수정 이력이 없습니다.")

# --- 4. 메인 타이틀 ---
st.markdown("<h1 style='text-align: center;'>글로벌 생산 관리 시스템</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- 5. 대시보드 (가동 현황) ---
st.subheader("🏭 국가별 공장 가동 현황")

# 현재 사용량 계산
usage_data = {f: {"Main": 0, "Outsourced": 0} for f in st.session_state.factory_info}
for item in st.session_state.orders:
    if item["국가"] in usage_data:
        usage_data[item["국가"]][item["생산구분"]] += item["사용라인"]

# 대시보드 카드 그리기 (3열로 배치)
cols = st.columns(3)
for idx, (factory, info) in enumerate(st.session_state.factory_info.items()):
    with cols[idx % 3]:
        with st.container(border=True):
            st.markdown(f"**{factory}**")
            
            # 본공장 상태
            m_used = usage_data[factory]["Main"]
            m_total = info['Main']
            m_color = "red" if m_used >= m_total and m_total > 0 else "black"
            st.markdown(f"본공장: :{m_color}[{m_used} / {m_total}]")
            
            # 외주공장 상태
            o_used = usage_data[factory]["Outsourced"]
            o_total = info['Outsourced']
            o_color = "red" if o_used >= o_total and o_total > 0 else "black"
            st.markdown(f"외주공장: :{o_color}[{o_used} / {o_total}]")

st.markdown("---")

# --- 6. 생산 오더 입력 폼 ---
st.subheader("📝 생산 오더 입력")

with st.form("order_form"):
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    buyer = c1.text_input("바이어 (Buyer)")
    style = c2.text_input("스타일 (Style)")
    qty = c3.number_input("수량 (Q'ty)", min_value=0, step=100)
    del_date = c4.date_input("납기일", datetime.now())

    c5, c6, c7, c8 = st.columns([1.5, 1, 1.5, 1])
    country = c5.selectbox("국가 선택", list(st.session_state.factory_info.keys()))
    prod_type = c6.selectbox("생산 구분", ["Main", "Outsourced"])
    detail_name = c7.text_input("상세 공장명", "공장 이름 입력")
    lines = c8.number_input("필요 라인", min_value=1, value=1)

    submitted = st.form_submit_button("오더 등록 (Add Order)", use_container_width=True)

    if submitted:
        if not buyer or not style or qty == 0:
            st.error("바이어, 스타일, 수량을 정확히 입력해주세요.")
        else:
            # Capa Check
            current_u = usage_data[country][prod_type]
            limit = st.session_state.factory_info[country][prod_type]
            
            if current_u + lines > limit:
                st.warning(f"⚠️ 용량 초과 경고! (잔여: {limit - current_u} / 필요: {lines}) 하지만 등록은 진행됩니다.")
            
            # 데이터 저장
            new_order = {
                "바이어": buyer, "스타일": style, "수량": qty,
                "납기일": str(del_date), "국가": country, "생산구분": prod_type,
                "상세공장명": detail_name, "사용라인": lines
            }
            st.session_state.orders.append(new_order)
            st.success(f"{buyer} 오더가 등록되었습니다.")
            st.rerun()

# --- 7. 외부 링크 (Google / Gemini) ---
# 웹 환경에서는 webbrowser 모듈 대신 링크 버튼을 사용해야 함
if buyer:
    st.markdown("##### 🔗 기업 정보 조회")
    gc1, gc2 = st.columns(2)
    
    # 구글 링크 생성
    google_url = f"https://www.google.com/search?q={buyer}+기업+실적+신용도"
    gc1.link_button(f"🔍 Google: {buyer} 조회", google_url, use_container_width=True)
    
    # Gemini 링크 (단순 이동)
    gemini_url = "https://gemini.google.com/app"
    gc2.link_button("✨ Gemini 열기", gemini_url, use_container_width=True)
    st.caption("※ Gemini는 링크 클릭 후 '바이어 이름 + 실적/신용도 알려줘'라고 직접 입력하세요.")

# --- 8. 리스트 및 엑셀 다운로드 ---
st.markdown("---")
c_list, c_down = st.columns([4, 1])
c_list.subheader("📋 오더 리스트")

if st.session_state.orders:
    df = pd.DataFrame(st.session_state.orders)
    st.dataframe(df, use_container_width=True)
    
    # 엑셀 다운로드 로직 (메모리 내 생성)
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
