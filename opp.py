import time
import random
from datetime import datetime

# --- 1. 기본 데이터 구조 및 노드 설정 ---
class Node:
    """공급망의 각 거점(공장, 창고, 항구)을 정의합니다."""
    def __init__(self, name, zone, stock, capacity):
        self.name = name
        self.zone = zone
        self.stock = stock
        self.capacity = capacity
        self.risk_level = random.uniform(0, 1)  # 0: 안전, 1: 매우 위험

    def __repr__(self):
        status = "정상" if self.risk_level < 0.7 else "위험(지연 발생)"
        return f"[{self.name}] 재고: {self.stock}/{self.capacity} | 상태: {status}"

# --- 2. 물류 및 리스크 관리 엔진 ---
class GSCMS_Engine:
    def __init__(self):
        self.nodes = {}
        self.logs = []

    def add_node(self, node):
        self.nodes[node.name] = node

    def get_optimized_route(self, start_node, end_node):
        """리스크와 거리를 고려한 경로 최적화 로직"""
        start = self.nodes[start_node]
        end = self.nodes[end_node]
        
        # 가상의 경로 계산 (리스크가 높으면 우회로 선택)
        total_risk = (start.risk_level + end.risk_level) / 2
        if total_risk > 0.6:
            return "우회 경로(Route-B: 항공 운송)", "High"
        else:
            return "최적 경로(Route-A: 해상 운송)", "Low"

    def execute_transfer(self, sender_name, receiver_name, quantity):
        """재고 이동 실행 및 유효성 검사"""
        sender = self.nodes[sender_name]
        receiver = self.nodes[receiver_name]

        if sender.stock < quantity:
            self._log(f"❌ 오류: {sender_name} 재고 부족 (요청: {quantity}, 보유: {sender.stock})")
            return False

        route, risk_cat = self.get_optimized_route(sender_name, receiver_name)
        
        # 재고 반영
        sender.stock -= quantity
        receiver.stock += quantity
        
        self._log(f"🚚 이동 완료: {sender_name} -> {receiver_name} | 수량: {quantity} | 경로: {route} (리스크: {risk_cat})")
        return True

    def _log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)

    def display_dashboard(self):
        """현재 전체 공급망 상태 출력"""
        print("\n" + "="*50)
        print("📊 GSCMS 실시간 통합 대시보드")
        print("="*50)
        for node in self.nodes.values():
            print(node)
        print("="*50 + "\n")

# --- 3. 시스템 실행 시뮬레이션 ---
def run_simulation():
    system = GSCMS_Engine()

    # 거점 등록 (이름, 지역, 현재 재고, 최대 용량)
    system.add_node(Node("상하이 공장", "Asia", 1200, 2000))
    system.add_node(Node("부산 물류센터", "Asia", 500, 1500))
    system.add_node(Node("LA 항구", "North America", 800, 3000))
    system.add_node(Node("로테르담 터미널", "Europe", 300, 2000))

    # 초기 상태 확인
    system.display_dashboard()

    # 시나리오 1: 아시아 내 재고 최적화
    print("🚀 시나리오 1: 상하이에서 부산으로 원자재 이동")
    system.execute_transfer("상하이 공장", "부산 물류센터", 300)

    # 시나리오 2: 대륙 간 물류 이동 및 리스크 자동 대응
    print("\n🚀 시나리오 2: 부산에서 LA 항구로 제품 수출")
    system.execute_transfer("부산 물류센터", "LA 항구", 600)

    # 시나리오 3: 재고 부족 상황 테스트
    print("\n🚀 시나리오 3: 로테르담 긴급 재고 요청")
    system.execute_transfer("LA 항구", "로테르담 터미널", 2000)

    # 최종 결과 확인
    system.display_dashboard()

if __name__ == "__main__":
    run_simulation()
