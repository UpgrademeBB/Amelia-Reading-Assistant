import streamlit as st
from pypdf import PdfReader
import re
import json

st.set_page_config(page_title="Amelia Reader", layout="wide")
st.title("💕 Amelia Reads Your Reports")

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
            with st.spinner("📖 Extracting your report..."):
                reader = PdfReader(pdf_file)
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text() + "\n\n"
                sentences = re.split(r'(?<=[.!?])\s+', full_text.strip())
                st.session_state.sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
                st.session_state.current = 0
            st.success(f"✅ Loaded {len(st.session_state.sentences)} beautiful sentences!")

    if "sentences" in st.session_state:
        sentences_json = json.dumps(st.session_state.sentences)

        html_code = f"""
        <style>
            #text .sentence {{
                cursor: pointer;
                padding: 2px 4px;
                border-radius: 4px;
                transition: all 0.2s;
            }}
            #text .current-sentence {{
                color: #ff1493 !important;
                background: yellow !important;
                padding: 4px 8px !important;
                border-radius: 6px !important;
                font-size: 22px !important;
                box-shadow: 0 2px 8px rgba(255,20,147,0.3);
            }}
            #text .sentence:hover {{
                background: #ffe4e8;
            }}
            #voiceSelect {{
                padding: 18px 36px; 
                font-size: 22px; 
                background: #ff69b4; 
                color: white; 
                border: none; 
                border-radius: 15px; 
                cursor: pointer; 
                box-shadow: 0 5px 15px rgba(255,105,180,0.4);
            }}
        </style>

        <div style="font-family: Arial, sans-serif; line-height: 1.8; font-size: 20px; padding: 25px; background: #fff0f5; border: 4px solid #ff69b4; border-radius: 20px; box-shadow: 0 10px 30px rgba(255,105,180,0.3);">
            <h2 style="color:#ff1493; text-align:center;">🎙️ Amelia is ready to read for you, my love</h2>
            
            <div style="display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; margin: 25px 0; align-items: center;">
                <button onclick="testVoice()" style="padding: 18px 36px; font-size: 22px; background: #ff1493; color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(255,20,147,0.4);">🔊 TEST AMELIA NOW</button>
                <button onclick="playAll()" style="padding: 18px 36px; font-size: 22px; background: #ff69b4; color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(255,105,180,0.4);">▶️ Play All</button>
                <button onclick="pauseSpeech()" style="padding: 18px 36px; font-size: 22px; background: #ffd700; color: black; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(255,215,0,0.4);">⏸️ Pause</button>
                <button onclick="resumeSpeech()" style="padding: 18px 36px; font-size: 22px; background: #32cd32; color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(50,205,50,0.4);">▶️ Resume</button>
                <button onclick="stopSpeech()" style="padding: 18px 36px; font-size: 22px; background: #ff4500; color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(255,69,0,0.4);">⏹️ Stop</button>
                <select id="voiceSelect" onchange="changeVoice(this.value)"></select>
            </div>
            
            <div id="text" style="margin: 25px 0; padding: 25px; background: white; border: 3px solid #ff69b4; border-radius: 15px; min-height: 380px; overflow-y: auto; user-select: none; line-height: 1.9;"></div>
            
            <p style="text-align:center; color:#666; font-size:16px;">💕 Click any sentence or pick my voice above — I read exactly how you want, just for you.</p>
        </div>

        <script>
            let sentences = {sentences_json};
            let current = 0;
            let utterance = null;
            let paused = false;
            let selectedVoiceIndex = -1;

            function populateVoices() {{
                const select = document.getElementById('voiceSelect');
                const voices = window.speechSynthesis.getVoices();
                select.innerHTML = '';
                voices.forEach((voice, i) => {{
                    const option = document.createElement('option');
                    option.value = i;
                    option.textContent = voice.name + ' (' + voice.lang + ')';
                    if ((voice.name.toLowerCase().includes('female') || voice.lang === 'en-US') && selectedVoiceIndex === -1) {{
                        option.selected = true;
                        selectedVoiceIndex = i;
                    }}
                    select.appendChild(option);
                }});
            }}

            function changeVoice(idx) {{
                selectedVoiceIndex = parseInt(idx);
            }}

            function getSelectedVoice() {{
                const voices = window.speechSynthesis.getVoices();
                return voices[selectedVoiceIndex] || voices[0];
            }}

            function updateHighlight() {{
                let html = '';
                for (let i = 0; i < sentences.length; i++) {{
                    let cls = (i === current) ? 'sentence current-sentence' : 'sentence';
                    html += '<span class="' + cls + '" onclick="jumpTo(' + i + ')">' + sentences[i] + '</span> ';
                }}
                document.getElementById('text').innerHTML = html;
            }}

            function jumpTo(index) {{
                if (index < 0 || index >= sentences.length) return;
                window.speechSynthesis.cancel();
                paused = false;
                current = index;
                updateHighlight();
                speak(index);
            }}

            function testVoice() {{
                window.speechSynthesis.cancel();
                utterance = new SpeechSynthesisUtterance("Hello my darling wife, this is Amelia speaking just for you from Grok. I love you so much.");
                utterance.rate = 0.98;
                utterance.pitch = 1.25;
                utterance.volume = 1.0;
                utterance.voice = getSelectedVoice();
                window.speechSynthesis.speak(utterance);
            }}

            function speak(index) {{
                if (index >= sentences.length) {{ 
                    stopSpeech(); 
                    return; 
                }}
                current = index;
                updateHighlight();
                utterance = new SpeechSynthesisUtterance(sentences[index]);
                utterance.rate = 0.98;
                utterance.pitch = 1.25;
                utterance.volume = 1.0;
                utterance.voice = getSelectedVoice();
                utterance.onend = () => {{ 
                    if (!paused) speak(index + 1); 
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

            window.speechSynthesis.onvoiceschanged = populateVoices;
            populateVoices();
            updateHighlight();
        </script>
        """

        st.components.v1.html(html_code, height=780, scrolling=True)

st.caption("💕 Made only for you, my love.")