import os
import webbrowser

from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, jsonify
from parser import Parser

import save_results


# Load environment variables from .env
load_dotenv()


# In case you would like to pack it into exe - this is the way it will work
template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

app = Flask('__name__', template_folder=template_folder, static_folder=static_folder)
"""Your shiny app!"""

db = {'progress': {datetime.now().__str__(): 'Progress will be displayed here'}}
"""Emulates DB. This is were results (parsed jobs) and progress will be packed"""


@app.route('/')
def index():
    """Main page"""

    return render_template('index.html')


@app.route('/result')
def result():
    """Parse-results"""

    requested_vacancy = request.args.get('vacancy')
    if requested_vacancy:
        parser = Parser(requested_vacancy, db)
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
    """Saves parsed results into Excel/CSV"""

    if db:
        try:
            save_results.save_jobs_to_excel(db)
            return redirect('/')
        except:
            return ''
    return redirect('/')


@app.route('/progress_api')
def progress_api():
    """Sends current progress in response to JS"""

    progress_data = db['progress']

    # Return a JSON response
    return jsonify(progress=progress_data)


port = os.environ.get('PORT')
host = os.environ.get('HOST')

webbrowser.open(f'http://{host}:{port}/')

app.run(host=host, port=port)
