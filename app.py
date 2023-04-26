from flask import Flask, render_template, redirect, url_for, request, session, send_file, jsonify
from collections import defaultdict
import csv
import re
import datetime
import json
from .pdf_generator import fill_pdf

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


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


@app.route('/<section>', methods=['GET', 'POST'])
def assessment(section):
    sections = ["analysis", "design", "developing_coded_solution", "testing_inform_development", "testing_inform_evaluation", "evaluation_of_solution"]
    # Handle the analysis section separately

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
            if selected:
                # Calculate the score per criterion by dividing the boundary score by the number of items in that boundary
                score_per_selected_criterion = score_per_criterion[boundary] / len(grading_criteria[section][boundary])

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


# Exam question probability calcualtor

def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = [row for row in reader]
    return data


def parse_data(data, recency_weight_factor):
    header, data = [item.strip() for item in data[0]], data[1:]
    current_year = 2023
    # question_counts is a dictionary that keeps track of the weighted count of questions for each topic. 
    question_counts = defaultdict(float)

    for row in data:
        try:
            year = int(re.match(r'\d+', row[0]).group())
        except (AttributeError, ValueError):
            continue

        # The purpose of using weights is to give more importance to questions that are more recent, as specified by the recency_weight_factor. 
        # The higher the value of recency_weight_factor, the more weight recent questions will have compared to older ones. e.g
        # {
        # 'Topic A': 25.5,
        # 'Topic B': 18.0,
        # 'Topic C': 32.7,
        # 'Topic D': 12.2
        # }
        # current_year - year: This computes the difference in years between the present year and the year the data was recorded. 
        # For example, if the data is from 2020, the difference would be 3 (2023 - 2020).

        # recency_weight_factor * (current_year - year): This multiplies the difference in years by the recency weight factor. 
        # The recency weight factor is a value that you can set to control the importance given to more recent data.
        # A higher value will give more weight to recent data, while a lower value will make the weighting less sensitive to the recency of the data.
        # We add 1 so recency is never 0
        recency_weight = 1 + recency_weight_factor * (current_year - year)
        for idx, cell in enumerate(row[1:], start=1):
            if cell:
                # The keys in the dictionary represent the question topics (column names in the data, except for the year column), 
                # and the values are the weighted counts for each topic.
                question_counts[header[idx]] += recency_weight

    return question_counts

# It takes the question_counts dictionary as an argument.
# The function then iterates through each item in the question_counts dictionary and divides the weighted count by total_questions. 
def calculate_probabilities(question_counts):
    # The total_questions variable calculates the sum of all the weighted counts in the question_counts dictionary.
    total_questions = sum(question_counts.values())
    # This gives the probability of each question.
    question_probabilities = {question: count / total_questions for question, count in question_counts.items()}
    # It returns a dictionary containing the calculated probabilities for each question.
    return question_probabilities


@app.route('/data/algorithms')
def data_algorithms():
    csv1 = 'questions1.csv'
    recency_weight_factor = float(request.args.get('recency_weight_factor', 0.5))
    data1 = read_csv(csv1)
    question_counts1 = parse_data(data1, recency_weight_factor)
    probabilities = calculate_probabilities(question_counts1)
    sorted_probabilities = {k: v for k, v in sorted(probabilities.items(), key=lambda item: item[1], reverse=True)}
    return jsonify(list(sorted_probabilities.items()))

@app.route('/data/computer_systems')
def data_computer_systems():

    csv2 = 'questions2.csv'
    recency_weight_factor = float(request.args.get('recency_weight_factor', 0.5))
    data2 = read_csv(csv2)
    question_counts2 = parse_data(data2, recency_weight_factor)
    probabilities = calculate_probabilities(question_counts2)
    sorted_probabilities = {k: v for k, v in sorted(probabilities.items(), key=lambda item: item[1], reverse=True)}
    return jsonify(list(sorted_probabilities.items()))


@app.route('/questions')
def questions():
    return render_template('questions.html')


if __name__ == '__main__':
    app.run(debug=True)