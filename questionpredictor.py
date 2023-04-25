import csv
from collections import defaultdict
import pandas as pd
import numpy as np

# Read the CSV data from a file
filename = 'questions.csv'

with open(filename, 'r') as file:
    reader = csv.reader(file)
    data = [row for row in reader]

# Remove leading/trailing spaces from header names
header, data = [item.strip() for item in data[0]], data[1:]

# Count the occurrences of each question type
question_counts = defaultdict(int)

for row in data:
    for idx, cell in enumerate(row[1:], start=1):
        if cell:
            question_counts[header[idx]] += 1

# Display the frequency of each question type
print("Frequency of questions:")
for question, count in question_counts.items():
    print(f"{question}: {count}")

# Create a DataFrame and set the "Year" column to numeric
df = pd.DataFrame(data, columns=header)
print(df)
df["Year"] = pd.to_numeric(df["Year"])

# This algorithm essentially predicts the questions for 2023 by considering the historical frequency of each question type and selecting questions randomly, 
# but with a higher probability for more frequent question types. This approach assumes that the distribution of questions in the past is representative of 
# the distribution of questions in the future.# Calculate the total number of questions by summing the values in question_counts. 
# This is done using sum(question_counts.values()).
total_questions = sum(question_counts.values())

# Calculate the probability of each question occurring by dividing the count of each question by the total number of questions. 
# This is done using a dictionary comprehension: {question: count / total_questions for question, count in question_counts.items()}. 
# The resulting question_probabilities dictionary contains the probabilities for each question type.
question_probabilities = {question: count / total_questions for question, count in question_counts.items()}

# Predict the possible questions for 2023
# Calculate the average number of questions per year by taking the mean of the number of questions in each row, excluding the 'Year' column: 
# int(np.mean([len(row) - 1 for row in data])). 
# This gives an estimate of the number of questions to expect in 2023.
num_questions_2023 = int(np.mean([len(row) - 1 for row in data]))

# Use numpy's random.choice function to randomly select num_questions_2023 questions from the available question types, weighted by their probabilities. 
# The p parameter in the np.random.choice function ensures that the selection is weighted by the probabilities calculated earlier.
predicted_questions_2023 = np.random.choice(list(question_probabilities.keys()), size=num_questions_2023, p=list(question_probabilities.values()))

print("\nPredicted questions for 2023:")
print(predicted_questions_2023)
