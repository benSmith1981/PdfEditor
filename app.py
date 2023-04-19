from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "secret-key"

@app.route('/')
def index():
    return redirect(url_for('design'))

@app.route('/design', methods=['GET', 'POST'])
def design():
    if request.method == 'POST':
        session['design_score'] = int(request.form.get('design'))
        return redirect(url_for('analysis'))
    return render_template('design.html')


@app.route('/development', methods=['GET', 'POST'])
def development():
    if request.method == 'POST':
        session['development_score'] = int(request.form.get('development'))
        return redirect(url_for('testing'))
    return render_template('development.html')

@app.route('/testing', methods=['GET', 'POST'])
def testing():
    if request.method == 'POST':
        session['testing_score'] = int(request.form.get('testing'))
        return redirect(url_for('evaluation'))
    return render_template('testing.html')

@app.route('/evaluation', methods=['GET', 'POST'])
def evaluation():
    if request.method == 'POST':
        session['evaluation_score'] = int(request.form.get('evaluation'))
        return redirect(url_for('result'))
    return render_template('evaluation.html')

@app.route('/result')
def result():
    total_score = sum([session.get(key, 0) for key in ('design_score', 'analysis_score', 'development_score', 'testing_score', 'evaluation_score')])
    return render_template('result.html', total_score=total_score)


@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    grading_criteria = {
        "1-2 marks": [
            "Identified some features that make the problem solvable by computational methods.",
            "Identified suitable stakeholders for the project and described them and some of their requirements.",
            "Identified some appropriate features to incorporate into their solution.",
            "Identified some features of the proposed computational solution.",
            "Identified some limitations of the proposed solution.",
            "Identified some requirements for the solution.",
            "Identified some success criteria for the proposed solution."
        ],
        "3-5 marks": [
            "Described the features that make the problem solvable by computational methods.",
            "Identified suitable stakeholders for the project and described how they will make use of the proposed solution.",
            "Researched the problem looking at existing solutions to similar problems identifying some appropriate features to incorporate into their solution.",
            "Identified the essential features of the proposed computational solution.",
            "Identified and described some limitations of the proposed solution.",
            "Identified most requirements for the solution.",
            "Identified some measurable success criteria for the proposed solution."
        ],
        "6-8 marks": [
            "Described the features that make the problem solvable by computational methods and why it is amenable to a computational approach.",
            "Identified suitable stakeholders for the project and described them and how they will make use of the proposed solution and why it is appropriate to their needs.",
            "Researched the problem in depth looking at existing solutions to similar problems identifying and describing suitable approaches based on this research.",
            "Identified and described the essential features of the proposed computational solution.",
            "Identified and explained any limitations of the proposed solution.",
            "Specified the requirements for the solution including (as appropriate) any hardware and software requirements.",
            "Identified measurable success criteria for the proposed solution."
        ],
        "9-10 marks": [
            "Described and justified the features that make the problem solvable by computational methods, explaining why it is amenable to a computational approach.",
            "Identified suitable stakeholders for the project and described them explaining how they will make use of the proposed solution and why it is appropriate to their needs.",
            "Researched the problem in depth looking at existing solutions to similar problems, identifying and justifying suitable approaches based on this research.",
            "Identified the essential features of the proposed computational solution explaining these choices.",
            "Identified and explained with justification any limitations of the proposed solution.",
            "Specified and justified the requirements for the solution including (as appropriate) any hardware and software requirements.",
            "Identified and justified measurable success criteria for the proposed solution."
        ]
    }
    if request.method == 'POST':
        selected_criteria = {}
        for boundary, criteria in grading_criteria.items():
            selected_criteria[boundary] = [criterion for criterion in criteria if request.form.get(criterion) == '1']

        score = 0
        if len(selected_criteria["9-10 marks"]) > 0:
            score = 9
        elif len(selected_criteria["6-8 marks"]) > 0:
            score = 6
        elif len(selected_criteria["3-5 marks"]) > 0:
            score = 3
        else:
            score = 1

        session['analysis_score'] = score
        return redirect(url_for('development'))

    return render_template('analysis.html', grading_criteria=grading_criteria)
