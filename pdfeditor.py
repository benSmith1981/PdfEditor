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

input_pdf = '330205-non-exam-assessment-cover-sheet-interactive.pdf'
output_pdf = 'output.pdf'

def fill_pdf(input_pdf_path, output_pdf_path, data_dict):
    template_pdf = pdfrw.PdfReader(input_pdf_path)
    for page in template_pdf.pages:
        annotations = page['/Annots']
        if annotations is None:
            continue
        for annotation in annotations:
            if annotation['/Subtype'] == '/Widget':
                key = annotation['/T'][1:-1]
                if key in data_dict:
                    annotation.update(pdfrw.PdfDict(AP='', V='{}'.format(data_dict[key])))
                    annotation.update(pdfrw.PdfDict(Ff=1))
    pdfrw.PdfWriter().write(output_pdf_path, template_pdf)

# Define the fields you want to fill
fields = {
    '1': 'field_value_1',
    '2': 'field_value_2',
    # ... add more fields as needed
}

# Fill out the PDF form
fill_pdf(input_pdf, output_pdf, fields)
