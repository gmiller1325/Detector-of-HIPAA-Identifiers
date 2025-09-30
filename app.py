# app.py
import streamlit as st
import google.generativeai as genai

# --- Page and Model Configuration ---

# Set the page configuration for your app
st.set_page_config(
    page_title="HIPAA Identifier Detector",
    page_icon="🛡️",
    layout="centered"
)

# Configure the Gemini API using Streamlit's secrets management
# This is the secure, standard method we learned
try:
    genai.configure(api_key=st.secrets["google_api_key"])
except (KeyError, AttributeError):
    st.error("Your Google API key is missing or invalid. Please create a `.streamlit/secrets.toml` file with your key.")
    st.stop()


# --- Core Detection Function ---

def detect_hipaa_identifiers(text_input: str) -> str:
    """
    Sends the text to the Gemini model with specific instructions to detect HIPAA identifiers.
    Includes error handling for API calls.
    """
    # This is the detailed prompt you provided, which instructs the model on its task
    prompt = f"""
I want to detect any of the 18 HIPAA identifiers under Section 164.514(a) of the HIPAA Privacy Rules for an individual or of relatives, employers, or household members of the individual. Here are the identifiers:

“1. Names;
2. All geographical subdivisions smaller than a State, including street address, city, county, precinct, zip code, and their equivalent geocodes, except for the initial three digits of a zip code if specific census conditions are met.
3. All elements of dates (except year) for dates directly related to an individual, and all ages over 89.
4. Phone numbers;
5. Fax numbers;
6. Electronic mail addresses;
7. Social Security numbers;
8. Medical record numbers;
9. Health plan beneficiary numbers;
10. Account numbers;
11. Certificate/license numbers;
12. Vehicle identifiers and serial numbers, including license plate numbers;
13. Device identifiers and serial numbers;
14. Web Universal Resource Locators (URLs);
15. Internet Protocol (IP) address numbers;
16. Biometric identifiers, including finger and voice prints;
17. Full face photographic images and any comparable images; and
18. Any other unique identifying number, characteristic, or code.”

Please detect HIPAA identifiers in a step-by-step fashion. First, internally identify all named entities. Then, determine and output which of those entities are part of the 18 HIPAA identifiers.

Now you detect HIPAA identifiers, please explain your thinking using this format:

Rationale:
<your thinking>

Final Answer:
<List of any HIPAA identifiers found or write "No HIPAA identifiers in the text">

Here is the text to consider:

---
{text_input}
---
"""

    try:
        # We use the latest Gemini model, as we learned older names can be deprecated
        model = genai.GenerativeModel('gemini-2.5-pro')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # This handles potential API errors, like the 429 quota error we encountered
        return f"Error: Could not contact the AI model. This might be due to a rate limit or other API issue. Please try again later. Details: {e}"


# --- Streamlit App UI ---

st.title("🛡️ HIPAA Identifier Detector")
st.markdown(
    "This app uses AI to detect Protected Health Information (PHI) based on the 18 HIPAA identifiers. Paste text below to analyze it for potential PHI."
)

# Example text from your prompt
example_text = (
    "David Johnson, born 11/02/1980, lives at 22 Pine Street, Boston, MA 02108. His phone number is (617) 555-3210. He came in complaining of headaches and blurred vision."
)

# Text area for user input
user_input = st.text_area(
    "Enter text to be analyzed for HIPAA identifiers:",
    value=example_text,
    height=200,
)

# Button to trigger the analysis
if st.button("Detect Identifiers", type="primary"):
    if user_input and user_input.strip():
        with st.spinner("🔍 Analyzing text..."):
            result = detect_hipaa_identifiers(user_input)
            st.subheader("Analysis Result")
            # The model's response is already well-formatted, so we can display it directly
            st.markdown(result)
    else:
        st.warning("Please enter some text to analyze.")
