from flask import Flask, render_template, request, redirect
from parser import Parser

import save_results


app = Flask('HHScrapper')
db = {}


@app.route('/')
def index():
    """Главная страница сайта

    Returns:
        html-шаблон главной страницы"""

    return render_template('index.html')


@app.route('/result')
def result():
    """Страница с результатами поиска

    Returns:
        html-шаблон страницы с результатами при введенном ключе поиска, иначе - переход на главную страницу"""

    requested_vacancy = request.args.get('vacancy')
    if requested_vacancy:
        parser = Parser(requested_vacancy)
        parsed_vacancies = parser.parse_vacancies()
        count_jobs = len(parsed_vacancies)
        db['requested_vacancy'] = parsed_vacancies
    else:
        return redirect('/')
    return render_template('results.html',
                           result=requested_vacancy,
                           jobs=parsed_vacancies,
                           count_jobs=count_jobs)


@app.route('/export')
def export_data_to_csv():
    """Сохранение результатов поиска в CSV-файл"""

    if db:
        try:
            save_results.save_jobs_to_excel(db['requested_vacancy'])
            return redirect('/')
        except:
            return ''
    return redirect('/')


app.run()
