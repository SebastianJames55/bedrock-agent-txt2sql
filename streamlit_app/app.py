import InvokeAgent as agenthelper
import streamlit as st
import json
import pandas as pd
from PIL import Image, ImageOps, ImageDraw
import os

# Streamlit page configuration
st.set_page_config(page_title="Text2SQL Agent", page_icon=":robot_face:", layout="wide")

# Function to crop image into a circle
def crop_to_circle(image):
    mask = Image.new('L', image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0) + image.size, fill=255)
    result = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    result.putalpha(mask)
    return result

# Title
st.title("Text2SQL Agent - Amazon Athena")

# Display a text box for input
prompt = st.text_input("Please enter your query?", max_chars=2000)
prompt = prompt.strip()

# Display a primary button for submission
submit_button = st.button("Submit", type="primary")

# Display a button to end the session
end_session_button = st.button("End Session")

# Sidebar for user input
st.sidebar.title("Trace Data")

# Get the root directory of the project
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
human_image_path = os.path.join(root_dir, 'images/human_face.png')
robot_image_path = os.path.join(root_dir, 'images/robot_face.jpg')

# Session State Management
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Function to parse and format response
def format_response(response_body):
    try:
        # Try to load the response as JSON
        data = json.loads(response_body)
        # If it's a list, convert it to a DataFrame for better visualization
        if isinstance(data, list):
            return pd.DataFrame(data)
        else:
            return response_body
    except json.JSONDecodeError:
        # If response is not JSON, return as is
        return response_body



# Handling user input and responses
if submit_button and prompt:
    event = {
        "sessionId": "MYSESSION",
        "question": prompt
    }
    response = agenthelper.lambda_handler(event, None)
    
    try:
        # Parse the JSON string
        if response and 'body' in response and response['body']:
            response_data = json.loads(response['body'])
            print("TRACE & RESPONSE DATA ->  ", response_data)
        else:
            print("Invalid or empty response received")
    except json.JSONDecodeError as e:
        print("JSON decoding error:", e)
        response_data = None 
    
    try:
        # Extract the response and trace data
        all_data = format_response(response_data['response'])
        the_response = response_data['trace_data']
    except:
        all_data = "..." 
        the_response = "Apologies, but an error occurred. Please rerun the application" 

    # Use trace_data and formatted_response as needed
    st.sidebar.text_area("", value=all_data, height=300)
    st.session_state['history'].append({"question": prompt, "answer": the_response})
    st.session_state['trace_data'] = the_response

    
    

if end_session_button:
    st.session_state['history'].append({"question": "Session Ended", "answer": "Thank you for using AnyCompany Support Agent!"})
    event = {
        "sessionId": "MYSESSION",
        "question": "placeholder to end session",
        "endSession": True
    }
    agenthelper.lambda_handler(event, None)
    st.session_state['history'].clear()


# Display conversation history
st.write("## Conversation History")

for idx, chat in enumerate(reversed(st.session_state['history'])):
    
    # Creating columns for Question
    col1_q, col2_q = st.columns([2, 10])
    with col1_q:
        human_image = Image.open(human_image_path)
        circular_human_image = crop_to_circle(human_image)
        st.image(circular_human_image, width=125)
    with col2_q:
        st.text_area("Q:", value=chat["question"], height=50, key=str(chat)+"q", disabled=True)

    # Creating columns for Answer
    col1_a, col2_a = st.columns([2, 10])
    if isinstance(chat["answer"], pd.DataFrame):
        with col1_a:
            robot_image = Image.open(robot_image_path)
            circular_robot_image = crop_to_circle(robot_image)
            st.image(circular_robot_image, width=100)
        with col2_a:
            st.dataframe(chat["answer"])
    else:
        with col1_a:
            robot_image = Image.open(robot_image_path)
            circular_robot_image = crop_to_circle(robot_image)
            st.image(circular_robot_image, width=150)
        with col2_a:
            st.text_area("A:", value=chat["answer"], height=100, key=str(chat)+"a")


# Example Prompts Section


# Increase the maximum width of the text in each cell of the dataframe
pd.set_option('display.max_colwidth', None)

# Define the queries and their descriptions
query_data = {
    "Test Prompts": [
        "Show me details of any customer.",
        "Return to me the number of products.",
        "Let me see the number of customer having a child."
}

# Create DataFrame
queries_df = pd.DataFrame(query_data)

# Display the DataFrame in Streamlit
st.write("## Test Prompts for Amazon Athena")
st.dataframe(queries_df, width=900)  # Adjust the width to fit your layout