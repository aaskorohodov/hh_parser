import csv
import datetime
import os.path

import pandas as pd


def save_jobs_to_csv(jobs: list[dict]) -> None:
    """Сохраняет полученный список с вакансиями в csv-файл

    Args:
        jobs: список с вакансиями после парсинга"""

    rows = list(jobs[0].keys())  # Наименование колонок
    with open('jobs.csv', mode='w', encoding='utf-8') as file:
        csv.writer(file).writerow(rows)
        for job in jobs:
            csv.writer(file).writerow(list(job.values()))
        file.close()


def save_jobs_to_excel(db: dict) -> None:
    """"""

    jobs = db['requested_vacancy']

    try:
        # Create the 'results' directory if it doesn't exist
        results_dir = 'results'
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        df = pd.DataFrame(jobs)

        dt = datetime.datetime.now()
        formatted_date = dt.strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]
        excel_file_name = f'{formatted_date}.xlsx'
        excel_file_path = os.path.join('results', excel_file_name)

        df.to_excel(excel_file_path, index=False)
        db['progress'][datetime.datetime.now().__str__()] = '------------ Сохранено! ------------'
    except Exception as e:
        db['progress'][datetime.datetime.now().__str__()] = f'Не сохранено! Ошибка:\n {e.__str__()}'
