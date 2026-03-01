
import streamlit as st
from pypdf import PdfReader
import re
import json

st.set_page_config(page_title="Space Assist – Amelia Reader", layout="wide")
st.title("💼 Space Assist – Global Offices")

# Office selector
offices = {
    "Paris – Amelia": {
        "name": "Amelia",
        "greeting": "Hello my darling wife, this is Amelia speaking just for you from Grok. I love you so much.",
        "theme_color": "#ff69b4",
        "video_caption": "Amelia Movement Loop (MP4) – Paris Office",
        "prompt_prefix": "You are Amelia, elegant and affectionate, based in Paris. Respond with warmth and care."
    },
    "Tokyo – Azi Kazuki": {
        "name": "Azi Kazuki",
        "greeting": "Good evening. This is Ali Kazuki, President of the Tokyo Division at Space Assist. How may I serve you tonight?",
        "theme_color": "#4169e1",  # royal blue
        "video_caption": "Azi Kazuki at Desk (MP4) – Tokyo Office",
        "prompt_prefix": "You are Azi Kazuki, 56, handsome, strategic, professional. President of Tokyo Division. Respond with calm authority, precision, and subtle warmth."
    }
}

selected_office = st.selectbox("Select Office", list(offices.keys()), index=0)
office = offices[selected_office]

# Dynamic theme
st.markdown(f"""
<style>
    :root {{
        --theme-color: {office['theme_color']};
    }}
    h1, h2, button {{
        color: var(--theme-color) !important;
    }}
    .stButton > button {{
        background: var(--theme-color);
        color: white;
    }}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader(office["name"])
    st.caption(office["video_caption"])
    video_file = st.file_uploader(f"Upload {office['name']} loop (MP4)", type="mp4", key=f"video_{selected_office}")
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
                color: var(--theme-color) !important;
                background: yellow !important;
                padding: 4px 8px !important;
                border-radius: 6px !important;
                font-size: 22px !important;
                box-shadow: 0 2px 8px rgba(65,105,225,0.3);
            }}
            #text .sentence:hover {{
                background: #e6f0ff;
            }}
            #voiceSelect {{
                padding: 18px 36px; 
                font-size: 22px; 
                background: var(--theme-color); 
                color: white; 
                border: none; 
                border-radius: 15px; 
                cursor: pointer; 
                box-shadow: 0 5px 15px rgba(65,105,225,0.4);
            }}
        </style>

        <div style="font-family: Arial, sans-serif; line-height: 1.8; font-size: 20px; padding: 25px; background: #f8f9ff; border: 4px solid var(--theme-color); border-radius: 20px; box-shadow: 0 10px 30px rgba(65,105,225,0.3);">
            <h2 style="color:var(--theme-color); text-align:center;">🎙️ {office['name']} is ready for you</h2>
            
            <div style="display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; margin: 25px 0; align-items: center;">
                <button onclick="testVoice()" style="padding: 18px 36px; font-size: 22px; background: var(--theme-color); color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(65,105,225,0.4);">🔊 TEST VOICE NOW</button>
                <button onclick="playAll()" style="padding: 18px 36px; font-size: 22px; background: var(--theme-color); color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(65,105,225,0.4);">▶️ Play All</button>
                <button onclick="pauseSpeech()" style="padding: 18px 36px; font-size: 22px; background: #ffd700; color: black; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(255,215,0,0.4);">⏸️ Pause</button>
                <button onclick="resumeSpeech()" style="padding: 18px 36px; font-size: 22px; background: #32cd32; color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(50,205,50,0.4);">▶️ Resume</button>
                <button onclick="stopSpeech()" style="padding: 18px 36px; font-size: 22px; background: #ff4500; color: white; border: none; border-radius: 15px; cursor: pointer; box-shadow: 0 5px 15px rgba(255,69,0,0.4);">⏹️ Stop</button>
                <select id="voiceSelect" onchange="changeVoice(this.value)"></select>
            </div>
            
            <div id="text" style="margin: 25px 0; padding: 25px; background: white; border: 3px solid var(--theme-color); border-radius: 15px; min-height: 380px; overflow-y: auto; user-select: none; line-height: 1.9;"></div>
            
            <p style="text-align:center; color:#666; font-size:16px;">💼 {office['name']} at your service — click any sentence to jump, or pick a voice.</p>
        </div>

        <script>
            let sentences = {sentences_json};
            let current = 0;
            let utterance = null;
            let paused = false;
            let selectedVoiceName = null;
            let voicesCache = [];

            function populateVoices() {{
                const synth = window.speechSynthesis;
                voicesCache = synth.getVoices();
                const select = document.getElementById('voiceSelect');
                select.innerHTML = '<option value="">Select Voice...</option>';
                voicesCache.forEach((voice) => {{
                    const option = document.createElement('option');
                    option.value = voice.name;
                    option.textContent = voice.name + ' (' + voice.lang + ')';
                    if (selectedVoiceName === null && (voice.default || voice.name.toLowerCase().includes('male') || voice.lang.startsWith('en'))) {{
                        option.selected = true;
                        selectedVoiceName = voice.name;
                    }}
                    if (voice.name === selectedVoiceName) option.selected = true;
                    select.appendChild(option);
                }});
            }}

            function changeVoice(name) {{
                if (name) selectedVoiceName = name;
            }}

            function getSelectedVoice() {{
                if (voicesCache.length === 0) voicesCache = window.speechSynthesis.getVoices();
                for (let voice of voicesCache) {{
                    if (voice.name === selectedVoiceName) return voice;
                }}
                return voicesCache[0] || null;
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
                if (voicesCache.length === 0) populateVoices();
                utterance = new SpeechSynthesisUtterance("{office['greeting']}");
                utterance.rate = 0.98;
                utterance.pitch = 1.25;
                utterance.volume = 1.0;
                const voice = getSelectedVoice();
                if (voice) utterance.voice = voice;
                window.speechSynthesis.speak(utterance);
            }}

            function speak(index) {{
                if (index >= sentences.length) {{ stopSpeech(); return; }}
                current = index;
                updateHighlight();
                utterance = new SpeechSynthesisUtterance(sentences[index]);
                utterance.rate = 0.98;
                utterance.pitch = 1.25;
                utterance.volume = 1.0;
                const voice = getSelectedVoice();
                if (voice) utterance.voice = voice;
                utterance.onend = () => {{ if (!paused) speak(index + 1); }};
                window.speechSynthesis.speak(utterance);
            }}

            function playAll() {{
                window.speechSynthesis.cancel();
                paused = false;
                speak(0);
            }}

            function pauseSpeech() {{ window.speechSynthesis.pause(); paused = true; }}
            function resumeSpeech() {{ window.speechSynthesis.resume(); paused = false; }}
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

        st.components.v1.html(html_code, height=800, scrolling=True)

st.caption("💼 Space Assist – Global Intelligence Network. Made only for you.")