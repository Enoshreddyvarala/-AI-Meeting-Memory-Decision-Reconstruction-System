import streamlit as st
import requests
import json
import pandas as pd
from datetime import date

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Meeting Memory & Decision Reconstruction",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI Meeting Memory & Decision Reconstruction System")
st.markdown("Convert meetings into **persistent organizational memory** and reconstruct the reasoning behind past decisions.")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to page:",
    [
        "1. Upload Meeting",
        "2. Meeting Memory",
        "3. Decision Explorer",
        "4. Ask Organizational Memory",
        "5. Decision Timeline"
    ]
)

# Helper function to query backend
def fetch_api(endpoint: str, method: str = "GET", payload: dict = None, files: dict = None, data: dict = None):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            res = requests.get(url, params=payload)
        elif method == "POST":
            if files or data:
                res = requests.post(url, data=data, files=files)
            else:
                res = requests.post(url, json=payload)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API Error ({url}): {e}")
        return None

# Page 1: Upload Meeting
if page == "1. Upload Meeting":
    st.header("📤 Upload Meeting Recording or Transcript")
    st.caption("Upload meeting audio or paste transcript text to generate persistent memory.")
    
    with st.form("upload_form"):
        title = st.text_input("Meeting Title", "Architecture Decision Meeting")
        m_date = st.date_input("Meeting Date", date.today())
        project = st.text_input("Project Name", "AI Platform")
        participants = st.text_input("Participants (comma separated)", "Rahul (Tech Lead), Priya (Backend Lead), Arjun (PM)")
        
        input_type = st.radio("Input Source", ["Text Transcript", "Audio File"])
        
        uploaded_file = None
        transcript_text = ""
        
        if input_type == "Audio File":
            uploaded_file = st.file_uploader("Choose Audio File", type=["mp3", "wav", "m4a", "mp4", "webm"])
        else:
            transcript_text = st.text_area("Paste Meeting Transcript Text", height=200, value="""00:05:00 - Speaker 1: We need to finalize the database.
00:07:30 - Speaker 2: PostgreSQL is selected because we need strong transaction support and relational joins.
00:10:00 - Speaker 1: Agreed. MongoDB is rejected due to lack of relational transaction guarantees.""")
            
        submitted = st.form_submit_button("🚀 Process Meeting Memory")
        
        if submitted:
            with st.spinner("Transcribing, analyzing, extracting decisions & building persistent memory..."):
                form_data = {
                    "title": title,
                    "date": str(m_date),
                    "project": project,
                    "participants": participants,
                }
                if input_type == "Text Transcript":
                    form_data["transcript_text"] = transcript_text
                    res = fetch_api("/meetings/upload", method="POST", data=form_data)
                elif uploaded_file:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    res = fetch_api("/meetings/upload", method="POST", data=form_data, files=files)
                else:
                    st.warning("Please provide transcript text or upload an audio file.")
                    res = None

                if res:
                    st.success(f"Successfully processed meeting: {res.get('title')} (ID: {res.get('meeting_id')})!")
                    st.json(res)

# Page 2: Meeting Memory
elif page == "2. Meeting Memory":
    st.header("📋 Persistent Meeting Memory")
    meetings = fetch_api("/meetings")
    if meetings:
        meeting_options = {f"{m['title']} ({m['date']}) - {m['meeting_id']}": m['meeting_id'] for m in meetings}
        selected_m = st.selectbox("Select Meeting:", list(meeting_options.keys()))
        m_id = meeting_options[selected_m]
        
        if m_id:
            memory = fetch_api(f"/meetings/{m_id}/memory")
            if memory:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.subheader(f"📌 {memory['title']}")
                    st.write(f"**Date:** {memory['date']} | **Project:** {memory['project']}")
                    st.write(f"**Participants:** {', '.join(memory['participants'])}")
                    st.markdown("### Executive Summary")
                    st.info(memory['summary'])
                    
                    st.markdown("### Key Decisions")
                    for d in memory['decisions']:
                        st.success(f"**{d['title']}**: {d['decision']}\n\n*Rationale:* {', '.join(d['rationale'])}\n\n*Alternatives considered:* {', '.join(d['alternatives']) if d['alternatives'] else 'None'}")
                        
                with col2:
                    st.markdown("### Action Items")
                    for a in memory['actions']:
                        st.warning(f"**{a['description']}**\n\nOwner: `{a['owner']}` | Priority: `{a['priority']}`")
                        
                    st.markdown("### Topics")
                    st.write(", ".join([f"`{t}`" for t in memory['topics']]))
                    
                    if memory.get('risks'):
                        st.markdown("### Risks")
                        for r in memory['risks']:
                            st.error(r)

# Page 3: Decision Explorer
elif page == "3. Decision Explorer":
    st.header("🔍 Decision Explorer")
    decisions = fetch_api("/decisions")
    if decisions:
        for d in decisions:
            with st.expander(f"⚖️ {d['title']} — {d['decision']} ({d['status']})", expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.metric("Confidence Score", f"{int(d['confidence'] * 100)}%")
                c2.metric("Meeting ID", d['source_meeting_id'])
                c3.metric("Timestamp", d['timestamp'])
                
                st.write("**Rationale / Why:**")
                for r in d['rationale']:
                    st.write(f"- {r}")
                    
                st.write(f"**Alternatives Considered:** {', '.join(d['alternatives']) if d['alternatives'] else 'None'}")
                st.write(f"**Participants Involved:** {', '.join(d['participants'])}")

# Page 4: Ask Organizational Memory
elif page == "4. Ask Organizational Memory":
    st.header("❓ Ask Organizational Memory (Source-Grounded RAG)")
    
    st.markdown("""
    > Try asking:
    > **"Why did we choose PostgreSQL instead of MongoDB three months ago?"**
    """)
    
    query = st.text_input("Enter your historical question:", value="Why did we choose PostgreSQL instead of MongoDB three months ago?")
    
    if st.button("🔎 Reconstruct Decision Context"):
        with st.spinner("Searching historical vector store, retrieving evidence, and reconstructing decision timeline..."):
            res = fetch_api("/ask", method="POST", payload={"question": query})
            if res:
                st.markdown("### 💬 Reconstructed Answer")
                st.markdown(res.get("answer"))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 🎯 Decision Summary")
                    st.write(f"**Chosen:** `{res.get('decision')}`")
                    st.write("**Reasons:**")
                    for r in res.get("reasons", []):
                        st.write(f"- {r}")
                    st.write(f"**Alternatives:** {', '.join(res.get('alternatives', []))}")
                    st.write(f"**Participants:** {', '.join(res.get('participants', []))}")
                    st.write(f"**Confidence:** {int(res.get('confidence', 0.9) * 100)}%")

                with col2:
                    st.markdown("#### 📌 Supporting Sources")
                    for src in res.get("sources", []):
                        st.info(f"**{src['title']}** ({src['date']}) — Timestamp: `{src['timestamp']}`")
                        
                    st.markdown("#### ⚡ Actions Followed")
                    for act in res.get("actions", []):
                        st.write(f"• {act}")

# Page 5: Decision Timeline
elif page == "5. Decision Timeline":
    st.header("📅 Historical Decision Timeline")
    topic = st.text_input("Filter Timeline by Topic / Term", value="database")
    
    timeline = fetch_api("/decisions/timeline/topic", payload={"topic": topic})
    if timeline:
        df = pd.DataFrame(timeline)
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Visual Chronology")
        for item in timeline:
            st.markdown(f"**{item['date']}** | `{item['event_type']}` — *{item['meeting_title']}*")
            st.caption(item['description'])
            st.markdown("---")
