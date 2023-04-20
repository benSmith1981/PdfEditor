from flask import Flask, render_template, request, redirect, url_for, session, send_file

import json
import os
from flask import flash

from grading import grading_criteria
import re
import datetime
from pdfeditor import fill_pdf
now = datetime.datetime.now()
current_year = now.year

app = Flask(__name__)
app.secret_key = "secret-key"
# Add a dictionary to store the maximum score for each section
section_max_scores = {
    "analysis": 10,
    "design": 15,
    "developing_coded_solution": 15,
    "testing_inform_development": 5,
    "testing_inform_evaluation": 5,
    "evaluation_of_solution": 15
}
@app.route('/')
def index():
    return render_template('welcome.html')
    # return redirect(url_for('assessment', section='analysis'))

@app.route('/<section>', methods=['GET', 'POST'])
def assessment(section):
    sections = ["analysis", "design", "developing_coded_solution", "testing_inform_development", "testing_inform_evaluation", "evaluation_of_solution"]
    # Handle the analysis section separately
    print(section)

    if section not in sections:
        return "Invalid section", 404

    if request.method == 'POST':
        # selected_criteria = {}
        # for boundary, criteria in grading_criteria[section].items():
        #     selected_criteria[boundary] = [criterion for criterion in criteria if request.form.get(criterion) == '1']
        selected_criteria = {}
        for boundary, criteria in grading_criteria[section].items():
            selected_criteria[boundary] = []
            for criterion in criteria:
                unique_criterion_id = f"{boundary}__{criterion}"
                if request.form.get(unique_criterion_id) == '1':
                    selected_criteria[boundary].append(criterion)

        # Store the comment for this section
        comment = request.form.get(f'{section}_comments')
        print(comment)
        if comment:
            session[f'{section}_comments'] = comment

        max_score = section_max_scores[section]  # Get the maximum score for this section
        score_per_criterion = {}

        for boundary in grading_criteria[section]:
            # Extract all the integer values from the boundary string using regular expressions
            matches = re.findall(r'\d+', boundary)
            # print(matches)
            # print(boundary)

            if matches:
                # Convert the matches to integers and find the highest one
                highest_score = max(int(match) for match in matches)
                # print(highest_score)
                score_per_criterion[boundary] = highest_score



        # score = 0
        # for boundary, selected in selected_criteria.items():
        #     if selected:

        #         score += score_per_criterion[boundary]
        score = 0
        for boundary, selected in selected_criteria.items():
            print(boundary)
            if selected:
                # Calculate the score per criterion by dividing the boundary score by the number of items in that boundary
                score_per_selected_criterion = score_per_criterion[boundary] / len(grading_criteria[section][boundary])
                print(score_per_selected_criterion)

                # Add the score per criterion for each selected criterion in the boundary
                score += len(selected) * score_per_selected_criterion



        session[f'{section}_score'] = score
        if section == "evaluation_of_solution":
            analysis_score = session.get('analysis_score', 0)
            design_score = session.get('design_score', 0)
            development_score = session.get('developing_coded_solution_score', 0)
            testing_inform_dev_score = session.get('testing_inform_development_score', 0)
            testing_inform_eval_score = session.get('testing_inform_evaluation_score', 0)
            eval_score = score
            total_score = analysis_score + design_score + development_score + testing_inform_dev_score + testing_inform_eval_score + eval_score
            session['total_score'] = total_score
            session['sections'] = sections
            return redirect(url_for('summary', analysis_score=analysis_score, design_score=design_score, development_score=development_score, testing_inform_dev_score=testing_inform_dev_score, testing_inform_eval_score=testing_inform_eval_score, eval_score=eval_score, total_score=total_score))
        else:
            next_section_index = (sections.index(section) + 1) % len(sections)
            if next_section_index == 0:
                return render_template('summary.html', current_year=current_year, sections=sections, section_max_scores=section_max_scores)
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
    sections = session.get('sections', [])
    print(sections)
    return render_template('summary.html', current_year=current_year, sections=sections, section_max_scores=section_max_scores)

@app.route('/fill_cover_sheet', methods=['POST'])
def fill_cover_sheet():
    input_pdf = '330205-non-exam-assessment-cover-sheet-interactive.pdf'
    output_pdf = 'output.pdf'
    
    data_dict = {
        'year': request.form.get('year', str(datetime.date.today().year)),
        'centre_name': request.form.get('centre_name', 'City of Bristol College'),
        'centre_number': request.form.get('centre_number', '50507'),
        'candidate_name': request.form.get('candidate_name'),
        'candidate_number': request.form.get('candidate_number'),
        # 'unit_code': request.form.get('unit_code', 'H446 (03/04)'),
        # 'session': request.form.get('session', 'June'),
        # 'unit_title': request.form.get('unit_title', 'Programming project'),
        'analysis_score': session.get('analysis_score', 0),
        'analysis_comments': session.get('analysis_comments', ''),

        'design_score': session.get('design_score', 0),
        'design_comments': session.get('design_comments', ''),

        'development_score': session.get('developing_coded_solution_score', 0),
        'development_comments': session.get('developing_coded_solution_comments', ''),

        'testing_inform_dev_score': session.get('testing_inform_development_score', 0),
        'testing_inform_dev_comments': session.get('testing_inform_development_comments', ''),

        'testing_inform_eval_score': session.get('testing_inform_evaluation_score_score', 0),
        'testing_inform_eval_comments': session.get('testing_inform_evaluation_comments', ''),

        'evaluation_score': session.get('evaluation_of_solution_score', 0),
        'evaluation_comments': session.get('evaluation_of_solution_comments', ''),
                
        'total_score': session.get('total_score', '')

    }


    fill_pdf(input_pdf, output_pdf, data_dict)
    return send_file(output_pdf, as_attachment=True)
    # return redirect(url_for('index'))


from flask import send_from_directory
from werkzeug.utils import secure_filename

# Replace your save_data function with this one
@app.route('/save_data', methods=['POST'])
def save_data():
    candidate_name = session.get("candidate_name", "Candidate")
    filename = f"{candidate_name}_assessment_data.json"

    data = {
        "sections": session.get("sections", []),
        "total_score": session.get("total_score", 0),
    }
    for section in data["sections"]:
        data[f"{section}_score"] = session.get(f"{section}_score", 0)
        data[f"{section}_comments"] = session.get(f"{section}_comments", "")

    with open(filename, "w") as file:
        json.dump(data, file)

    return send_file(filename, as_attachment=True)

# Replace your load_data function with this one
@app.route('/load_data', methods=['POST'])
def load_data():
    if 'file' not in request.files:
        flash('No file uploaded')
        return redirect(url_for("summary"))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for("summary"))

    if file and file.filename.endswith('.json'):
        data = json.load(file)

        for key, value in data.items():
            session[key] = value

        flash("Data loaded successfully.")
    else:
        flash("Invalid file format. Please upload a JSON file.")

    return redirect(url_for("summary"))

@app.route('/clear_data', methods=['POST'])
def clear_data():
    sections = session.get('sections', [])
    for section in sections:
        session.pop(f"{section}_score", None)
        session.pop(f"{section}_comments", None)

    session.pop('total_score', None)

    flash("Data cleared successfully.")
    return redirect(url_for("summary"))

if __name__ == '__main__':
    app.run(debug=True)