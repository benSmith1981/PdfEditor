import os
import pdfrw

import pdfrw

input_pdf = '330205-non-exam-assessment-cover-sheet-interactive.pdf'

def get_field_names(input_pdf_path):
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    field_names = []
    for page in template_pdf.pages:
        annotations = page['/Annots']
        if annotations is None:
            continue
        for annotation in annotations:
            if annotation['/Subtype'] == '/Widget':
                key = annotation['/T'][1:-1]
                field_names.append(key)
    return field_names

field_names = get_field_names(input_pdf)

for field in field_names:
    print(field)

# input_pdf = '330205-non-exam-assessment-cover-sheet-interactive.pdf'
# output_pdf = 'output.pdf'


def fill_pdf1(input_pdf_path, output_pdf_path, data_dict):
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    for page in template_pdf.pages:
        annotations = page['/Annots']
        if annotations is None:
            continue
        for annotation in annotations:
            if annotation['/Subtype'] == '/Widget':
                key = annotation['/T'][1:-1]
                if key in data_dict:
                    # Get the value for the field name from the data dictionary
                    value = data_dict[key]
                    # Set the value of the annotation to the value from the data dictionary
                    annotation.update(pdfrw.PdfDict(AP='', V='{}'.format(value)))
                    annotation.update(pdfrw.PdfDict(Ff=1))
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)

def fill_pdf(input_pdf_path, output_pdf_path, data_dict):
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    field_map = {
        'Dropdown2': 'analysis_score',
        "0": 'design_score',
        "0": 'development_score',
        "1": 'testing_inform_dev_score',
        "1": 'testing_inform_eval_score',
        "1": 'evaluation_score',
        "0": 'analysis_comments',
        "0": 'design_comments',
        "3": 'development_comments',
        "2": 'testing_inform_dev_comments',
        "4": 'testing_inform_eval_comments',
        "0": 'evaluation_comments',
        "5": 'candidate_name',
        "1": 'candidate_number',
        "6": 'centre_number',
        "2": 'centre_name',
        "1": 'unit_code',
        "17": 'session',
        "18": 'year',
        "19": 'unit_title'
    }


    for page in template_pdf.pages:
        annotations = page['/Annots']
        if annotations is None:
            continue
        for annotation in annotations:
            if annotation['/Subtype'] == '/Widget':
                field_name = annotation['/T'][1:-1]
                print(field_name)
                print(field_map[field_name])
                if field_name in field_map:
                    value = data_dict[field_map[field_name]]
                    print(value)
                    annotation.update(pdfrw.PdfDict(AP='', V='{}'.format(value)))
                    annotation.update(pdfrw.PdfDict(Ff=1))

    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)




# Define the fields you want to fill
# fields = {
#     '1': 'field_value_1',
#     '2': 'field_value_2',
#     # ... add more fields as needed
# }

# # Fill out the PDF form
# fill_pdf(input_pdf, output_pdf, fields)
