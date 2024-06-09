from flask import Flask, request, jsonify, render_template_string, send_file
import os
import re
import logging
from collections import defaultdict

app = Flask(__name__)

# 로깅 설정: 콘솔과 파일 모두에 로그 출력
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()])

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
version_names = ["한글개역", "한글흠정역", "새번역", "KJV_한글KJV"]

# 텍스트 파일 경로
bible_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bible")

@app.route('/')
def index():
    versions = version_names
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>성경 말씀 구절 / 단어 검색</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: '맑은 고딕', sans-serif;
                    margin: 0;
                    padding: 20px;
                    box-sizing: border-box;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: auto;
                    padding: 20px;
                    border: 1px solid #000;
                    border-radius: 15px;
                    background-color: #fff;
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: space-between;
                }
                .section {
                    border: 1px solid #000;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    padding: 10px;
                    box-sizing: border-box;
                }
                .section h3 {
                    margin: 0 0 10px 0;
                    padding: 5px;
                    font-size: 16px;
                    font-weight: bold;
                    background-color: #e5e5e5;
                    border-radius: 5px;
                }
                .section label {
                    display: block;
                    margin: 5px 0;
                }
                .section input[type="text"], 
                .section select, 
                .section button {
                    padding: 5px;
                    margin: 5px 0;
                    font-size: 12pt;
                    box-sizing: border-box;
                }
                .section input[type="text"], 
                .section select {
                    width: calc(100% - 20px);
                }
                .section button {
                    width: calc(100% - 20px);
                }
                .left, .right {
                    width: 48%;
                }
                .results-box {
                    width: 100%;
                    margin-top: 20px;
                    overflow-y: auto;
                    max-height: 150px;
                }
                .results-box h3 {
                    margin: 0 0 10px 0;
                    padding: 5px;
                    font-size: 16px;
                    font-weight: bold;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }
                table, th, td {
                    border-bottom: 1px solid black;
                }
                th, td {
                    padding: 10px;
                    text-align: center;
                    font-size: 10pt;
                    word-wrap: break-word;
                    white-space: pre-line;
                    overflow: hidden;
                }
                th.version, td.version {
                    width: 0.5cm;
                }
                th.book, td.book {
                    width: 1cm;
                }
                th.chapter-verse, td.chapter-verse {
                    width: 1.5cm;
                }
                td.content {
                    text-align: left;
                    background-color: white;
                    white-space: normal;
                    word-break: break-all;
                    cursor: pointer;
                }
                .english-content {
                    font-family: 'Palatino Linotype', serif;
                    font-weight: bold;
                    font-size: 10pt;
                }
                .highlight {
                    background-color: yellow;
                    font-weight: bold;
                }
                .loader {
                    border: 8px solid #f3f3f3;
                    border-radius: 50%;
                    border-top: 8px solid #3498db;
                    width: 40px;
                    height: 40px;
                    display: inline-block;
                    position: relative;
                    margin: 10px auto;
                }
                .loader-text {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 12px;
                    font-weight: bold;
                    animation: none;
                }
                .hidden {
                    display: none;
                }
                .search-box {
            margin-bottom: 0.5cm; /* 아래쪽 여백을 0.5cm로 설정 */
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="left section">
                    <h3>◎ 성경 버전 선택 [기본:KJV_한글KJV]</h3>
                    <form id="searchForm">
                        <select id="versions" name="versions" multiple style="height: 100px;">
                            {% for version in versions %}
                                <option value="{{ version }}" {% if version == 'KJV_한글KJV' %}selected{% endif %}>{{ version }}</option>
                            {% endfor %}
                        </select>
                    </form>
                    <div class="results-box">
                        <h3>◎ 검색 결과 - 찾았음 : <span id="resultCount">0</span> 개</h3>
                        <table id="searchResult">
                            <thead>
                                <tr>
                                    <th>버전</th>
                                    <th>성경</th>
                                    <th>합계</th>
                                </tr>
                            </thead>
                            <tbody id="searchResultBody">
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="right section">
                    <div class="search-box">
                        <h3>◎ 성경 구절 검색</h3>
                        <label for="verse">예) 창1:10, 요3:16, 마1, 신1:10/15</label>
                        <input type="text" id="verse" name="verse">
                        <button type="button" id="verseSearchButton">검색</button>
                        <div class="loader hidden" id="loader-content">
                            <div class="loader-text" id="loaderText-content">0s</div>
                        </div>
                    </div>
                    <div class="search-box">
                        <h3>◎ 성경 내용 검색</h3>
                        <label for="keyword">예) 사랑, 믿음, 소망</label>
                        <input type="text" id="keyword" name="keyword">
                        <button type="button" id="keywordSearchButton">검색</button>
                        <div class="loader hidden" id="loader-keyword">
                            <div class="loader-text" id="loaderText-keyword">0s</div>
                        </div>
                    </div>
                </div>
                <div class="section results-box" style="width: 100%; max-height: 600px;">
                    <h3>◎ 성경 구절</h3>
                    <table>
                        <tbody id="searchResultContentBody">
                        </tbody>
                    </table>
                </div>
                <a href="/download">
                    <h4><i>◎ 성경 검색 프로그램 다운로드</i></h4>
                </a>
            </div>
            <script>
                document.getElementById('verseSearchButton').addEventListener('click', function(event) {
                    search('verse');
                });

                document.getElementById('keywordSearchButton').addEventListener('click', function(event) {
                    search('content');
                });

                document.getElementById('verse').addEventListener('keypress', function(event) {
                    if (event.key === 'Enter') {
                        event.preventDefault();
                        search('verse');
                    }
                });

                document.getElementById('keyword').addEventListener('keypress', function(event) {
                    if (event.key === 'Enter') {
                        event.preventDefault();
                        search('content');
                    }
                });

                let uniqueData = [];

                function search(type) {
                    let versions = Array.from(document.getElementById('versions').selectedOptions).map(option => option.value);
                    let value = (type === 'verse') ? document.getElementById('verse').value : document.getElementById('keyword').value;

                    if (versions.length === 0) {
                        versions = ['KJV_한글KJV'];
                    }

                    // 로딩 애니메이션 표시
                    let loader = document.getElementById(type === 'verse' ? 'loader-content' : 'loader-keyword');
                    let loaderText = document.getElementById(type === 'verse' ? 'loaderText-content' : 'loaderText-keyword');
                    loader.classList.remove('hidden');
                    let startTime = Date.now();

                    let timer = setInterval(() => {
                        let elapsedTime = Math.floor((Date.now() - startTime) / 1000);
                        loaderText.innerText = `${elapsedTime}s`;
                    }, 1000);

                    fetch('/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ versions: versions, type: type, value: value })
                    })
                    .then(response => {
                        clearInterval(timer);
                        loader.classList.add('hidden');
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        uniqueData = Array.from(new Set(data.map(JSON.stringify))).map(JSON.parse);
                        let resultTableBody = document.querySelector('#searchResultBody');
                        let contentTableBody = document.querySelector('#searchResultContentBody');
                        resultTableBody.innerHTML = '';
                        contentTableBody.innerHTML = '';
                        if (uniqueData.length === 0) {
                            let row = document.createElement('tr');
                            row.innerHTML = `<td colspan="3">결과가 없습니다.</td>`;
                            resultTableBody.appendChild(row);
                        } else {
                            let statistics = calculateStatistics(uniqueData);
                            statistics.forEach(stat => {
                                let statRow = document.createElement('tr');
                                statRow.innerHTML = `<td>${shortenVersion(stat.version)}</td><td>${abbreviateBook(stat.book)}</td><td>${stat.count}</td>`;
                                resultTableBody.appendChild(statRow);
                            });

                            uniqueData.forEach((result, index) => {
                                let contentRow = document.createElement('tr');
                                let content = result[3];
                                let eng_content = result[4] || ''; // 영어 내용을 result[4]로 가정
                                if (type === 'content') {
                                    let regex = new RegExp(value, 'gi');
                                    content = content.replace(regex, match => `<span class="highlight">${match}</span>`);
                                }
                                contentRow.innerHTML = `<td class="version">${shortenVersion(result[0])}</td><td class="book">${abbreviateBook(result[1])}</td><td class="chapter-verse">${result[2]}</td><td class="content" onclick="showVerseDetails(${index})">${content}<br><span class="english-content">${eng_content}</span></td>`;
                                contentTableBody.appendChild(contentRow);
                            });

                            document.getElementById('resultCount').innerText = uniqueData.length;
                        }
                    })
                    .catch(error => {
                        clearInterval(timer);
                        loader.classList.add('hidden');
                        console.error('Error:', error);
                    });
                }

                function showVerseDetails(index) {
                    let result = uniqueData[index];
                    let details = `${result[0]}-${result[1]}-${result[2]}`;
                    alert(details);
                }

                function calculateStatistics(data) {
                    let stats = [];
                    let counts = data.reduce((acc, curr) => {
                        let key = `${curr[0]}_${curr[1]}`;
                        if (!acc[key]) {
                            acc[key] = { version: curr[0], book: curr[1], count: 0 };
                        }
                        acc[key].count += 1;
                        return acc;
                    }, {});

                    for (let key in counts) {
                        stats.push(counts[key]);
                    }
                    return stats;
                }

                function shortenVersion(version) {
                    switch(version) {
                        case '새번역': return '새번';
                        case '한글흠정역': return '흠정';
                        case '한글개역': return '개역';
                        case 'KJV_한글KJV': return 'KJ';
                        default: return version;
                    }
                }

                function abbreviateBook(book) {
                    return book.length > 2 ? book.slice(0, 2) : book;
                }
            </script>
        </body>
        </html>
    ''', versions=versions)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    versions = data.get('versions', [])
    search_type = data.get('type')
    value = data.get('value')

    logging.debug(f"Search request: versions={versions}, search_type={search_type}, value={value}")

    if not versions:
        versions = ["KJV_한글KJV"]

    if search_type == 'verse':
        results = search_by_verse(versions, value)
    elif search_type == 'content':
        results = search_by_content(versions, value)
    else:
        results = []

    logging.debug(f"Search completed.")
    return jsonify(results)

def search_by_verse(versions, query):
    logging.debug(f"search_by_verse called with versions={versions}, query={query}")
    results = []
    try:
        verses = query.split(",")
        for vc in verses:
            vc = vc.strip()
            match = re.match(r"(\D+)(\d*):?(\d*/?\d*)", vc)
            if match:
                book = match.group(1)
                chapter = match.group(2)
                verse_range = match.group(3)
                book = abbreviations.get(book, book)
                logging.debug(f"Searching for book={book}, chapter={chapter}, verse_range={verse_range}")

                for version in versions:
                    if version == '새번역':
                        file_path = os.path.join(bible_dir, f"새번역_{book}.txt")
                    elif version == 'KJV_한글KJV':
                        file_path = os.path.join(bible_dir, f"KJV_한글KJV_{book}.txt")
                    else:
                        file_path = os.path.join(bible_dir, f"{version}_{book}.txt")
                    
                    logging.debug(f"Checking file: {file_path}")
                    if not os.path.exists(file_path):
                        logging.warning(f"File not found: {file_path}")
                        continue

                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = [line.strip() for line in file if line.strip()]
                        if chapter and '/' in verse_range:
                            start_verse, end_verse = map(int, verse_range.split('/'))
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue
                                chapter_verse, content = parts
                                line_chapter, line_verse = map(int, chapter_verse.split(':'))
                                if line_chapter == int(chapter) and start_verse <= line_verse <= end_verse:
                                    results.append((version, book, chapter_verse, content))
                        elif chapter and verse_range:
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue
                                chapter_verse, content = parts
                                if line.startswith(f"{chapter}:{verse_range} "):
                                    results.append((version, book, chapter_verse, content))
                        elif chapter:
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue
                                chapter_verse, content = parts
                                if line.startswith(f"{chapter}:"):
                                    results.append((version, book, chapter_verse, content))
                        else:
                            for line in lines:
                                parts = line.split(maxsplit=1)
                                if len(parts) != 2:
                                    continue
                                chapter_verse, content = parts
                                results.append((version, book, chapter_verse, content))
    except Exception as e:
        logging.error('Error occurred in search_by_verse', exc_info=True)
    return results

def search_by_content(versions, query):
    logging.debug(f"search_by_content called with versions={versions}, query={query}")
    results = []
    try:
        queries = query.split(",")
        for q in queries:
            q = q.strip()
            for version in versions:
                logging.debug(f"Searching in version={version}, query={q}")
                for filename in os.listdir(bible_dir):
                    if filename.startswith(version) and filename.endswith(".txt"):
                        book = filename[len(version) + 1:].split(".")[0]  # 수정된 부분
                        file_path = os.path.join(bible_dir, f"{version}_{book}.txt")
                        
                        logging.debug(f"Checking file: {file_path}")
                        if not os.path.exists(file_path):
                            logging.warning(f"File not found: {file_path}")
                            continue

                        with open(file_path, 'r', encoding='utf-8') as file:
                            lines = file.readlines()
                            for line in lines:
                                if q in line:
                                    chapter_verse, content = line.strip().split(maxsplit=1)
                                    if q in content:
                                        results.append((version, book, chapter_verse, content))
    except Exception as e:
        logging.error('Error occurred in search_by_content', exc_info=True)
    return results

@app.route('/download')
def download():
    file_path = "C:/Bible/download/bible_find.zip"
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    print(f'* Serving Flask app "web"\n* Debug mode: on')
    app.run(debug=True, host='0.0.0.0')
