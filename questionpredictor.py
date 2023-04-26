import csv
import re
from collections import defaultdict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data = [row for row in reader]
    return data


def parse_data(data, recency_weight_factor):
    header, data = [item.strip() for item in data[0]], data[1:]
    current_year = 2023
    question_counts = defaultdict(float)

    for row in data:
        try:
            year = int(re.match(r'\d+', row[0]).group())
        except (AttributeError, ValueError):
            continue

        recency_weight = 1 + recency_weight_factor * (current_year - year)
        for idx, cell in enumerate(row[1:], start=1):
            if cell:
                question_counts[header[idx]] += recency_weight

    return question_counts


def calculate_probabilities(question_counts):
    total_questions = sum(question_counts.values())
    question_probabilities = {question: count / total_questions for question, count in question_counts.items()}
    return question_probabilities


def visualize_probabilities(probabilities, title):
    sorted_probabilities = {k: v for k, v in sorted(probabilities.items(), key=lambda item: item[1], reverse=True)}
    truncate_labels = lambda x: (x[:22] + '...') if len(x) > 25 else x
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(sorted_probabilities.keys(), sorted_probabilities.values())
    ax.set_xticks(range(len(sorted_probabilities.keys())))
    ax.set_xticklabels(map(truncate_labels, sorted_probabilities.keys()), rotation=90, fontsize=8)
    ax.set_xlabel('Question Types')
    ax.set_ylabel('Probability')
    ax.set_title(title)

    plt.show()


def main(csv1, csv2, recency_weight_factor):
    data1 = read_csv(csv1)
    data2 = read_csv(csv2)
    question_counts1 = parse_data(data1, recency_weight_factor)
    question_counts2 = parse_data(data2, recency_weight_factor)

    merged_counts = defaultdict(float)
    for question, count in question_counts1.items():
        merged_counts[question] += count
    for question, count in question_counts2.items():
        merged_counts[question] += count

    probabilities = calculate_probabilities(merged_counts)
    visualize_probabilities(probabilities, 'Probabilities of Topics Appearing in 2023 (Weighted by Frequency and Recency)')


if __name__ == '__main__':
    csv1 = 'questions1.csv'
    csv2 = 'questions2.csv'
    recency_weight_factor = 0.5
    main(csv1, csv2, recency_weight_factor)
