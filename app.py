import streamlit as st
import gmail
import pickle
import os

from preprocessing import transform_text

# Load saved model and vectorizer
# @st.cache(allow_output_mutation=True)
def load_model():
    tfidf = pickle.load(open('vectorizer.pkl', 'rb'))
    model = pickle.load(open('model.pkl', 'rb'))
    return tfidf, model

import pandas as pd
# Main function to run the Streamlit app
def main():
    st.title("Fetch Data from Gmail and Classify Emails as Spam or Not Spam")
    st.write("This app fetches emails from your Gmail account and classifies them as spam or not spam.")
    
    # Display the app's features with style
    st.markdown(
        """
        <div style="background-color: #f4f4f4; padding: 10px; border-radius: 10px;">
            <p style="font-size: 18px; font-weight: bold;">App Features:</p>
            <ul>
                <li>The app uses a machine learning model trained on the Kaggle SMS Spam Collection dataset.</li>
                <li>The model is trained on the TF-IDF vectorized text data of the emails.</li>
                <li>The app fetches the emails using the Gmail API and then classifies them using the trained model.</li>
                <li>The app displays the fetched emails along with their date, subject, sender, and spam classification.</li>
                <li>The app also displays the content of the email.</li>
                <li>The app allows you to login to your Gmail account to fetch emails.</li>
                <li>The app uses a custom token-based authentication system to securely store your credentials.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Load model
    tfidf, model = load_model()

    # Check if logged in
    if 'token.json' in os.listdir():
        display_emails(tfidf, model)
    else:
        display_home()



# Function to display home page
def display_home():
    st.header("Home")
    st.write("Please login to your Google account.")
    
    # Check if already logged in
    if 'token.json' not in os.listdir():
        # Display login button if not logged in
        if st.button("Login with Google"):
            creds = gmail.authenticate()
            if creds:
                st.success("Login successful. You can now fetch emails.")
                # Save credentials to token.json
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                # Reload the page to show the logout button
                st.experimental_rerun()
    else:
        # Display logout button if logged in
        if st.button("Logout"):
            os.remove('token.json')
            st.success("Logout successful.")
            # Reload the page to show the login button
            st.experimental_rerun()


# Function to display fetched emails
def display_emails(tfidf, model):
    st.header("Fetched Emails")

    # Logout Button
    if st.button("Logout"):
        os.remove('token.json')
        st.success("Logout successful.")
        st.empty()  # Clear the content
        display_home()  # Display the home page again

    with st.spinner("Fetching emails..."):  # Display spinner while fetching emails
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
                    "Spam": "Yes" if prediction == 1 else "No",
                    "See": message_content  # Add the mail content to the DataFrame
                })

            # Create a DataFrame from the email data
            email_df = pd.DataFrame(email_data)

            # Pagination
            items_per_page = 50
            page_number = st.number_input("Page Number", min_value=1, max_value=len(email_df) // items_per_page + 1)
            start_index = (page_number - 1) * items_per_page
            end_index = min(start_index + items_per_page, len(email_df)) 
            email_df_page = email_df.iloc[start_index:end_index] 

            # Display the DataFrame
            st.dataframe(email_df_page) 
            
        else:
            st.write("No emails found.")


# Function to predict spam email
def predict(email_content, tfidf, model):
    transformed_email = transform_text(email_content)
    vectorized_email = tfidf.transform([transformed_email])
    prediction = model.predict(vectorized_email)[0]
    return prediction

if __name__ == "__main__":
    main()
