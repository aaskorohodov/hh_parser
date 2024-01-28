import csv
import datetime

import pandas as pd


def save_jobs_to_csv(jobs):
    """Сохраняет полученный список с описанием вакансий в csv-файл

    Args:
        jobs: список с описанием вакансий
    Returns:
        csv-файл"""

    rows = list(jobs[0].keys())  # Наименование колонок
    with open('jobs.csv', mode='w', encoding='utf-8') as file:
        csv.writer(file).writerow(rows)
        for job in jobs:
            csv.writer(file).writerow(list(job.values()))
        file.close()


def save_jobs_to_excel(jobs: list[dict]) -> None:
    """"""

    df = pd.DataFrame(jobs)

    dt = datetime.datetime.now()
    formatted_date = dt.strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]
    excel_file_path = f'{formatted_date}.xlsx'

    df.to_excel(excel_file_path, index=False)
