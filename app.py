from flask import Flask, render_template, request, redirect, url_for, session, send_file
from grading import grading_criteria
import re
import datetime
from pdfeditor import fill_pdf
now = datetime.datetime.now()
current_year = now.year

app = Flask(__name__)
app.secret_key = "secret-key"

@app.route('/')
def index():
    return redirect(url_for('assessment', section='analysis'))

@app.route('/<section>', methods=['GET', 'POST'])
def assessment(section):
    sections = ["analysis", "design", "developing_coded_solution", "testing_inform_development", "testing_inform_evaluation", "evaluation_of_solution"]
    if section not in sections:
        return "Invalid section", 404

    if request.method == 'POST':
        selected_criteria = {}
        for boundary, criteria in grading_criteria[section].items():
            selected_criteria[boundary] = [criterion for criterion in criteria if request.form.get(criterion) == '1']

        total_criteria = len(grading_criteria[section].keys())
        max_score = max([int(re.search(r'\d+', boundary).group()) for boundary in grading_criteria[section].keys()])
        
        score_per_criterion = {}
        for boundary in grading_criteria[section]:
            # Extract the integer value from the boundary string using regular expressions
            match = re.search(r'\d+', boundary)
            if match:
                score = int(match.group())
                score_per_criterion[boundary] = score / total_criteria

        score = 0
        for boundary, selected in selected_criteria.items():
            score += len(selected) * score_per_criterion[boundary]

        session[f'{section}_score'] = score
        if section == "evaluation":
            analysis_score = session.get('analysis_score', 0)
            design_score = session.get('design_score', 0)
            development_score = session.get('development_score', 0)
            testing_inform_dev_score = session.get('testing_inform_dev_score', 0)
            testing_inform_eval_score = session.get('testing_inform_eval_score', 0)
            eval_score = score
            total_score = analysis_score + design_score + development_score + testing_inform_dev_score + testing_inform_eval_score + eval_score
            return redirect(url_for('summary', analysis_score=analysis_score, design_score=design_score, development_score=development_score, testing_inform_dev_score=testing_inform_dev_score, testing_inform_eval_score=testing_inform_eval_score, eval_score=eval_score, total_score=total_score))
        else:
            next_section_index = (sections.index(section) + 1) % len(sections)
            if next_section_index == 0:
                return render_template('summary.html', current_year=current_year)
            else:
                next_section = sections[next_section_index]
                return redirect(url_for('assessment', section=next_section))


    next_section_index = (sections.index(section) + 1) % len(sections)
    if next_section_index == 0:
        return render_template('assessment.html', grading_criteria=grading_criteria[section], section=section)
    else:
        next_section = sections[next_section_index]
        return render_template('assessment.html', grading_criteria=grading_criteria[section], section=section, next_section=next_section)



@app.route('/summary')
def summary():
    analysis_score = request.args.get('analysis_score')
    design_score = request.args.get('design_score')
    development_score = request.args.get('development_score')
    testing_inform_dev_score = request.args.get('testing_inform_dev_score')
    testing_inform_eval_score = request.args.get('testing_inform_eval_score')
    eval_score = request.args.get('eval_score')
    total_score = request.args.get('total_score')
    return render_template('summary.html', analysis_score=analysis_score, design_score=design_score, development_score=development_score, testing_inform_dev_score=testing_inform_dev_score, testing_inform_eval_score=testing_inform_eval_score, eval_score=eval_score, total_score=total_score)

@app.route('/fill_cover_sheet', methods=['POST'])
def fill_cover_sheet():
    input_pdf = '330205-non-exam-assessment-cover-sheet-interactive.pdf'
    output_pdf = 'output.pdf'
    
    data_dict = {
        'candidate_name': request.form.get('candidate_name'),
        'candidate_number': request.form.get('candidate_number'),
        'centre_number': request.form.get('centre_number', '50507'),
        'centre_name': request.form.get('centre_name', 'City of Bristol College'),
        'unit_code': request.form.get('unit_code', 'H446 (03/04)'),
        'session': request.form.get('session', 'June'),
        'year': request.form.get('year', str(datetime.date.today().year)),
        'unit_title': request.form.get('unit_title', 'Programming project'),
        'analysis_score': session.get('analysis_score', 0),
        'design_score': session.get('design_score', 0),
        'development_score': session.get('development_score', 0),
        'testing_inform_dev_score': session.get('testing_inform_dev_score', 0),
        'testing_inform_eval_score': session.get('testing_inform_eval_score', 0),
        'evaluation_score': session.get('evaluation_score', 0),
        'analysis_comments': request.form.get('analysis_comments'),
        'design_comments': request.form.get('design_comments'),
        'development_comments': request.form.get('development_comments'),
        'testing_inform_dev_comments': request.form.get('testing_inform_dev_comments'),
        'testing_inform_eval_comments': request.form.get('testing_inform_eval_comments'),
        'evaluation_comments': request.form.get('evaluation_comments')
    }

    fill_pdf(input_pdf, output_pdf, data_dict)
    return send_file(output_pdf, as_attachment=True)
    # return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)