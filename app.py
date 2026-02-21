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
    st.caption("Amelia Movement Loop (MP4)")
    video_file = st.file_uploader("Upload Amelia typing loop (MP4)", type="mp4")
    if video_file:
        st.video(video_file, format="video/mp4", loop=True, autoplay=True)

with col2:
    st.subheader("Your Report")
    pdf_file = st.file_uploader("Upload PDF report (any size)", type="pdf")
    
    if pdf_file:
        reader = PdfReader(pdf_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n\n"
        
        # Split into safe 5000-char chunks
        chunk_size = 5000
        chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
        
        sentences = [s.strip() + "." for s in full_text.replace("\n", " ").split(".") if s.strip()]
        
        if st.button("▶️ Start Reading"):
            placeholder = st.empty()
            current_sentence = 0
            
            for chunk_idx, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                    
                # Generate and play voice for this chunk
                tts = gTTS(text=chunk, lang='en', slow=False)
                audio_bytes = BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                
                # Highlight only sentences in this chunk
                chunk_sentences = [s.strip() + "." for s in chunk.replace("\n", " ").split(".") if s.strip()]
                for sent in chunk_sentences:
                    highlighted = " ".join(
                        [f"**{sentences[j]}**" if j == current_sentence else sentences[j] 
                         for j in range(len(sentences))]
                    )
                    placeholder.markdown(highlighted)
                    current_sentence += 1
                    time.sleep(1.2)
            
            st.success("Full report finished")
