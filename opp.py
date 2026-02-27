import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. 페이지 설정
st.set_page_config(page_title="Global Apparel Production Manager", layout="wide")

# 2. 초기 데이터 및 설정 (기존 FACTORY_INFO 복원)
if 'FACTORY_INFO' not in st.session_state:
    st.session_state.FACTORY_INFO = {
        "베트남(VNM)":      {"Region": "Asia", "Main": 30, "Outsourced": 20},
        "인도네시아(IDN)":   {"Region": "Asia", "Main": 25, "Outsourced": 15},
        "미얀마(MMR-내수)":  {"Region": "Asia", "Main": 20, "Outsourced": 10},
        "과테말라(GTM)":     {"Region": "Central America", "Main": 20, "Outsourced": 10},
        "니카라과(NIC)":     {"Region": "Central America", "Main": 20, "Outsourced": 5},
        "아이티(HTI)":       {"Region": "Central America", "Main": 10, "Outsourced": 5}
    }

if 'production_data' not in st.session_state:
    st.session_state.production_data = []

# 3. 사이드바 - 관리자 모드 (Admin)
with st.sidebar:
    st.header("⚙️ 시스템 설정 (Admin)")
    admin_pw = st.text_input("관리자 비번", type="password")
    if admin_pw == "1234":
        st.success("인증 완료")
        with st.expander("Capa 설정 변경"):
            for factory, info in st.session_state.FACTORY_INFO.items():
                st.write(f"**{factory}**")
                new_main = st.number_input(f"{factory} 본공장", value=info["Main"], key=f"m_{factory}")
                new_out = st.number_input(f"{factory} 외주", value=info["Outsourced"], key=f"o_{factory}")
                st.session_state.FACTORY_INFO[factory]["Main"] = new_main
                st.session_state.FACTORY_INFO[factory]["Outsourced"] = new_out

# 4. 메인 화면 타이틀
st.title("🏭 글로벌 생산 관리 시스템 (Seoul HQ)")
st.divider()

# 5. 국가별 공장 가동 현황 대시보드
st.subheader("📊 국가별 공장 가동 현황 (사용량 / 전체 Capa)")
usage = {f: {"Main": 0, "Outsourced": 0} for f in st.session_state.FACTORY_INFO}
for item in st.session_state.production_data:
    if item["국가"] in usage:
        usage[item["국가"]][item["생산구분"]] += item["사용라인"]

cols = st.columns(len(st.session_state.FACTORY_INFO))
for i, (factory, info) in enumerate(st.session_state.FACTORY_INFO.items()):
    with cols[i]:
        m_used = usage[factory]["Main"]
        m_capa = info["Main"]
        o_used = usage[factory]["Outsourced"]
        o_capa = info["Outsourced"]
        
        st.markdown(f"**{factory}**")
        st.caption(f"본공장: {m_used} / {m_capa}")
        st.progress(min(m_used/m_capa, 1.0) if m_capa > 0 else 0)
        st.caption(f"외주: {o_used} / {o_capa}")
        st.progress(min(o_used/o_capa, 1.0) if o_capa > 0 else 0)

st.divider()

# 6. 생산 오더 입력 폼
st.subheader("📝 생산 오더 입력")
with st.form("order_form", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns(4)
    buyer = c1.text_input("바이어")
    style = c2.text_input("스타일")
    qty = c3.number_input("수량(Q'ty)", min_value=0, step=100)
    date = c4.date_input("납기일", datetime.now())
    
    c5, c6, c7, c8 = st.columns(4)
    country = c5.selectbox("국가 선택", list(st.session_state.FACTORY_INFO.keys()))
    p_type = c6.selectbox("생산 구분", ["Main", "Outsourced"])
    factory_name = c7.text_input("상세 공장명", value="공장 이름 입력")
    lines = c8.number_input("필요 라인", min_value=1, step=1)
    
    submit = st.form_submit_button("오더 등록 (Add)")
    
    if submit:
        if buyer and style:
            # Capa 체크 로직
            current_total = usage[country][p_type]
            limit = st.session_state.FACTORY_INFO[country][p_type]
            
            if current_total + lines > limit:
                st.warning(f"⚠️ {country} {p_type} Capa 초과! (잔여: {limit-current_total})")
            
            new_order = {
                "바이어": buyer, "스타일": style, "수량": f"{qty:,}",
                "국가": country, "생산구분": p_type, 
                "상세공장명": factory_name, "사용라인": lines, "납기일": str(date)
            }
            st.session_state.production_data.append(new_order)
            st.success("오더가 등록되었습니다.")
            st.rerun()
        else:
            st.error("바이어와 스타일을 입력해주세요.")

# 7. 오더 리스트 및 엑셀 저장
st.subheader("📋 오더 리스트")
if st.session_state.production_data:
    df = pd.DataFrame(st.session_state.production_data)
    st.table(df)
    
    # 엑셀 다운로드 버튼 (Export 기능)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    st.download_button(
        label="📥 엑셀 저장 (Export)",
        data=output.getvalue(),
        file_name=f"production_schedule_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.ms-excel"
    )
else:
    st.write("등록된 오더가 없습니다.")

# 8. 바이어 조회 (Google / Gemini 링크)
st.divider()
st.subheader("🔍 바이어 정보 조회")
search_buyer = st.text_input("조회할 바이어 이름")
col_b1, col_b2 = st.columns(2)
if search_buyer:
    col_b1.link_button("🔍 Google 검색", f"https://www.google.com/search?q={search_buyer}+기업+실적+신용도")
    col_b2.link_button("✨ Gemini 질문", f"https://gemini.google.com/app")
    st.info(f"Tip: Gemini에 접속 후 '{search_buyer} 기업의 최근 실적과 신용도에 대해 알려줘'라고 물어보세요.")
