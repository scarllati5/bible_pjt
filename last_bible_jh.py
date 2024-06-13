import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import re

import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG)

def main():
    logging.debug('Program started')
    try:
        # Your main code here
        pass
    except Exception as e:
        logging.error('Error occurred', exc_info=True)

if __name__ == "__main__":
    main()

# 현재 실행 파일의 디렉토리를 찾아 경로 설정
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 파일 경로 설정
bible_dir = resource_path("bible_texts_separated")

# 약어 매핑
abbreviations = {
    "창": "창세기", "출": "출애굽기", "레": "레위기", "민": "민수기", "신": "신명기",
    "수": "여호수아", "삿": "사사기", "룻": "룻기", "삼상": "사무엘상", "삼하": "사무엘하",
    "왕상": "열왕기상", "왕하": "열왕기하", "대상": "역대상", "대하": "역대하", "스": "에스라",
    "느": "느헤미야", "에": "에스더", "욥": "욥기", "시": "시편", "잠": "잠언",
    "전": "전도서", "아": "아가", "사": "이사야", "렘": "예레미야", "애": "예레미야애가",
    "겔": "에스겔", "단": "다니엘", "호": "호세아", "욜": "요엘", "암": "아모스",
    "옵": "오바댜", "욘": "요나", "미": "미가", "나": "나훔", "합": "하박국",
    "습": "스바냐", "학": "학개", "슥": "스가랴", "말": "말라기",
    "마": "마태복음", "막": "마가복음", "눅": "누가복음", "요": "요한복음",
    "행": "사도행전", "롬": "로마서", "고전": "고린도전서", "고후": "고린도후서",
    "갈": "갈라디아서", "엡": "에베소서", "빌": "빌립보서", "골": "골로새서",
    "살전": "데살로니가전서", "살후": "데살로니가후서", "딤전": "디모데전서",
    "딤후": "디모데후서", "딛": "디도서", "몬": "빌레몬서", "히": "히브리서",
    "약": "야고보서", "벧전": "베드로전서", "벧후": "베드로후서",
    "요일": "요한일서", "요이": "요한이서", "요삼": "요한삼서", "유": "유다서",
    "계": "요한계시록"
}

# 성경 버전 명칭
version_names = ["한글개역", "개역개정", "바른성경", "한글KJV", "한글흠정역", "개역개정4판"]

# 선택된 버전 전역 변수
selected_versions = []

# 선택된 버전 설정 함수
def set_selected_versions(version_vars):
    global selected_versions
    selected_versions = [version for version, var in version_vars.items() if var.get()]
    if not selected_versions:
        selected_versions = ["한글KJV"]  # 기본 선택

def search_verse(event=None):
    book_chapter_verse = verse_entry.get().strip()
    set_selected_versions(version_vars)  # 선택된 버전 업데이트
    result_list.delete(*result_list.get_children())
    results = perform_search_verse(book_chapter_verse)
    
    # 중복된 결과를 제거하기 위해 집합을 사용
    seen = set()
    unique_results = []
    for result in results:
        if (result[0], result[2]) not in seen:
            unique_results.append(result)
            seen.add((result[0], result[2]))
    
    for result in unique_results:
        result_list.insert("", tk.END, values=result)
    
    count_label.config(text=f"찾았음: {len(unique_results)} 개")

def perform_search_verse(book_chapter_verse):
    results = []
    try:
        # 여러 구절을 콤마로 구분하여 처리
        verses = book_chapter_verse.split(",")
        for vc in verses:
            vc = vc.strip()
            match = re.match(r"(\D+)(\d*):?(\d*/?\d*)", vc)
            if match:
                book = match.group(1)
                chapter = match.group(2)
                verse_range = match.group(3)
                book = abbreviations.get(book, book)  # 약어 변환

                for version in selected_versions:
                    file_path = os.path.join(bible_dir, f"{version}_{book}.txt")
                    if not os.path.exists(file_path):
                        continue

                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = [line.strip() for line in file if line.strip()]  # 공백 라인 무시
                        if chapter and '/' in verse_range:
                            # 특정 장의 절 범위 검색
                            start_verse, end_verse = map(int, verse_range.split('/'))
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue  # 잘못된 형식 무시
                                chapter_verse, content = parts
                                line_chapter, line_verse = map(int, chapter_verse.split(':'))
                                if line_chapter == int(chapter) and start_verse <= line_verse <= end_verse:
                                    results.append((version, book, chapter_verse, content))
                        elif chapter and verse_range:
                            # 특정 장:절 검색
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue  # 잘못된 형식 무시
                                chapter_verse, content = parts
                                if line.startswith(f"{chapter}:{verse_range} "):
                                    results.append((version, book, chapter_verse, content))
                        elif chapter:
                            # 특정 장 검색
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue  # 잘못된 형식 무시
                                chapter_verse, content = parts
                                if line.startswith(f"{chapter}:"):
                                    results.append((version, book, chapter_verse, content))
                        else:
                            # 책 전체 검색
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue  # 잘못된 형식 무시
                                chapter_verse, content = parts
                                results.append((version, book, chapter_verse, content))
    except Exception as e:
        print(f"오류: {str(e)}")
    return results

