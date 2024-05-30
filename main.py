import seaborn as sns
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Title of the Streamlit app
st.title('Governmental Financial Aid Analysis')

# Input for budget
budget = st.number_input("Enter the total budget for financial aid (in CHF):", min_value=0.0, step=1000.0)

# Function to compute financial aid score
def compute_aid_score(row):

    age_weight = 0.1
    income_weight = 0.50
    marital_status_weight = 0.1
    children_weight = 0.1
    social_help_weight = 0.1
    student_weight = 0.1
    # net_income_weight = 0.1
    # wealth_weight = 0.05
    # financial_change_weight = 0.05
    # living_years_weight = 0.1

    # Normalizing the values (example normalization)
    age = row['Age'] / 100 if pd.notnull(row['Age']) else 0
    income = row['Income (yearly in CHF)'] / 100000 or 0
    marital_status = 1 if row['Marital status'] == 'Single' else 0.5
    children = row['Number of children'] / 10 or 0
    social_help = 1 if row['Receive social help (Von socialhelfe oder SRK)'] == 'Yes' else 0
    student = 1 if row['Student (Uni Hochschule Lehre ausbildung)'] == 'Yes' else 0
    # living_years = int(row['Living in Switzerland since (in years)']) / 100 or 0
    # net_income = row['Net Income (Reineinkommen) in CHF'] / 100000 or 0
    # wealth = row['Wealth (Vermögen) in CHF'] / 1000000 or 0
    # financial_change = 1 if row['Significant financial change'] == 'Yes' else 0

    # Calculate the score
    score = (age_weight * age +
             income_weight * (1 - income) +
             marital_status_weight * marital_status +
             children_weight * children +
             social_help_weight * social_help +
             student_weight * student)
            #  net_income_weight * (1 - net_income) +
            #  wealth_weight * (1 - wealth) +
            #  financial_change_weight * financial_change)

    return score

# Function to assign priority based on aid score
# def assign_priority(score):
#     if score < 0.25:
#         return 'Very Low Priority'
#     elif 0.25 <= score < 0.5:
#         return 'Low Priority'
#     elif 0.5 <= score < 0.75:
#         return 'Medium Priority'
#     else:
#         return 'High Priority'

# Read the Excel file directly
file_path = 'data.xlsx'
df = pd.read_excel(file_path)
yes_df = df[df['Service provided'] == 'Yes']

if budget > 0:
    st.write("## Data Preview")
    st.write(df.head(200))

    # Calculate the financial aid score for each applicant
    yes_df['Aid Score'] = yes_df.apply(compute_aid_score, axis=1)

    # Drop rows with NaN aid scores
    yes_df = yes_df.dropna(subset=['Aid Score'])

    # Normalize the aid scores to sum to 1
    yes_df['Normalized Aid Score'] = yes_df['Aid Score'] / yes_df['Aid Score'].sum()

    # Distribute the budget based on normalized aid scores
    yes_df['Allocated Budget (CHF)'] = yes_df['Normalized Aid Score'] * budget

    # Calculate the average aid score of all data points
    average_score = yes_df['Aid Score'].mean()

    # Split the data into two halves based on whether the aid score is above or below the average
    above_average = yes_df[yes_df['Aid Score'] > average_score]
    below_average = yes_df[yes_df['Aid Score'] <= average_score]

    # Calculate the average aid score of each half
    avg_above = above_average['Aid Score'].mean()
    avg_below = below_average['Aid Score'].mean()

    # Split each half into two further halves based on whether the aid score is above or below the average of that half
    high_priority = above_average[above_average['Aid Score'] > avg_above]
    medium_priority = above_average[above_average['Aid Score'] <= avg_above]
    low_priority = below_average[below_average['Aid Score'] > avg_below]
    very_low_priority = below_average[below_average['Aid Score'] <= avg_below]

    # Assign priorities accordingly based on the four resulting groups
    high_priority['Priority'] = 'High Priority'
    medium_priority['Priority'] = 'Medium Priority'
    low_priority['Priority'] = 'Low Priority'
    very_low_priority['Priority'] = 'Very Low Priority'

    # Combine the dataframes
    yes_df = pd.concat([high_priority, medium_priority, low_priority, very_low_priority])

    # Pie chart of marital status
    st.write("## Pie Chart of Marital Status")
    marital_status_counts = yes_df['Marital status'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(marital_status_counts, labels=marital_status_counts.index, autopct='%1.1f%%')
    st.pyplot(fig)

    # Histogram of aid scores
    st.write("## Histogram of Aid Scores")
    fig, ax = plt.subplots()
    ax.hist(yes_df['Aid Score'], bins=10, edgecolor='black')
    ax.set_xlabel('Aid Score')
    ax.set_ylabel('Number of Applicants')
    st.pyplot(fig)

    # Histogram of allocated budget
    st.write("## Allocated Budget Distribution")
    fig, ax = plt.subplots()
    ax.hist(yes_df['Allocated Budget (CHF)'], bins=10, edgecolor='black')
    ax.set_xlabel('Allocated Budget (CHF)')
    ax.set_ylabel('Number of Applicants')
    st.pyplot(fig)

    st.write("## Data with Aid Scores and Allocated Budget")
    st.write(yes_df.head(200))

    # Create histogram
    st.write("## Histogram: Income vs Allocated Budget")
    fig, ax = plt.subplots()
    sns.histplot(data=yes_df, x='Income (yearly in CHF)', y='Allocated Budget (CHF)', bins=20, ax=ax)
    ax.set_xlabel('Income (yearly in CHF)')
    ax.set_ylabel('Allocated Budget (CHF)')
    st.pyplot(fig)

    # Create pie chart of priorities
    st.write("## Pie Chart of Priorities")
    priority_counts = yes_df['Priority'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(priority_counts, labels=priority_counts.index, autopct='%1.1f%%')
    st.pyplot(fig)

