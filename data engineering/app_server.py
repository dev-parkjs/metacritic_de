import threading
import mariadb
import pymysql
from flask import Flask, request, render_template, redirect, g
from bs4 import BeautifulSoup
import requests
from datetime import datetime

app = Flask(__name__)

# 스레딩 로컬을 사용하여 각 스레드별로 데이터베이스 연결을 관리합니다.
db_connections = threading.local()

# 데이터베이스 연결 설정
def get_db():
    if 'db' not in g:
        g.db =mariadb.connect(
            host='localhost',
            user='root',
            password='5252',
            database='pipeline'
        )
        cursorclass=pymysql.cursors.DictCursor
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

# MySQL 데이터베이스 연결 설정
db_connection = mariadb.connect(
    host='localhost',
    user='root',
    password='5252',
    database='pipeline'
)
cursorclass=pymysql.cursors.DictCursor

cursor = db_connection.cursor()

# crawl_and_store_data 함수를 정의합니다.
def crawl_and_store_data():
    final_page = 205  

    for page in range(1, final_page + 1):
        url = f'https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?sort=desc&page={page}'
        user_agent = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

        response = requests.get(url, headers=user_agent)
        soup = BeautifulSoup(response.text, 'lxml')

        games_dict = {
            'name': [],
            'platform': [],
            'release_date': [],
            'summary': [],
            'must_play': [],
            'meta_score': [],
            'user_score': []
        }

        names = soup.find_all('a', class_='title')
        for name in names:
            games_dict['name'].append(name.text)

        details = soup.find_all('div', class_='clamp-details')
        for detail in details:
            platform = detail.find('span', class_='data').text.strip()
            games_dict['platform'].append(platform)
            release = detail.find_all('span')[-1].text
            games_dict['release_date'].append(release)

        scores = soup.find_all('div', class_='browse-score-clamp')
        for score in scores:
            meta = score.find_all('div')[1].text
            games_dict['meta_score'].append(meta)
            user = score.find_all('div')[-1].text
            if user.lower() == 'tbd':
                user = None
            games_dict['user_score'].append(user)

        summary = soup.find_all('div', class_='summary')
        for summ in summary:
            games_dict['summary'].append(summ.text.strip())

        must_play = soup.find_all('td', class_='clamp-image-wrap')
        for i in must_play:
            if i.find('span', class_='mcmust'):
                games_dict['must_play'].append('Yes')
            else:
                games_dict['must_play'].append('No')

        # 스레딩 로컬을 사용하여 각 스레드별로 데이터베이스 연결을 관리합니다.
        db_conn = get_db()
        cur = db_conn.cursor()
        for i in range(len(games_dict['name'])):
            name = games_dict['name'][i]
            platform = games_dict['platform'][i]
            release_date_str = games_dict['release_date'][i]

            release_date_obj = datetime.strptime(release_date_str, '%B %d, %Y')
            release_date = release_date_obj.strftime('%Y-%m-%d')

            summary = games_dict['summary'][i]
            must_play = games_dict['must_play'][i]
            meta_score = games_dict['meta_score'][i]
            user_score = games_dict['user_score'][i]

            cur.execute("INSERT INTO games (name, platform, release_date, summary, must_play, meta_score, user_score) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (name, platform, release_date, summary, must_play, meta_score, user_score))
        db_conn.commit()
        cur.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    deleted_game_ids = []  # 삭제된 게임 ID를 저장할 리스트를 초기화합니다.

    if request.method == 'POST':
        search_term = request.form.get('search_term')
        cursor = db_connection.cursor()
        print("검색어:", search_term)  # 디버그용 출력
        cursor.execute('SELECT * FROM games WHERE name LIKE %s', ('%' + search_term + '%',))
        search_results = cursor.fetchall()
        cursor.close()
        return render_template('search_results.html', search_term=search_term, search_results=search_results, deleted_game_ids=deleted_game_ids)

    return render_template('search_results.html', deleted_game_ids=deleted_game_ids)  # GET 요청 시에도 렌더링을 수행합니다.


@app.route('/input_form', methods=['POST'])
def input_form():
    if request.method == 'POST':
        # POST 요청에서 게임 정보 추출
        name = request.form.get('name')
        platform = request.form.get('platform')
        release_date = request.form.get('release_date')
        meta_score = request.form.get('meta_score')
        user_score = request.form.get('user_score')
        summary = request.form.get('summary')
        must_play = request.form.get('must_play')

        # MySQL 데이터베이스에 데이터 추가
        cursor = db_connection.cursor()
        query = "INSERT INTO games (name, platform, release_date, meta_score, user_score, summary, must_play) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (name, platform, release_date, meta_score, user_score, summary, must_play)
        cursor.execute(query, values)
        db_connection.commit()

        # 추가한 데이터의 ID 가져오기
        inserted_id = cursor.lastrowid

        return render_template('success.html', inserted_id=inserted_id)

    return 'Input Form Page'

@app.route('/all_data', methods=['GET'])
def view_all_data():
    cursor = db_connection.cursor()
    cursor.execute('SELECT * FROM games')
    all_data = cursor.fetchall()
    cursor.close()
    return render_template('all_data.html', all_data=all_data)

@app.route('/delete_games', methods=['POST'])
def delete_games():
    game_ids = request.form.getlist('game_ids')  # 선택된 게임의 ID 목록
    deleted_game_ids = request.form.getlist('deleted_game_ids')  # 삭제된 게임의 ID 목록

    cursor = db_connection.cursor()

    # 선택된 게임을 데이터베이스에서 삭제합니다.
    for game_id in game_ids:
        cursor.execute("DELETE FROM games WHERE id = %s", (game_id,))
        # 삭제한 게임의 ID를 deleted_game_ids 목록에서 제거합니다.
        if game_id in deleted_game_ids:
            deleted_game_ids.remove(game_id)

    db_connection.commit()
    cursor.close()

    # 삭제된 게임의 ID가 제거된 상태로 업데이트된 deleted_game_ids 목록을 사용하여 검색 결과 페이지로 리디렉션합니다.
    return redirect('/search')

@app.route('/crawl', methods=['GET'])
def crawl_data():
    crawl_and_store_data()
    return "크롤링이 완료되었습니다."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
