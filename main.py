import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title of the Streamlit app
st.title('Governmental Financial Aid Analysis')

# Input for budget
budget = st.number_input("Enter the total budget for financial aid (in CHF):", min_value=0.0, step=1000.0)


# Function to compute financial aid score
def compute_aid_score(row):
    # Example arbitrary weights for the formula
    age_weight = 0.1
    income_weight = 0.3
    marital_status_weight = 0.1
    children_weight = 0.2
    social_help_weight = 0.1
    living_years_weight = 0.1
    student_weight = 0.1

    # Normalizing the values (example normalization)
    age = row['Age'] / 100 if pd.notnull(row['Age']) else 0
    income = row['Income (yearly in CHF)'] / 100000 if pd.notnull(row['Income (yearly in CHF)']) else 0
    marital_status = 1 if row['Marital status'] == 'Single' else 0.5
    children = row['Number of children'] / 10 if pd.notnull(row['Number of children']) else 0
    social_help = 1 if row['Receive social help (Von socialhelfe oder SRK)'] == 'Yes' else 0
    living_years = row['Living in switzerland since (in years)'] / 100 if pd.notnull(
        row['Living in switzerland since (in years)']) else 0
    student = 1 if row['Student (Uni, Hochschule, Lehre, oder ausbildung)'] == 'Yes' else 0

    # Calculate the score
    score = (age_weight * age +
             income_weight * (1 - income) +
             marital_status_weight * marital_status +
             children_weight * children +
             social_help_weight * social_help +
             living_years_weight * living_years +
             student_weight * student)

    return score


# Read the Excel file directly
file_path = 'data.xlsx'
df = pd.read_excel(file_path)

if budget > 0:
    st.write("## Data Preview")
    st.write(df.head())

    # Calculate the financial aid score for each applicant
    df['Aid Score'] = df.apply(compute_aid_score, axis=1)

    # Drop rows with NaN aid scores
    df = df.dropna(subset=['Aid Score'])

    # Normalize the aid scores to sum to 1
    df['Normalized Aid Score'] = df['Aid Score'] / df['Aid Score'].sum()

    # Distribute the budget based on normalized aid scores
    df['Allocated Budget (CHF)'] = df['Normalized Aid Score'] * budget

    st.write("## Data with Aid Scores and Allocated Budget")
    st.write(df.head())

    # Pie chart of marital status
    st.write("## Pie Chart of Marital Status")
    marital_status_counts = df['Marital status'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(marital_status_counts, labels=marital_status_counts.index, autopct='%1.1f%%')
    st.pyplot(fig)

    # Histogram of aid scores
    st.write("## Histogram of Aid Scores")
    fig, ax = plt.subplots()
    ax.hist(df['Aid Score'], bins=10, edgecolor='black')
    ax.set_xlabel('Aid Score')
    ax.set_ylabel('Number of Applicants')
    st.pyplot(fig)

    # Histogram of allocated budget
    st.write("## Allocated Budget Distribution")
    fig, ax = plt.subplots()
    ax.hist(df['Allocated Budget (CHF)'], bins=10, edgecolor='black')
    ax.set_xlabel('Allocated Budget (CHF)')
    ax.set_ylabel('Number of Applicants')
    st.pyplot(fig)
