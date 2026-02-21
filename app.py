import streamlit as st
from pypdf import PdfReader
import time
from gtts import gTTS
from io import BytesIO
import re
from gtts.tts import gTTSError

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
        
        # Clean sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', full_text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if st.button("▶️ Start Reading"):
            text_placeholder = st.empty()
            audio_placeholder = st.empty()
            current = 0
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                
                # Highlight current sentence in full text
                highlighted = []
                for j, sent in enumerate(sentences):
                    if j == current:
                        highlighted.append(f"**{sent}**")
                    else:
                        highlighted.append(sent)
                text_placeholder.markdown(" ".join(highlighted))
                
                # Safe TTS with retries
                audio_fp = BytesIO()
                success = False
                for attempt in range(5):
                    try:
                        tts = gTTS(text=sentence, lang='en', slow=False)
                        tts.write_to_fp(audio_fp)
                        audio_fp.seek(0)
                        success = True
                        break
                    except (gTTSError, Exception):
                        if attempt == 4:
                            st.error("TTS temporarily unavailable – retrying in a moment...")
                            break
                        time.sleep(1.5 * (attempt + 1)) # backoff
                
                if success:
                    audio_placeholder.audio(audio_fp, format="audio/mp3", autoplay=True)
                
                # Dynamic sleep based on speaking length (\~180-200 words per minute)
                word_count = len(sentence.split())
                sleep_time = max(1.5, word_count * 0.35)
                time.sleep(sleep_time)
                
                current += 1
            
            st.success("✅ Full report finished reading!")
