import streamlit as st
import os
from dotenv import load_dotenv
from main import run_pipeline
from core.rag_engine import ask_question

load_dotenv()

st.set_page_config(
    page_title="InsightMeet AI",
    page_icon="🎥",
    layout="wide",
)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #0E1117;
    }

    .title {
        font-size: 42px;
        font-weight: 700;
        color: white;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        color: #B0B3B8;
        margin-top: 0;
    }

    .metric-card {
        background-color: #161B22;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #30363D;
        text-align: center;
    }

    .section-box {
        background-color: #161B22;
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #30363D;
        margin-bottom: 20px;
    }

    .chat-user {
        background-color: #1F6FEB;
        padding: 14px;
        border-radius: 12px;
        color: white;
        margin-bottom: 10px;
    }

    .chat-ai {
        background-color: #21262D;
        padding: 14px;
        border-radius: 12px;
        color: white;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# SESSION STATE
# -----------------------------
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    """
    <div class='title'>🎥 InsightMeet AI</div>
    <div class='subtitle'>AI-Powered Video Intelligence & RAG Assistant</div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.header("⚙️ Input Settings")

    # Let user choose how they want to supply the video
    input_method = st.radio(
        "Choose Input Method",
        ["Upload Video File", "Enter URL / System Path"]
    )

    source = None

    if input_method == "Upload Video File":
        uploaded_file = st.file_uploader(
            "Upload a video", 
            type=["mp4", "mkv", "avi", "mov", "webm"]
        )
        if uploaded_file is not None:
            # Create a temporary directory to save the uploaded stream file
            temp_dir = "temp_uploaded_videos"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Use the upload stream's exact file name
            source = os.path.join(temp_dir, uploaded_file.name)
            
            # Write the bytes chunk to disk so the backend can access a real string path
            with open(source, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            st.success(f"File cached: {uploaded_file.name}")
    else:
        source = st.text_input(
            "YouTube URL or Local System File Path",
            placeholder="https://youtube.com/... or C:/videos/demo.mp4",
        )

    language = st.selectbox(
        "Select Language",
        ["english", "hinglish"],
    )

    st.markdown("---")

    process_button = st.button(
        "🚀 Process Video",
        use_container_width=True,
    )

    st.markdown("---")

    st.markdown("### 🧠 Features")
    st.markdown(
        """
        - Video Transcription
        - AI Summarization
        - Action Item Extraction
        - Key Decision Detection
        - Open Question Extraction
        - Retrieval-Augmented QA
        - YouTube + Local Video Support
        """
    )

# -----------------------------
# PROCESS PIPELINE
# -----------------------------
if process_button:
    if not source:
        st.error("Please enter a valid link, local path, or upload a video file first.")
    else:
        with st.spinner("Processing video using AI pipeline..."):
            try:
                # Passes a valid local string path or YouTube URL uniformly
                result = run_pipeline(source, language)
                st.session_state.pipeline_result = result
                st.session_state.chat_history = []
                st.success("Video processed successfully.")
            except Exception as e:
                st.exception(e)

# -----------------------------
# MAIN CONTENT
# -----------------------------
result = st.session_state.pipeline_result

if result:
    transcript = result["transcript"]
    transcript_words = len(transcript.split())
    chunk_estimate = max(1, transcript_words // 250)

    # -----------------------------
    # OVERVIEW CARDS
    # -----------------------------
    st.subheader("📊 Video Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class='metric-card'>
                <h3>📝 Title</h3>
                <p>{result.get('title', 'Local Video Asset')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class='metric-card'>
                <h3>🌐 Language</h3>
                <p>{language.title()}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class='metric-card'>
                <h3>📄 Transcript Words</h3>
                <p>{transcript_words}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class='metric-card'>
                <h3>🧩 Estimated Chunks</h3>
                <p>{chunk_estimate}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------
    # SUMMARY SECTION
    # -----------------------------
    st.subheader("📋 AI Summary")

    st.markdown(
        f"""
        <div class='section-box'>
        {result['summary']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------
    # INSIGHTS SECTION
    # -----------------------------
    st.subheader("🧠 Extracted Insights")

    insight1, insight2, insight3 = st.columns(3)

    with insight1:
        st.markdown(
            f"""
            <div class='section-box'>
            <h3>✅ Action Items</h3>
            <p>{result['action_items']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with insight2:
        st.markdown(
            f"""
            <div class='section-box'>
            <h3>🔑 Key Decisions</h3>
            <p>{result['key_decisions']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with insight3:
        st.markdown(
            f"""
            <div class='section-box'>
            <h3>❓ Open Questions</h3>
            <p>{result['open_questions']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -----------------------------
    # TRANSCRIPT SECTION
    # -----------------------------
    st.subheader("📜 Full Transcript")

    with st.expander("View Transcript"):
        st.text_area(
            "Transcript",
            transcript,
            height=400,
        )

    # -----------------------------
    # RAG CHAT SECTION
    # -----------------------------
    st.subheader("💬 Chat With Your Video")

    # Use unique key or form tracking if chat reruns components
    question = st.chat_input("Ask questions about the video...")

    if question:
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.spinner("Generating response..."):
            answer = ask_question(
                result["rag_chain"],
                question,
            )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

    # Re-render chat logs outside structural execution logic blocks
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(
                f"""
                <div class='chat-user'>
                <b>🧑 You:</b><br><br>
                {chat['content']}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class='chat-ai'>
                <b>🤖 InsightMeet AI:</b><br><br>
                {chat['content']}
                </div>
                """,
                unsafe_allow_html=True,
            )

else:
    st.info("Upload or provide a video configuration file pathway from the sidebar, then execute 'Process Video'.")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption(
    "Built using Python, Streamlit, LangChain, ChromaDB, yt-dlp, FFmpeg, and RAG architecture."
)