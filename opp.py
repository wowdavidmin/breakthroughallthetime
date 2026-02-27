import streamlit as st
import pandas as pd
import random
import uuid
from datetime import datetime

# 1. 페이지 레이아웃 및 스타일 설정
st.set_page_config(page_title="Global Supply Chain Management", layout="wide")

# --- [Core Logic: 1월 27일자 엔진 복원] ---
class SupplyChainNode:
    def __init__(self, name, region, stock, capacity):
        self.node_id = str(uuid.uuid4())[:8]
        self.name = name
        self.region = region
        self.stock = stock
        self.capacity = capacity
        self.base_risk = random.uniform(0.05, 0.2)
        self.current_risk = self.base_risk

    def update_risk(self):
        # 실시간 리스크 변동 시뮬레이션
        self.current_risk = max(0.0, min(1.0, self.base_risk + random.uniform(-0.1, 0.3)))

# --- [Session State: 데이터 유지 설정] ---
if 'system_initialized' not in st.session_state:
    st.session_state.nodes = {
        "상하이 본사": SupplyChainNode("상하이 본사", "Asia", 10000, 15000),
        "베트남 공장": SupplyChainNode("베트남 공장", "Asia", 5000, 8000),
        "프랑크푸르트 창고": SupplyChainNode("프랑크푸르트 창고", "Europe", 2000, 5000),
        "뉴욕 물류센터": SupplyChainNode("뉴욕 물류센터", "North America", 1500, 6000)
    }
    st.session_state.logs = []
    st.session_state.system_initialized = True

# --- [UI Header] ---
st.title("🌐 글로벌 공급망 통합 관리 시스템 (GSCMS)")
st.markdown(f"**시스템 상태:** 온라인 | **기준 시간:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.divider()

# --- [Main Dashboard] ---
# 1. 상단 지표 (KPI Metrics)
col1, col2, col3, col4 = st.columns(4)
total_stock = sum(n.stock for n in st.session_state.nodes.values())
avg_risk = sum(n.current_risk for n in st.session_state.nodes.values()) / len(st.session_state.nodes)

col1.metric("전체 재고량", f"{total_stock:,} 단위")
col2.metric("운영 거점", f"{len(st.session_state.nodes)}개소")
col3.metric("평균 리스크 지수", f"{avg_risk:.2f}")
col4.metric("시스템 건전성", "Stable", delta="Good")

# 2. 거점 현황 테이블 (데이터 시각화)
st.subheader("📊 글로벌 거점 실시간 현황")
node_list = []
for name, node in st.session_state.nodes.items():
    node.update_risk() # 화면 갱신 때마다 리스크 업데이트
    fill_rate = (node.stock / node.capacity) * 100
    status = "🔴 위험" if node.current_risk > 0.4 else "🟡 주의" if node.current_risk > 0.2 else "🟢 정상"
    node_list.append({
        "거점명": node.name,
        "지역": node.region,
        "현재 재고": f"{node.stock:,}",
        "가동률": f"{fill_rate:.1f}%",
        "리스크 지수": round(node.current_risk, 3),
        "상태": status
    })

df = pd.DataFrame(node_list)
st.dataframe(df, use_container_width=True)

# 3. 물류 제어 센터 (사이드바)
with st.sidebar:
    st.header("🚚 물류 이동 제어")
    sender = st.selectbox("출발지(Origin)", list(st.session_state.nodes.keys()))
    receiver = st.selectbox("도착지(Destination)", [k for k in st.session_state.nodes.keys() if k != sender])
    amount = st.number_input("이동 수량", min_value=10, max_value=5000, value=500)
    
    priority = st.radio("우선순위", ["비용 최적화(SEA)", "속도 최적화(AIR)"])
    
    if st.button("재고 이동 확정"):
        s_node = st.session_state.nodes[sender]
        r_node = st.session_state.nodes[receiver]
        
        if s_node.stock >= amount:
            # 로직 실행
            s_node.stock -= amount
            r_node.stock += amount
            
            # 로그 기록
            mode = "AIR" if priority == "속도 최적화(AIR)" or (s_node.current_risk + r_node.current_risk > 0.5) else "SEA/ROAD"
            tx_id = str(uuid.uuid4()).upper()[:8]
            log_entry = f"[{tx_id}] {sender} → {receiver} | {amount}개 이동 완료 (운송모드: {mode})"
            st.session_state.logs.insert(0, log_entry)
            st.success(f"트랜잭션 {tx_id} 성공!")
            st.rerun()
        else:
            st.error("오류: 출발지의 재고가 부족합니다.")

# 4. 하단 시스템 로그
st.divider()
st.subheader("📋 시스템 활동 로그 (최근 5건)")
for log in st.session_state.logs[:5]:
    st.code(log)
