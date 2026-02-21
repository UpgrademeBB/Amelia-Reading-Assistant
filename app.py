import streamlit as st
from pypdf import PdfReader
import time
from gtts import gTTS
from io import BytesIO
import re
from gtts.tts import gTTSError

st.set_page_config(page_title="Amelia Reader", layout="wide")
st.title("Amelia Reads Your Reports")

# Session state
if 'current_sentence' not in st.session_state:
    st.session_state.current_sentence = 0
if 'playback_state' not in st.session_state:
    st.session_state.playback_state = 'stopped' # stopped, playing, paused
if 'sentences' not in st.session_state:
    st.session_state.sentences = []

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
    
    if pdf_file and not st.session_state.sentences:
        reader = PdfReader(pdf_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n\n"
        
        sentences = re.split(r'(?<=[.!?])\s+', full_text.strip())
        st.session_state.sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
    
    if st.session_state.sentences:
        # Playback controls
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
        
        with btn_col1:
            if st.session_state.playback_state == 'stopped':
                if st.button("▶️ Start Reading", type="primary"):
                    st.session_state.playback_state = 'playing'
                    st.session_state.current_sentence = 0
                    st.rerun()
        
        with btn_col2:
            if st.session_state.playback_state == 'playing':
                if st.button("⏸️ Pause"):
                    st.session_state.playback_state = 'paused'
                    st.rerun()
            elif st.session_state.playback_state == 'paused':
                if st.button("▶️ Resume"):
                    st.session_state.playback_state = 'playing'
                    st.rerun()
        
        with btn_col3:
            if st.button("⏹️ Stop"):
                st.session_state.playback_state = 'stopped'
                st.session_state.current_sentence = 0
                st.rerun()
        
        # Progress and text
        progress = st.progress(st.session_state.current_sentence / len(st.session_state.sentences) if st.session_state.sentences else 0)
        
        text_placeholder = st.empty()
        highlighted = []
        for j, sent in enumerate(st.session_state.sentences):
            if j == st.session_state.current_sentence:
                highlighted.append(f"**{sent}**")
            else:
                highlighted.append(sent)
        text_placeholder.markdown(" ".join(highlighted))
        
        audio_placeholder = st.empty()
        
        # Playback logic
        if (st.session_state.playback_state == 'playing' and 
            st.session_state.current_sentence < len(st.session_state.sentences)):
            
            sentence = st.session_state.sentences[st.session_state.current_sentence]
            
            # Safe TTS with retries
            audio_fp = BytesIO()
            success = False
            for attempt in range(4):
                try:
                    tts = gTTS(text=sentence, lang='en', slow=False)
                    tts.write_to_fp(audio_fp)
                    audio_fp.seek(0)
                    success = True
                    break
                except gTTSError:
                    time.sleep(1.2 * (attempt + 1))
            
            if success:
                audio_placeholder.audio(audio_fp, format="audio/mp3", autoplay=True)
            
            # Natural speaking pace
            words = len(sentence.split())
            sleep_time = max(1.8, words * 0.33)
            time.sleep(sleep_time)
            
            st.session_state.current_sentence += 1
            
            if st.session_state.current_sentence >= len(st.session_state.sentences):
                st.session_state.playback_state = 'stopped'
                st.success("✅ Amelia finished reading the full report!")
            else:
                st.rerun()
        
        elif st.session_state.current_sentence >= len(st.session_state.sentences):
            st.success("✅ Full report completed!")