# 성경 내용 검색 함수
def search_content(event=None):
    query = content_entry.get().strip()
    set_selected_versions(version_vars)  # 선택된 버전 업데이트
    result_list.delete(*result_list.get_children())
    results = perform_search_content(query)
    for result in results:
        result_list.insert("", tk.END, values=result)
    if not results:
        show_centered_messagebox("검색 결과", "찾을 수 없는 성경내용입니다")
    else:
        for result in unique_results:
            result_list.insert("", tk.END, values=result)
    count_label.config(text=f"찾았음: {len(results)} 개")

def perform_search_content(query):
    results = []
    try:
        queries = query.split(",")
        for q in queries:
            q = q.strip()
            for version in selected_versions:
                for filename in os.listdir(bible_dir):
                    if filename.startswith(version) and filename.endswith(".txt"):
                        book = filename.split("_", 1)[1].split(".")[0]
                        file_path = os.path.join(bible_dir, filename)
                        with open(file_path, 'r', encoding='utf-8') as file:
                            lines = file.readlines()
                            for line in lines:
                                if q in line:
                                    chapter_verse, content = line.strip().split(maxsplit=1)
                                    results.append((version, book, chapter_verse, content))
    except Exception as e:
        print(f"오류: {str(e)}")
    return results

# 결과 저장 함수
def save_results():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as file:
            for row_id in result_list.get_children():
                row = result_list.item(row_id)['values']
                file.write(f"{row[0]} {row[1]} {row[2]}: {row[3]}\n")
        messagebox.showinfo("저장 완료", "결과가 저장되었습니다.")

# 복사 기능 함수
def copy_selection(event=None):
    selected_items = result_list.selection()
    if selected_items:
        clipboard_text = ""
        for item_id in selected_items:
            row = result_list.item(item_id, 'values')
            clipboard_text += f"{row[0]} {row[1]} {row[2]}: {row[3]}\n"
        root.clipboard_clear()
        root.clipboard_append(clipboard_text)

# GUI 구성 요소
root = tk.Tk()
root.title("성경 말씀 구절 / 단어 검색")
root.geometry("1400x800")  # 창 크기 조정

# 창 크기에 따라 가변적으로 조정
root.columnconfigure(0, weight=1)
root.rowconfigure(3, weight=1)

# 성경 버전 선택 프레임
version_frame = tk.Frame(root, bd=4, relief="groove", padx=10, pady=10)
version_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

version_label = tk.Label(version_frame, text="성경 버전 선택 [기본: 한글KJV]", font=("맑은 고딕", 12, "bold"))
version_label.grid(row=0, column=0, columnspan=6, padx=5, sticky="w")

version_vars = {version: tk.BooleanVar() for version in version_names}
version_checks = [tk.Checkbutton(version_frame, text=version, variable=var, font=("맑은 고딕", 12), anchor="w") for version, var in version_vars.items()]

# 체크박스를 보기 좋게 나열하기 위해 열 수를 지정
for i, check in enumerate(version_checks):
    check.grid(row=1, column=i, sticky="w", padx=5, pady=2)

# 검색 프레임
search_frame = tk.Frame(root, bd=4, relief="groove", padx=10, pady=10)
search_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
search_frame.columnconfigure(1, weight=1)
search_frame.columnconfigure(4, weight=1)

# 성경 구절 검색 프레임
verse_frame = tk.Frame(search_frame, bd=2, relief="groove", padx=10, pady=10)
verse_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
verse_frame.columnconfigure(1, weight=1)

verse_label = tk.Label(verse_frame, text="성경 구절 검색", font=("맑은 고딕", 12, "bold"))
verse_label.grid(row=0, column=0, padx=5)

verse_entry = tk.Entry(verse_frame, width=30, font=("맑은 고딕", 12))  # validate 제거
verse_entry.grid(row=0, column=1, padx=5, sticky="ew")
verse_entry.bind("<Return>", search_verse)

verse_button = tk.Button(verse_frame, text="구절 검색", command=search_verse, font=("맑은 고딕", 12, "bold"))
verse_button.grid(row=0, column=2, padx=5)

# 성경 구절 검색 예시
verse_example_label = tk.Label(verse_frame, text="[단일검색 : 창, 창3, 창2:9] [이어서검색 : 요1:1/12] [다중검색(콤마로구분) : 사1:1,마1:1]", font=("맑은 고딕", 9))
verse_example_label.grid(row=1, column=0, columnspan=3, padx=5, sticky="w")

# 성경 내용 검색 프레임
content_frame = tk.Frame(search_frame, bd=2, relief="groove", padx=10, pady=10)
content_frame.grid(row=0, column=3, columnspan=3, padx=10, pady=5, sticky="ew")
content_frame.columnconfigure(1, weight=1)

