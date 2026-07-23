import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os

# --- पेज सेटिंग ---
st.set_page_config(page_title="NEET 2028 Bot Dashboard", page_icon="🤖", layout="wide")
st.title("🚀 NEET 2028: AI Question Bot Admin Panel")

# --- Supabase कनेक्शन ---
@st.cache_resource
def init_connection():
    # डॅशबोर्डसाठी Streamlit च्या Secrets मधून keys घेतल्या जातात
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- डेटा आणणे ---
try:
    # एकूण प्रश्नांचा डेटा
    response = supabase.table("NEET QUESTION BANK").select("Subject, Chapter").execute()
    df = pd.DataFrame(response.data)
    
    # कंट्रोल सेटिंग्स
    control_res = supabase.table("bot_control").select("*").eq("id", 1).execute()
    current_mode = control_res.data[0]['mode']
    current_manual_chapter = control_res.data[0]['manual_chapter']
except Exception as e:
    st.error(f"डेटाबेसशी कनेक्ट करताना एरर: {e}")
    st.stop()

# --- डॅशबोर्ड लेआऊट: २ कॉलम्स ---
col1, col2 = st.columns([2, 1])

with col2:
    st.header("⚙️ Bot Control")
    st.info("इथून तुम्ही बॉटला काय करायचे ते सांगू शकता.")
    
    # सर्व चॅप्टर्सची लिस्ट (ड्रॉपडाऊनसाठी)
    if not df.empty:
        all_chapters = sorted(df['Chapter'].unique().tolist())
    else:
        all_chapters = ["Cell Cycle and Cell Division", "Human Reproduction", "Kinematics"] # Default if empty
    
    # मोड निवडणे
    new_mode = st.radio("Bot Mode:", ['Auto', 'Manual'], index=0 if current_mode == 'Auto' else 1)
    
    # चॅप्टर निवडणे (फक्त मॅन्युअल मोडसाठी)
    new_chapter = "None"
    if new_mode == 'Manual':
        new_chapter = st.selectbox("पुढचा चॅप्टर निवडा:", all_chapters, index=all_chapters.index(current_manual_chapter) if current_manual_chapter in all_chapters else 0)
    
    # सेव्ह बटण
    if st.button("Save Settings"):
        supabase.table("bot_control").update({"mode": new_mode, "manual_chapter": new_chapter}).eq("id", 1).execute()
        st.success("✅ सेटिंग्स सेव्ह झाल्या! बॉट पुढच्या वेळी याच सेटिंग्स वापरेल.")

with col1:
    st.header("📊 Progress Report")
    
    if not df.empty:
        st.metric(label="एकूण तयार झालेले प्रश्न", value=len(df))
        
        # चॅप्टरनुसार प्रगतीचा चार्ट
        st.subheader("Chapter-wise Question Count")
        chapter_counts = df['Chapter'].value_counts().reset_index()
        chapter_counts.columns = ['Chapter', 'Questions Generated']
        st.bar_chart(chapter_counts.set_index('Chapter'))
        
        # विषयानुसार प्रगती
        st.subheader("Subject-wise Distribution")
        subject_counts = df['Subject'].value_counts().reset_index()
        subject_counts.columns = ['Subject', 'Count']
        st.dataframe(subject_counts, use_container_width=True)
    else:
        st.warning("अजून कोणतेही प्रश्न जनरेट झालेले नाहीत.")
