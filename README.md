# 🎮 Metacritic_DE: 데이터 엔지니어링 & 파이프라인 프로젝트

Metacritic_DE는 게임 리뷰/점수 정보 웹사이트인 **Metacritic**에서 데이터를 수집하고, 가공하여 저장하며, 웹 애플리케이션 및 자동화 파이프라인을 구성한 **엔드 투 엔드 데이터 엔지니어링 프로젝트**입니다.

데이터 수집 → 가공 → 저장 → 웹 제공 → 자동화까지의 전 과정이 포함된 실전형 프로젝트로, SQL, Python, Flask, Airflow 등 다양한 기술을 통합적으로 활용합니다.

---

## 📁 프로젝트 폴더 구조

```bash
Metacritic_DE/
├── data_engineering/         # 수집 및 DB 연동, 웹 인터페이스
│   ├── metacritic_crawling.ipynb      # Metacritic 웹 크롤링 노트북
│   ├── app_server.py                  # Flask 웹 서버: 검색/삽입/삭제
│   └── db_connector.py                # MariaDB 연결 및 쿼리 처리
│
├── pipeline/                # 자동화 파이프라인 (Airflow 기반)
│   ├── metacritic_batch_crawler.py   # 배치 크롤링 함수 (PythonOperator용)
│   ├── airflow_dag.py                 # Airflow DAG 정의
│   ├── games_data_first.csv           # 1차 배치 결과 샘플
│   └── games_data_second.csv          # 2차 배치 결과 샘플
│
├── requirements.txt         # 패키지 목록
├── .gitignore               # Git 추적 제외 파일 목록
└── README.md                # 프로젝트 설명서
```

---

## 🚀 기술 스택

- **언어**: Python 3.x, SQL
- **크롤링**: `requests`, `BeautifulSoup`
- **웹 프레임워크**: Flask
- **데이터베이스**: MariaDB
- **파이프라인 자동화**: Apache Airflow
- **환경 구성**: requirements.txt, Git 관리

---

## 🧩 주요 기능 흐름

### 📦 수집 & 저장
- Metacritic에서 게임 데이터 크롤링 (제목, 평점, 플랫폼 등)
- 수집 데이터를 **MariaDB**에 저장 (`INSERT`, `SELECT`, `DELETE` 지원)

### 🌐 웹 UI
- **Flask**를 통해 게임 정보 검색, 추가, 삭제 기능 제공
- 사용자 친화적 웹 인터페이스 구현 (`app_server.py`)

### ⚙️ 자동화 파이프라인
- Airflow DAG을 통한 배치 크롤링 실행 (`airflow_dag.py`)
- CSV 저장 또는 DB 적재 기능 포함

---

## 🧪 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. Flask 서버 실행
```bash
python app_server.py
```

### 3. Airflow DAG 적용 (예시)
```bash
# dags/ 폴더에 airflow_dag.py 복사 후 실행
airflow webserver
airflow scheduler
```

---

## 🧠
✅ 단순 크롤링이 아니라 **전체 데이터 흐름 설계 (수집 → 저장 → 제공 → 자동화)** 를 구현했습니다.  
✅ 데이터베이스 설계 + REST 웹 서버 + 배치 자동화까지 모두 포함됩니다.  
✅ 실무에서 바로 활용 가능한 기술스택(Airflow, Flask, SQL, Git 등)을 사용했습니다.


---

## 🙋‍♂️ 작성자

**dev-parkjs**  
[GitHub](https://github.com/dev-parkjs)


