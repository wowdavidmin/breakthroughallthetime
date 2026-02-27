import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
from datetime import datetime
import os
import webbrowser

class ProductionManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Global Apparel Production Manager (Seoul HQ)")
        self.root.geometry("1350x850") # 버튼 추가로 가로폭 약간 확장

        self.FACTORY_INFO = {
            "베트남(VNM)":      {"Region": "Asia", "Main": 30, "Outsourced": 20},
            "인도네시아(IDN)":   {"Region": "Asia", "Main": 25, "Outsourced": 15},
            "미얀마(MMR-내수)":  {"Region": "Asia", "Main": 20, "Outsourced": 10},
            "과테말라(GTM)":     {"Region": "Central America", "Main": 20, "Outsourced": 10},
            "니카라과(NIC)":     {"Region": "Central America", "Main": 20, "Outsourced": 5},
            "아이티(HTI)":       {"Region": "Central America", "Main": 10, "Outsourced": 5}
        }

        self.data = []
        self.history_log = [] 
        self.filename = "production_schedule_final.xlsx"
        self.status_labels = {} 

        self.create_widgets()
        self.update_dashboard_text() 

    def create_widgets(self):
        # 1. 상단 타이틀 영역 (디자인 수정)
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=20, pady=15)
        
        # 관리자 버튼 (오른쪽 배치)
        btn_admin = ttk.Button(top_frame, text="⚙️ 시스템 설정 (Admin)", command=self.open_admin_mode)
        btn_admin.pack(side="right", anchor="n")

        # [변경 1] 메인 타이틀 중앙 정렬 및 폰트 강화
        # pack을 쓰면서 중앙에 두기 위해 Label을 fill="x"로 잡고 anchor="center" 사용
        lbl_title = ttk.Label(top_frame, text="글로벌 생산 관리 시스템", font=("Malgun Gothic", 24, "bold"))
        lbl_title.pack(side="top", anchor="center", expand=True)

        # 2. 대시보드
        self.dash_frame = ttk.LabelFrame(self.root, text="🏭 국가별 공장 가동 현황 (사용량 / 전체 Capa)", padding=5)
        self.dash_frame.pack(fill="x", padx=10, pady=5)
        self.create_dashboard_labels()

        # 3. 입력 폼
        input_frame = ttk.LabelFrame(self.root, text="생산 오더 입력", padding=15)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Row 0
        ttk.Label(input_frame, text="바이어:").grid(row=0, column=0, sticky="e", padx=5)
        self.entry_buyer = ttk.Entry(input_frame, width=15)
        self.entry_buyer.grid(row=0, column=1, padx=5)

        # [변경 2] 기업정보 조회 버튼 2개 배치 (구글 / Gemini)
        # 구글 버튼
        btn_google = ttk.Button(input_frame, text="🔍 Google 검색", command=self.open_google_search, width=12)
        btn_google.grid(row=0, column=2, padx=2) 
        
        # Gemini 버튼
        btn_gemini = ttk.Button(input_frame, text="✨ Gemini 질문", command=self.open_gemini_search, width=12)
        btn_gemini.grid(row=0, column=3, padx=2) 
        
        # 나머지 위젯들 컬럼 번호 이동 (기존보다 오른쪽으로 밀림)
        ttk.Label(input_frame, text="스타일:").grid(row=0, column=4, sticky="e", padx=5)
        self.entry_style = ttk.Entry(input_frame, width=15)
        self.entry_style.grid(row=0, column=5, padx=5)

        ttk.Label(input_frame, text="수량(Q'ty):").grid(row=0, column=6, sticky="e", padx=5)
        self.entry_qty = ttk.Entry(input_frame, width=15)
        self.entry_qty.grid(row=0, column=7, padx=5)

        ttk.Label(input_frame, text="납기일:").grid(row=0, column=8, sticky="e", padx=5)
        self.entry_date = ttk.Entry(input_frame, width=12)
        self.entry_date.grid(row=0, column=9, padx=5)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Row 1 (공장 관련)
        ttk.Label(input_frame, text="국가 선택:").grid(row=1, column=0, sticky="e", padx=5, pady=10)
        self.combo_country = ttk.Combobox(input_frame, values=list(self.FACTORY_INFO.keys()), width=13)
        self.combo_country.grid(row=1, column=1, padx=5, pady=10)
        self.combo_country.current(0)

        # 빈 공간 (버튼 자리만큼 띄우기)
        ttk.Label(input_frame, text="").grid(row=1, column=2, columnspan=2)

        ttk.Label(input_frame, text="생산 구분:").grid(row=1, column=4, sticky="e", padx=5, pady=10)
        self.combo_type = ttk.Combobox(input_frame, values=["Main", "Outsourced"], state="readonly", width=13)
        self.combo_type.grid(row=1, column=5, padx=5, pady=10)
        self.combo_type.current(0)

        ttk.Label(input_frame, text="상세 공장명:").grid(row=1, column=6, sticky="e", padx=5, pady=10)
        self.entry_factory_name = ttk.Entry(input_frame, width=15)
        self.entry_factory_name.grid(row=1, column=7, padx=5, pady=10)
        self.entry_factory_name.insert(0, "공장 이름 입력")

        ttk.Label(input_frame, text="필요 라인:").grid(row=1, column=8, sticky="e", padx=5, pady=10)
        self.entry_lines = ttk.Entry(input_frame, width=5)
        self.entry_lines.grid(row=1, column=9, padx=5, pady=10)
        self.entry_lines.insert(0, "1")

        # 하단 버튼
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=2, column=0, columnspan=10, pady=5)
        ttk.Button(btn_frame, text="오더 등록 (Add)", command=self.add_order).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="엑셀 저장 (Export)", command=self.export_to_excel).pack(side="left", padx=5)

        # 4. 리스트 (Treeview)
        list_frame = ttk.LabelFrame(self.root, text="오더 리스트", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("buyer", "style", "qty", "country", "type", "detail_name", "lines")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=8)
        
        headers = ["바이어", "스타일", "수량", "국가", "구분", "상세 공장명", "라인수"]
        widths = [100, 100, 80, 120, 80, 150, 60]

        for col, h, w in zip(cols, headers, widths):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, anchor="center")
        
        self.tree.pack(fill="both", expand=True)

    # --- 구글 검색 기능 ---
    def open_google_search(self):
        buyer_name = self.entry_buyer.get().strip()
        if not buyer_name:
            messagebox.showwarning("입력 필요", "바이어 이름을 먼저 입력해주세요.")
            return
        
        query = f"{buyer_name} 기업 실적 신용도"
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)

    # --- [NEW] Gemini 바로가기 기능 ---
    def open_gemini_search(self):
        buyer_name = self.entry_buyer.get().strip()
        if not buyer_name:
            messagebox.showwarning("입력 필요", "바이어 이름을 먼저 입력해주세요.")
            return

        # 1. 바이어 이름 클립보드에 복사
        self.root.clipboard_clear()
        self.root.clipboard_append(f"{buyer_name} 기업의 최근 실적과 신용도에 대해 알려줘")
        self.root.update() # 클립보드 반영

        # 2. Gemini 웹사이트 열기
        url = "https://gemini.google.com/app"
        webbrowser.open(url)
        
        messagebox.showinfo("Gemini 열림", f"'{buyer_name}' 관련 질문이 복사되었습니다.\nGemini 입력창에 붙여넣기(Ctrl+V) 하세요.")

    def create_dashboard_labels(self):
        for widget in self.dash_frame.winfo_children():
            widget.destroy()
        
        self.status_labels = {}
        for factory in self.FACTORY_INFO:
            f_frame = ttk.Frame(self.dash_frame, borderwidth=2, relief="groove")
            f_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            ttk.Label(f_frame, text=factory, font=("bold", 10)).pack(pady=(5, 10))

            lbl_main = ttk.Label(f_frame, text="본공장: - / -", font=("Arial", 9))
            lbl_main.pack(anchor="w", padx=10, pady=2)
            
            lbl_out = ttk.Label(f_frame, text="외주 : - / -", font=("Arial", 9))
            lbl_out.pack(anchor="w", padx=10, pady=2)

            self.status_labels[factory] = {"Main": lbl_main, "Outsourced": lbl_out}

    def update_dashboard_text(self):
        usage_data = {f: {"Main": 0, "Outsourced": 0} for f in self.FACTORY_INFO}
        for item in self.data:
            if item["국가"] in usage_data:
                usage_data[item["국가"]][item["생산구분"]] += int(item["사용라인"])

        for factory, labels in self.status_labels.items():
            m_used = usage_data[factory]["Main"]
            m_capa = self.FACTORY_INFO[factory]["Main"]
            m_text = f"본공장: {m_used} / {m_capa}"
            m_color = "red" if m_used >= m_capa and m_capa > 0 else "black"
            labels["Main"].config(text=m_text, foreground=m_color)

            o_used = usage_data[factory]["Outsourced"]
            o_capa = self.FACTORY_INFO[factory]["Outsourced"]
            o_text = f"외주 : {o_used} / {o_capa}"
            o_color = "red" if o_used >= o_capa and o_capa > 0 else "black"
            labels["Outsourced"].config(text=o_text, foreground=o_color)

    def open_admin_mode(self):
        password = simpledialog.askstring("관리자 인증", "관리자 비밀번호를 입력하세요:", show='*')
        if password == "1234":
            self.show_settings_window()
        elif password is None:
            return 
        else:
            messagebox.showerror("인증 실패", "비밀번호가 틀렸습니다.")

    def show_settings_window(self):
        self.settings_win = tk.Toplevel(self.root)
        self.settings_win.title("관리자 모드 (설정 변경 및 수정 이력 조회 가능)")
        self.settings_win.geometry("600x600")
        
        notebook = ttk.Notebook(self.settings_win)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        tab_settings = ttk.Frame(notebook)
        notebook.add(tab_settings, text="Capa 설정 변경")

        tab_history = ttk.Frame(notebook)
        notebook.add(tab_history, text="수정 이력 조회")

        ttk.Label(tab_settings, text="각 국가별 전체 라인 수를 수정하세요.", font=("bold", 10)).pack(pady=10)
        container = ttk.Frame(tab_settings)
        container.pack(pady=5, padx=10, fill="both", expand=True)
        self.capa_entries = {}

        for idx, (factory, info) in enumerate(self.FACTORY_INFO.items()):
            lbl = ttk.Label(container, text=factory, font=("bold", 9))
            lbl.grid(row=idx, column=0, sticky="w", pady=8)
            
            ttk.Label(container, text="본공장:").grid(row=idx, column=1, sticky="e", padx=5)
            entry_main = ttk.Entry(container, width=5)
            entry_main.insert(0, str(info["Main"]))
            entry_main.grid(row=idx, column=2, padx=5)

            ttk.Label(container, text="외주:").grid(row=idx, column=3, sticky="e", padx=5)
            entry_out = ttk.Entry(container, width=5)
            entry_out.insert(0, str(info["Outsourced"]))
            entry_out.grid(row=idx, column=4, padx=5)

            self.capa_entries[factory] = {"Main": entry_main, "Outsourced": entry_out}

        ttk.Button(tab_settings, text="변경사항 저장 (Save)", command=self.save_settings).pack(pady=15)

        cols = ("time", "factory", "type", "old_val", "new_val")
        self.history_tree = ttk.Treeview(tab_history, columns=cols, show="headings")
        
        self.history_tree.heading("time", text="수정 시간")
        self.history_tree.heading("factory", text="국가")
        self.history_tree.heading("type", text="구분")
        self.history_tree.heading("old_val", text="변경 전")
        self.history_tree.heading("new_val", text="변경 후")
        
        self.history_tree.column("time", width=140, anchor="center")
        self.history_tree.column("factory", width=120, anchor="center")
        self.history_tree.column("type", width=70, anchor="center")
        self.history_tree.column("old_val", width=60, anchor="center")
        self.history_tree.column("new_val", width=60, anchor="center")

        self.history_tree.pack(fill="both", expand=True, padx=5, pady=5)

        for log in self.history_log:
            self.history_tree.insert("", "end", values=(log["time"], log["factory"], log["type"], log["old_val"], log["new_val"]))

    def save_settings(self):
        try:
            new_info = {}
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            changes_made = False

            for factory, entries in self.capa_entries.items():
                m_val_str = entries["Main"].get()
                o_val_str = entries["Outsourced"].get()

                if not (m_val_str.isdigit() and o_val_str.isdigit()):
                    raise ValueError(f"{factory}의 값은 모두 숫자여야 합니다.")
                
                new_main = int(m_val_str)
                new_out = int(o_val_str)
                
                old_main = self.FACTORY_INFO[factory]["Main"]
                old_out = self.FACTORY_INFO[factory]["Outsourced"]

                if old_main != new_main:
                    self.history_log.append({
                        "time": current_time, "factory": factory, "type": "Main", 
                        "old_val": old_main, "new_val": new_main
                    })
                    changes_made = True

                if old_out != new_out:
                    self.history_log.append({
                        "time": current_time, "factory": factory, "type": "Outsourced", 
                        "old_val": old_out, "new_val": new_out
                    })
                    changes_made = True

                current_region = self.FACTORY_INFO[factory]["Region"]
                new_info[factory] = {
                    "Region": current_region,
                    "Main": new_main,
                    "Outsourced": new_out
                }

            self.FACTORY_INFO = new_info
            
            self.create_dashboard_labels() 
            self.update_dashboard_text()
            
            if changes_made:
                messagebox.showinfo("완료", "설정이 업데이트되고 이력이 기록되었습니다.")
            else:
                messagebox.showinfo("알림", "변경된 내용이 없습니다.")

            self.settings_win.destroy()
            
        except ValueError as e:
            messagebox.showerror("입력 오류", str(e))

    def add_order(self):
        buyer = self.entry_buyer.get()
        style = self.entry_style.get()
        qty = self.entry_qty.get()
        country = self.combo_country.get()
        prod_type = self.combo_type.get()
        detail_name = self.entry_factory_name.get()
        lines = self.entry_lines.get()

        if not (buyer and style and qty and lines):
            messagebox.showwarning("입력 오류", "필수 항목을 모두 입력하세요.")
            return
        
        if not lines.isdigit() or int(lines) <= 0:
             messagebox.showerror("입력 오류", "라인 수는 1 이상의 숫자여야 합니다.")
             return

        current_used = sum([item['사용라인'] for item in self.data 
                            if item['국가'] == country and item['생산구분'] == prod_type])
        limit = self.FACTORY_INFO[country][prod_type]

        if current_used + int(lines) > limit:
            msg = f"{country} [{prod_type}] 잔여 라인이 부족합니다.\n(잔여: {limit - current_used} / 필요: {lines})\n강제 배정하시겠습니까?"
            if not messagebox.askyesno("Capa 초과 경고", msg):
                return

        row = {
            "바이어": buyer, "스타일": style, "수량": qty,
            "국가": country, "생산구분": prod_type, 
            "상세공장명": detail_name,
            "사용라인": int(lines)
        }
        self.data.append(row)
        
        self.tree.insert("", "end", values=(buyer, style, f"{int(qty):,}", country, prod_type, detail_name, lines))
        
        self.update_dashboard_text()
        self.clear_inputs()

    def clear_inputs(self):
        self.entry_buyer.delete(0, 'end')
        self.entry_style.delete(0, 'end')
        self.entry_qty.delete(0, 'end')
        self.entry_lines.delete(0, 'end')
        self.entry_lines.insert(0, "1")
        self.entry_factory_name.delete(0, 'end')
        self.entry_factory_name.insert(0, "공장 이름 입력")

    def export_to_excel(self):
        if not self.data:
            messagebox.showwarning("알림", "저장할 데이터가 없습니다.")
            return
        try:
            df = pd.DataFrame(self.data)
            df.to_excel(self.filename, index=False)
            messagebox.showinfo("성공", f"엑셀 저장 완료: {self.filename}")
        except Exception as e:
            messagebox.showerror("에러", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductionManagerApp(root)
    root.mainloop()
