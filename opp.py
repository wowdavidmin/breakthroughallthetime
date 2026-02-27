import time
import random
import uuid
from datetime import datetime, timedelta

# --- [상수 및 설정 데이터] ---
REGIONS = ["Asia", "North America", "Europe", "Middle East"]
TRANSPORT_MODES = {
    "SEA": {"speed": 20, "cost_factor": 1.0, "risk_buffer": 0.2},
    "AIR": {"speed": 80, "cost_factor": 5.5, "risk_buffer": 0.05},
    "ROAD": {"speed": 40, "cost_factor": 2.0, "risk_buffer": 0.1}
}

# --- [1. 거점(Node) 및 재고 관리 모듈] ---
class SupplyChainNode:
    def __init__(self, name, region, initial_stock, capacity):
        self.node_id = str(uuid.uuid4())[:8]
        self.name = name
        self.region = region
        self.stock = initial_stock
        self.capacity = capacity
        self.base_risk = random.uniform(0.05, 0.15) # 지역 기본 리스크
        self.current_risk = self.base_risk

    def update_risk(self):
        """실시간 리스크 변동 시뮬레이션 (기상, 정치, 파업 등)"""
        fluctuation = random.uniform(-0.05, 0.2)
        self.current_risk = max(0.0, min(1.0, self.base_risk + fluctuation))

    def get_status(self):
        fill_rate = (self.stock / self.capacity) * 100
        status = "정상" if self.current_risk < 0.25 else "주의" if self.current_risk < 0.5 else "위험"
        return {
            "ID": self.node_id,
            "이름": self.name,
            "지역": self.region,
            "재고량": self.stock,
            "가동률": f"{fill_rate:.1f}%",
            "리스크상태": status
        }

# --- [2. 물류 이동 및 최적화 엔진] ---
class LogisticsOptimizer:
    @staticmethod
    def calculate_best_route(origin, destination, priority="COST"):
        """
        리스크와 비용을 고려한 최적 운송 수단 결정
        priority: "COST" (비용 중심) 또는 "SPEED" (속도 중심)
        """
        combined_risk = origin.current_risk + destination.current_risk
        
        # 리스크가 임계값을 넘으면 무조건 가장 안전한 AIR(항공) 모드 강제
        if combined_risk > 0.6:
            return "AIR", "안전을 위한 우회 경로 선택"
        
        if priority == "SPEED":
            return "AIR", "긴급 배송 모드"
        else:
            return "SEA" if origin.region != destination.region else "ROAD", "표준 최적 경로"

# --- [3. 통합 관리 시스템 클래스 (Main System)] ---
class GSCMS_Core:
    def __init__(self):
        self.nodes = {}
        self.transaction_history = []
        self.system_log = []

    def register_node(self, node):
        self.nodes[node.name] = node
        self._add_log(f"거점 등록 완료: {node.name} ({node.region})")

    def _add_log(self, message):
        entry = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
        self.system_log.append(entry)
        print(entry)

    def process_order(self, sender_name, receiver_name, amount, priority="COST"):
        """전체 주문 처리 프로세스"""
        if sender_name not in self.nodes or receiver_name not in self.nodes:
            self._add_log("❌ 오류: 등록되지 않은 거점입니다.")
            return

        sender = self.nodes[sender_name]
        receiver = self.nodes[receiver_name]

        # 1. 재고 체크
        if sender.stock < amount:
            self._add_log(f"⚠️ 재고 부족: {sender_name} (보유: {sender.stock}, 요청: {amount})")
            return

        # 2. 리스크 업데이트 및 경로 최적화
        sender.update_risk()
        receiver.update_risk()
        mode, reason = LogisticsOptimizer.calculate_best_route(sender, receiver, priority)

        # 3. 이동 실행
        sender.stock -= amount
        receiver.stock += amount

        # 4. 트랜잭션 기록
        tx_id = str(uuid.uuid4()).upper()[:12]
        tx_data = {
            "TX_ID": tx_id,
            "출발": sender_name,
            "도착": receiver_name,
            "수량": amount,
            "운송수단": mode,
            "사유": reason
        }
        self.transaction_history.append(tx_data)
        self._add_log(f"✅ 주문 처리 완료 [{tx_id}]: {sender_name} -> {receiver_name} ({amount} units via {mode})")

    def print_inventory_report(self):
        print("\n" + "="*80)
        print(f" {datetime.now().year} 글로벌 공급망 통합 재고 현황 리포트 ")
        print("="*80)
        print(f"{'ID':<10} | {'거점명':<15} | {'지역':<12} | {'재고':<8} | {'가동률':<8} | {'상태'}")
        print("-"*80)
        for name, node in self.nodes.items():
            s = node.get_status()
            print(f"{s['ID']:<10} | {s['이름']:<15} | {s['지역']:<12} | {s['재고량']:<10} | {s['가동률']:<8} | {s['리스크상태']}")
        print("="*80 + "\n")

# --- [4. 시스템 구동 시뮬레이션] ---
def main():
    # 시스템 초기화
    gscms = GSCMS_Core()

    # 글로벌 거점 셋업
    gscms.register_node(SupplyChainNode("상하이 본사", "Asia", 10000, 15000))
    gscms.register_node(SupplyChainNode("베트남 공장", "Asia", 5000, 8000))
    gscms.register_node(SupplyChainNode("프랑크푸르트 창고", "Europe", 2000, 5000))
    gscms.register_node(SupplyChainNode("뉴욕 물류센터", "North America", 1500, 6000))

    # 주기적 업무 시뮬레이션
    gscms.print_inventory_report()

    print("\n[업무 프로세스 개시]")
    # 업무 1: 아시아 내 재고 보충
    gscms.process_order("상하이 본사", "베트남 공장", 2000)
    
    # 업무 2: 유럽으로 긴급 수출 (Priority: SPEED)
    gscms.process_order("상하이 본사", "프랑크푸르트 창고", 1500, priority="SPEED")
    
    # 업무 3: 북미 지역 리스크 발생 가정 시뮬레이션
    gscms.process_order("베트남 공장", "뉴욕 물류센터", 3000)

    # 최종 상태 확인
    gscms.print_inventory_report()

if __name__ == "__main__":
    main()