content_label = tk.Label(content_frame, text="성경 내용 검색", font=("맑은 고딕", 12, "bold"))
content_label.grid(row=0, column=0, padx=5)

content_entry = tk.Entry(content_frame, width=30, font=("맑은 고딕", 12))  # validate 제거
content_entry.grid(row=0, column=1, padx=5, sticky="ew")
content_entry.bind("<Return>", search_content)

content_button = tk.Button(content_frame, text="내용 검색", command=search_content, font=("맑은 고딕", 12, "bold"))
content_button.grid(row=0, column=2, padx=5)

# 성경 내용 검색 예시
content_example_label = tk.Label(content_frame, text="[단일 검색 : 사랑] [다중 검색 (콤마로 구분) : 천국 , 복음 , 영광]", font=("맑은 고딕", 9))
content_example_label.grid(row=1, column=0, columnspan=3, padx=5, sticky="w")

# 창 크기에 따라 가변적으로 조정
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=3)  # 결과 프레임이 있는 row 2의 높이를 늘림
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)
root.rowconfigure(5, weight=1)
root.rowconfigure(6, weight=1)

# 결과 표시 테이블 프레임
result_frame = tk.Frame(root, bd=4, relief="groove", padx=10, pady=10)
result_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
result_frame.columnconfigure(0, weight=1)
result_frame.rowconfigure(0, weight=1)

columns = ("Version", "Book", "Chapter:Verse", "Content")
result_list = ttk.Treeview(result_frame, columns=columns, show="headings", selectmode="extended")
result_list.heading("Version", text="버전")
result_list.heading("Book", text="성경")
result_list.heading("Chapter:Verse", text="장:절")
result_list.heading("Content", text="내용")

result_list.column("Version", width=150, anchor=tk.CENTER, stretch=False)
result_list.column("Book", width=150, anchor=tk.CENTER, stretch=False)
result_list.column("Chapter:Verse", width=100, anchor=tk.CENTER, stretch=False)
result_list.column("Content", width=900, stretch=True)
result_list.grid(row=0, column=0, sticky="nsew")

# 스크롤바 추가
scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=result_list.yview)
result_list.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")

# 테이블 스타일 설정
style = ttk.Style()
style.configure("Treeview", font=("맑은 고딕", 11), rowheight=25)
style.configure("Treeview.Heading", font=("맑은 고딕", 12, "bold"))
style.map("Treeview", background=[('selected', 'gray')])
style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])  # Removing borders
style.configure("Treeview", highlightthickness=0, bd=0, background="white", foreground="black", fieldbackground="white")
style.map('Treeview', background=[('selected', 'gray')], foreground=[('selected', 'black')])

# 행 색상 설정
def set_row_colors():
    for i, item in enumerate(result_list.get_children()):
        if i % 2 == 0:
            result_list.item(item, tags=('evenrow',))
        else:
            result_list.item(item, tags=('oddrow',))
    style.configure('Treeview', rowheight=25, background="white", foreground="black", fieldbackground="white")
    style.map('Treeview', background=[('selected', 'gray')], foreground=[('selected', 'black')])

result_list.tag_configure('oddrow', background='lightgrey')
result_list.tag_configure('evenrow', background='white')

result_list.bind('<<TreeviewSelect>>', lambda e: set_row_colors())

# 복사 기능 추가
result_list.bind("<Button-3>", copy_selection)

# 스크롤바 추가
scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=result_list.yview)
result_list.configure(yscroll=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky="ns")

# 검색 결과 개수 라벨
count_label = tk.Label(root, text="찾았음: 0 개", font=("맑은 고딕", 12, "bold"))
count_label.grid(row=4, column=0, pady=5, sticky="e", padx=10)

# 결과 저장 버튼
save_button = tk.Button(root, text="현재 찾은 내용 저장", command=save_results, font=("맑은 고딕", 12, "bold"))
save_button.grid(row=3, column=0, pady=5, sticky="n")

# 성경 구절 라벨 추가
bible_verse_frame = tk.Frame(root, bd=4, relief="groove", padx=10, pady=10)
bible_verse_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

bible_verse_label = tk.Label(bible_verse_frame, text="네 하나님 여호와를 사랑하고 그의 말씀을 청종하며 또 그를 의지하라 그는 네 생명이시요 네 장수이시니 [신명기30장20절]", font=("맑은 고딕", 12, "bold italic"))
bible_verse_label.pack()

# 하단 오른쪽 텍스트
footer_frame = tk.Frame(root)
footer_frame.grid(row=6, column=0, pady=5, sticky="ew")
footer_frame.columnconfigure(0, weight=1)

separator = ttk.Separator(footer_frame, orient='horizontal')
separator.grid(row=0, column=0, sticky="ew", padx=10)

footer_label = tk.Label(footer_frame, text="By JHS@2024.06", font=("맑은 고딕", 12, "bold italic"))
footer_label.grid(row=1, column=0, pady=5, sticky="e", padx=10)

# 메인 루프 실행
root.mainloop()
