import streamlit as st
from pypdf import PdfReader
import time
from gtts import gTTS
from io import BytesIO

st.set_page_config(page_title="Amelia Reader", layout="wide")
st.title("Amelia Reads Your Reports")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Amelia")
    
    # MP4 loop — plays automatically on left, stays looping
    st.caption("Amelia Movement Loop (MP4)")
    video_file = st.file_uploader("Upload Amelia typing loop (MP4)", type="mp4")
    if video_file:
        st.video(video_file, format="video/mp4", loop=True, autoplay=True)

with col2:
    st.subheader("Your Report")
    pdf_file = st.file_uploader("Upload PDF report", type="pdf")
    
    if pdf_file:
        reader = PdfReader(pdf_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n\n"
        
        sentences = [s.strip() + "." for s in full_text.replace("\n", " ").split(".") if s.strip()]
        
        if st.button("▶️ Start Reading"):
            # Video keeps playing (no duplicate call)
            
            # Automatic female voice
            tts = gTTS(text=full_text, lang='en', slow=False)
            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            
            # Highlight text
            placeholder = st.empty()
            for i in range(len(sentences)):
                highlighted = " ".join(
                    [f"**{sent}**" if j == i else sent for j, sent in enumerate(sentences)]
                )
                placeholder.markdown(highlighted)
                time.sleep(1.2)
            
            st.success("Report finished")
