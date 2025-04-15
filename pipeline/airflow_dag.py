from pathlib import Path
import airflow
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

import csv
import requests
from bs4 import BeautifulSoup
import datetime as dt
from datetime import datetime
from datetime import timedelta
import pandas as pd

# dag 정의
dag = DAG(
    dag_id="meta_refactoring",
    schedule_interval='@once',
    start_date=dt.datetime(2023, 10, 26, 6, 32),
)

# 크롤러 정의
def _metacritic_crawler(crawler_name, **context):
    output_path = context["templates_dict"]["output_path"]
    Path(output_path).parent.mkdir(exist_ok=True)

    USER_AGENT = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    # 데이터 유입을 Batch 단위로 가정하여 두 번으로 나눔
    PAGE_RANGES = {
        'crawler1': range(1, 201),
        'crawler2': range(201, 544)
    }
    URL_TEMPLATE = 'https://www.metacritic.com/browse/game/all/all/all-time/popular/?releaseYearMin=1910&releaseYearMax=2023&page={}'

    # 각 컬럼 데이터 크롤링
    names = []
    release_dates = []
    meta_scores = []
    recommendations = []

    def extract_names(soup):
            names = []
            h3_tags = soup.find_all('h3', class_='c-finderProductCard_titleHeading')
            for tag in h3_tags:
                span_tags = tag.find_all('span')
                if len(span_tags) > 1:
                    name = span_tags[1].get_text().replace(',', '')
                    names.append(name)
            return names

    def extract_release_dates(soup):
        release_dates = []
        release_divs = soup.find_all('div', class_='c-finderProductCard_meta')
        for div in release_divs:
            span_tags = div.find_all('span', class_='u-text-uppercase')
            release_date = ''
            for span in span_tags:
                if 'Metascore' not in span.get_text(strip=True):
                    release_date = span.get_text(strip=True)
                    release_dates.append(release_date)
        return release_dates

    def extract_meta_scores(soup):
        meta_scores = []
        metascore_elements = soup.find_all('div', class_='c-siteReviewScore')
        for element in metascore_elements:
            span = element.find('span')
            if span is not None:
                meta_scores.append(span.text.strip())
            else:
                meta_scores.append('')
        return meta_scores

    def extract_recommendations(soup):
        recommendations = []
        metascore_elements = soup.find_all('div', class_='c-siteReviewScore')
        for element in metascore_elements:
            if 'c-siteReviewScore_green' in element['class']:
                recommendations.append('A score')
            elif 'c-siteReviewScore_yellow' in element['class']:
                recommendations.append('B score')
            elif 'c-siteReviewScore_red' in element['class']:
                recommendations.append('C score')
        return recommendations

    page_range = PAGE_RANGES[crawler_name]
    for page in page_range:
        url = URL_TEMPLATE.format(page)
        response = requests.get(url, headers=USER_AGENT)
        soup = BeautifulSoup(response.text, 'lxml')
                   
        names += extract_names(soup)
        release_dates += extract_release_dates(soup)
        meta_scores += extract_meta_scores(soup)
        recommendations += extract_recommendations(soup)

    # 데이터 전처리 및 저장
    df = pd.DataFrame(list(zip(names, release_dates, meta_scores, recommendations)), 
                      columns=['name', 'release_date', 'meta_score', 'recommendation'])
    df['name'] = df['name'].str.replace('[^\w\s]','')
    df['recommendation'] = df['recommendation'].str.replace('[^\w\s]','')
    df['meta_score'] = pd.to_numeric(df['meta_score'], errors='coerce')
    df['release_date'] = pd.to_datetime(df['release_date'], format='%b %d, %Y')
    df.to_csv(output_path, index=False)

# 파이썬 오퍼레이터 정의: Batch 단위에 따라 2개로 나눔
metacritic_crawler1 = PythonOperator(
        task_id="metacritic_crawler1",
        python_callable=_metacritic_crawler,
        op_kwargs={'crawler_name': 'crawler1'},
        templates_dict={
            "output_path": "/home/ubuntu/airflow/output/batch_1.csv",
        },
        dag=dag,
)

metacritic_crawler2 = PythonOperator(
        task_id="metacritic_crawler2",
        python_callable=_metacritic_crawler,
        op_kwargs={'crawler_name': 'crawler2'},
        templates_dict={
            "output_path": "/home/ubuntu/airflow/output/batch_2.csv",
        },
        dag=dag,
)

# sql query operator로 sql 테이블 생성
create_meta_table = SQLExecuteQueryOperator(
    task_id='create_meta_table',
    sql="""
    CREATE TABLE airflow_meta (
        Name VARCHAR(100),
        Release_Date VARCHAR(100),
        Meta_Score VARCHAR(100),
        Recommendation VARCHAR(100)
    );
    """,
    conn_id='root',
    database='airflow',
    dag=dag,
)

# bashoperator로 크롤링한 파일을 특정 폴더로 이동
## mysql 적재 시 scp 관련 오류가 계속 나서 지정 폴더에서 적재 진행
send_files1 = BashOperator(
        task_id="send_files1",
        bash_command=(
            "sudo mv /home/ubuntu/airflow/output/batch_1.csv /var/lib/mysql-files/"
        ),
        dag=dag,
)

send_files2 = BashOperator(
        task_id="send_files2",
        bash_command=(
            "sudo mv /home/ubuntu/airflow/output/batch_2.csv /var/lib/mysql-files/"
        ),
        dag=dag,
)

# sql query operator로 mysql에 데이터 적재
load_data1 = SQLExecuteQueryOperator(
    task_id='load_data1',
    sql="""
    LOAD DATA INFILE '/var/lib/mysql-files/batch_1.csv'
    INTO TABLE airflow_meta
    FIELDS TERMINATED BY ','
    IGNORE 1 ROWS
    ;
    """,
    conn_id='root',
    database='airflow',
    dag=dag,
)

load_data2 = SQLExecuteQueryOperator(
    task_id='load_data2',
    sql="""
    LOAD DATA INFILE '/var/lib/mysql-files/batch_2.csv'
    INTO TABLE airflow_meta
    FIELDS TERMINATED BY ','
    IGNORE 1 ROWS
    ;
    """,
    conn_id='root',
    database='airflow',
    dag=dag,
)

metacritic_crawler1 >> metacritic_crawler2 >> create_meta_table >> send_files1 >> send_files2 >> load_data1 >> load_data2

