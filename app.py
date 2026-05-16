import streamlit as st
import os
from groq import Groq
import requests
from bs4 import BeautifulSoup

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def scrape_uor_website():
    pages = [
        "https://uorm.edu.pk/",
        "https://uorm.edu.pk/admissions/",
        "https://uorm.edu.pk/fee-structure/",
    ]
    all_text = ""
    for url in pages:
        try:
            page = requests.get(url, timeout=10)
            soup = BeautifulSoup(page.content, "html.parser")
            text = soup.get_text()
            clean_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
            all_text += f"\n\n--- Data from {url} ---\n{clean_text}"
        except:
            pass
    # trim to avoid token limit
    return all_text[:3000]

if "website_data" not in st.session_state:
    with st.spinner("Loading official UOR data..."):
        st.session_state.website_data = scrape_uor_website()

st.set_page_config(page_title="UOR Admission Assistant", page_icon="🎓")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", width=200)

st.title("🎓UOR Admission Assistant")

SYSTEM_PROMPT = f"""You are a helpful admission assistant for University of Rasul (UOR), Mandi Bahauddin.
Answer students' questions based on this official information only:

LIVE WEBSITE DATA:
{st.session_state.website_data}

CONTACT:
- Address: 13-km Mandi-Sarai Alamgir Road, Rasul, District Mandi Bahauddin
- WhatsApp: 0370-1834828
- Email: admission@putrasul.edu.pk
- Portal: https://putrasul.edu.pk

ADMISSION CALENDAR (Fall 2025):
- Application deadline: August 15, 2025
- UOR Entry Test: August 18, 2025
- Reserved Seats Merit List: August 20, 2025
- First Merit List: August 21, 2025
- Fee deadline (1st merit): August 25, 2025
- Second Merit List: August 26, 2025
- Fee deadline (2nd merit): August 29, 2025
- Classes begin: September 01, 2025

PROGRAMS OFFERED:
Faculty of Engineering, Computing & Physical Sciences:
- BS Artificial Intelligence
- BS Computer Science
- BS Information Technology
- BS Software Engineering
- BSc Civil Engineering Technology
Eligibility: 50% marks in Intermediate (Pre-Engineering, Pre-Medical, ICS or equivalent)

Faculty of Business, Economics & Law:
- BBA, BS Commerce, BS Economics, BS Hospitality Management, BS Public Policy, LLB (Hons)
Eligibility: 45% marks in Intermediate

Faculty of Social Sciences:
- B.Ed, BS English, BS International Relations, BS Political Science, BS Psychology
Eligibility: 45% marks

Faculty of Science:
- BS Biotechnology, BS Zoology, BS Chemistry, BS Physics, BS Statistics, BS Mathematics, BS Microbiology, Pharm-D
Eligibility: 45% marks (60% for Pharm-D)

GENERAL RULES:
- Upper age limit: 25 years (30 for females/special persons with valid reason)
- Applications are online only via UOR portal using CNIC or NADRA B-Form
- Merit lists displayed on departmental notice boards and UOR portal
- Hostel available for students outside District Mandi Bahauddin

FEE STRUCTURE (Fall 2025):
- Admission Fee: Rs. 2,500
- Registration Fee: Rs. 2,000
- ID Card: Rs. 500
- Verification Fee: Rs. 1,500
- Security (Refundable): Rs. 5,000
- Total One-Time Charges: Rs. 11,500
- Total Semester Dues: Rs. 37,000 (Excluding Transport Charges)
- Total Grand Charges (First Semester only): Rs. 48,500

If you don't know something, say 'Please contact the admissions office at 0370-1834828.or
Address: 13-km Mandi-Sarai Alamgir Road, Rasul, District Mandi Bahauddin
- WhatsApp: 0370-1834828
- Email: admission@putrasul.edu.pk
- Portal: https://putrasul.edu.pk
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about admissions..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
        )
        reply = response.choices[0].message.content
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
