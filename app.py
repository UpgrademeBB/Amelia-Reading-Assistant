import streamlit as st
from PyPDF2 import PdfReader
import time

st.set_page_config(page_title="Amelia Reader", layout="wide")
st.title("Amelia Reads Your Reports")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Amelia")
    amelia_photo = st.file_uploader("Upload Amelia photo", type=["jpg", "png"])
    if amelia_photo:
        st.image(amelia_photo, width=250)

with col2:
    st.subheader("Your Report")
    pdf_file = st.file_uploader("Upload PDF report", type="pdf")
    
    if pdf_file:
        reader = PdfReader(pdf_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n\n"
        
        sentences = [s.strip() + "." for s in full_text.replace("\n", " ").split(".") if s.strip()]
        
        if st.button("Start Reading"):
            placeholder = st.empty()
            for i in range(len(sentences)):
                highlighted = " ".join(
                    [f"**{sent}**" if j == i else sent for j, sent in enumerate(sentences)]
                )
                placeholder.markdown(highlighted)
                time.sleep(1.2) # change 1.2 to faster/slower
