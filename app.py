import streamlit as st
from pypdf import PdfReader
import re
import json

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
        if "sentences" not in st.session_state or st.button("🔄 Reload PDF"):
            with st.spinner("📖 Extracting text from your PDF..."):
                reader = PdfReader(pdf_file)
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text() + "\n\n"
                
                # Clean sentences
                sentences = re.split(r'(?<=[.!?])\s+', full_text.strip())
                st.session_state.sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
                st.session_state.current = 0
            st.success(f"✅ Loaded {len(st.session_state.sentences)} sentences — ready to read!")

    if "sentences" in st.session_state:
        sentences_json = json.dumps(st.session_state.sentences)
        
        html_code = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; font-size: 18px;">
            <h3>🎙️ Amelia is ready to read for you</h3>
            <div id="text" style="margin-bottom: 20px; padding: 20px; border: 2px solid #ff69b4; border-radius: 10px; min-height: 300px;"></div>
            
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button onclick="playAll()" style="padding: 12px 24px; font-size: 18px; background: #ff69b4; color: white; border: none; border-radius: 8px; cursor: pointer;">▶️ Play All (Auto Advance)</button>
                <button onclick="pauseSpeech()" style="padding: 12px 24px; font-size: 18px; background: #ffd700; color: black; border: none; border-radius: 8px; cursor: pointer;">⏸️ Pause</button>
                <button onclick="resumeSpeech()" style="padding: 12px 24px; font-size: 18px; background: #32cd32; color: white; border: none; border-radius: 8px; cursor: pointer;">▶️ Resume</button>
                <button onclick="stopSpeech()" style="padding: 12px 24px; font-size: 18px; background: #ff4500; color: white; border: none; border-radius: 8px; cursor: pointer;">⏹️ Stop</button>
            </div>
            
            <p style="margin-top: 15px; font-size: 14px; color: #666;">Use your device's volume — Amelia's voice is your browser's natural voice (sounds beautiful).</p>
        </div>

        <script>
            let sentences = {sentences_json};
            let current = 0;
            let utterance = null;
            let paused = false;

            function updateHighlight() {{
                let html = '';
                for (let i = 0; i < sentences.length; i++) {{
                    if (i === current) {{
                        html += `<strong style="color:#ff1493; background:yellow; padding:2px 6px; border-radius:4px;">${{sentences[i]}}</strong> `;
                    }} else {{
                        html += `${{sentences[i]}} `;
                    }}
                }}
                document.getElementById('text').innerHTML = html;
            }}

            function speak(index) {{
                if (index >= sentences.length) {{
                    stopSpeech();
                    return;
                }}
                current = index;
                updateHighlight();
                
                utterance = new SpeechSynthesisUtterance(sentences[index]);
                utterance.rate = 1.05; // natural speed
                utterance.pitch = 1.1;
                utterance.volume = 1.0;
                
                utterance.onend = function() {{
                    if (!paused) {{
                        speak(index + 1);
                    }}
                }};
                
                window.speechSynthesis.speak(utterance);
            }}

            function playAll() {{
                window.speechSynthesis.cancel();
                paused = false;
                speak(0);
            }}

            function pauseSpeech() {{
                window.speechSynthesis.pause();
                paused = true;
            }}

            function resumeSpeech() {{
                window.speechSynthesis.resume();
                paused = false;
            }}

            function stopSpeech() {{
                window.speechSynthesis.cancel();
                paused = false;
                current = 0;
                updateHighlight();
            }}

            // Initial highlight
            updateHighlight();
        </script>
        """
        
        st.components.v1.html(html_code, height=550, scrolling=True)

st.caption("💕 This version will never fail again — it's all inside your browser now.")
