import streamlit as st
import gmail
import pickle
import os

from preprocessing import transform_text

# Load saved model and vectorizer
@st.cache(allow_output_mutation=True)
def load_model():
    tfidf = pickle.load(open('vectorizer.pkl', 'rb'))
    model = pickle.load(open('model.pkl', 'rb'))
    return tfidf, model

import pandas as pd

# Function to fetch emails and display them
def fetch_and_display_emails(tfidf, model):
    st.header("Fetched Emails")

    # Logout Button
    if st.button("Logout"):
        os.remove('token.json')
        st.success("Logout successful.")
        st.empty()  # Clear the content
        display_home()  # Display the home page again

    emails = gmail.fetch_emails()
    if emails:
        email_data = []
        for message_id, email_info in emails:
            message_content = gmail.fetch_email_content(message_id)
            prediction = predict(message_content, tfidf, model)
            email_data.append({
                "Date": email_info.get('date', ''),
                "Subject": email_info.get('subject', ''),
                "From": email_info.get('from', ''),
                "Spam": "Yes" if prediction == 1 else "No"
            })

        # Create a DataFrame from the email data
        email_df = pd.DataFrame(email_data)

        # Display the DataFrame
        st.dataframe(email_df)

    else:
        st.write("No emails found.")

# Main function to run the Streamlit app
def main():
    st.title("Email/SMS Spam Classifier")

    # Load model
    tfidf, model = load_model()

    # Check if the 'fetch_emails' query parameter is present in the URL
    query_params = st.experimental_get_query_params()
    if 'fetch_emails' in query_params:
        fetch_and_display_emails(tfidf, model)
    else:
        display_home()

# Function to display home page
def display_home():
    st.header("Home")
    st.write("Please login to your Google account.")
    if st.button("Login with Google"):
        gmail.authenticate()
        st.success("Login successful.")
        # Redirect to the route for fetching emails
        st.experimental_set_query_params(fetch_emails=True)

# Function to predict spam email
def predict(email_content, tfidf, model):
    transformed_email = transform_text(email_content)
    vectorized_email = tfidf.transform([transformed_email])
    prediction = model.predict(vectorized_email)[0]
    return prediction

if __name__ == "__main__":
    main()
