import csv
import re
from collections import defaultdict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



# The probability calculation in the updated code considers both the frequency and recency of the questions. 
# Here's a detailed explanation of the calculation:

# The resulting question_probabilities dictionary contains the probability of each question type, 
# considering both their frequency and recency.
def read_and_sort_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = [row for row in reader]

    header, data = [item.strip() for item in data[0]], data[1:]
    # current_year: The year we are making the predictions for (in this case, 2023).
    # year: The year the question appeared in the data.
    # recency_weight_factor: A value between 0 and 1 that controls the impact of recency on the probabilities. 
    current_year = 2023
    recency_weight_factor = 0.5

    # Frequency: The number of times a particular question type appears in the data.
    # Recency: The number of years that have passed since the question type last appeared.
    # To account for both factors, we introduce a recency_weight for each question in the data, which is calculated as:
    # recency_weight = 1 + recency_weight_factor * (current_year - year)
    question_counts = defaultdict(float) # The updated count for each question type is stored in the question_counts dictionary.

    # A higher value gives more weight to recency, while a lower value reduces its impact.
    # The recency_weight is multiplied by the frequency of the question type for each row in the data, 
    # effectively increasing the count of questions that have appeared more recently. 
    for row in data:
        year = int(re.match(r'\d+', row[0]).group())
        recency_weight = 1 + recency_weight_factor * (current_year - year)
        for idx, cell in enumerate(row[1:], start=1):
            if cell:
                question_counts[header[idx]] += recency_weight

    # Once we have the weighted counts, we calculate the total count of all question types:
    # total_questions = sum(question_counts.values())
    total_questions = sum(question_counts.values())

    # Next, we calculate the probability of each question type by dividing the weighted count of that question type 
    # by the total count:
    # question_probabilities = {question: count / total_questions for question, count in question_counts.items()}
    question_probabilities = {question: count / total_questions for question, count in question_counts.items()}
    
    return question_probabilities

csv1 = 'questions1.csv'
csv2 = 'questions2.csv'

probabilities1 = read_and_sort_csv(csv1)
probabilities2 = read_and_sort_csv(csv2)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), sharey=True)

truncate_labels = lambda x: (x[:22] + '...') if len(x) > 25 else x

ax1.bar(probabilities1.keys(), probabilities1.values())
ax1.set_xticks(range(len(probabilities1.keys())))
ax1.set_xticklabels(map(truncate_labels, probabilities1.keys()), rotation=90, fontsize=8)
ax1.set_xlabel('Question Types')
ax1.set_ylabel('Probability')
ax1.set_title('Probabilities from CSV1')

ax2.bar(probabilities2.keys(), probabilities2.values())
ax2.set_xticks(range(len(probabilities2.keys())))
ax2.set_xticklabels(map(truncate_labels, probabilities2.keys()), rotation=90, fontsize=8)
ax2.set_xlabel('Question Types')
ax2.set_title('Probabilities from CSV2')

plt.suptitle('Probabilities of Topics Appearing in 2023 (Calculated as Count of Each Topic / Total Count)')

plt.show()
