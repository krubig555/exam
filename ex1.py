import streamlit as st
import pandas as pd
import os
import time
from io import BytesIO

# --- การตั้งค่าเบื้องต้น ---
EXCEL_FILE = "exam_data.xlsx"
TIME_LIMIT = 30 

st.set_page_config(page_title="ระบบสอบออนไลน์ Cloud Version", layout="centered")

# --- ฟังก์ชันจัดการข้อมูล ---
def load_data():
    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE)
            cols_to_fix = ["question", "option_a", "option_b", "option_c", "option_d", "answer", "image_url"]
            for col in cols_to_fix:
                if col in df.columns:
                    df[col] = df[col].astype(str).replace('nan', '')
            if "id" in df.columns:
                df["id"] = pd.to_numeric(df["id"], errors='coerce').fillna(0).astype(int)
            return df
        except:
            return pd.DataFrame()
    else:
        # สร้างไฟล์ตัวอย่างถ้าไม่มีไฟล์เลย
        df = pd.DataFrame(columns=["id", "question", "option_a", "option_b", "option_c", "option_d", "answer", "image_url"])
        sample = {"id": [1], "question": ["1+1=?"], "option_a": ["1"], "option_b": ["2"], "option_c": ["3"], "option_d": ["4"], "answer": ["ข"], "image_url": [""]}
        df = pd.concat([df, pd.DataFrame(sample)], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        return df

def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- เริ่มต้นโปรแกรม ---
df = load_data()
num_questions = len(df)

if 'exam_started' not in st.session_state:
    st.session_state.exam_started = False
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

# --- Sidebar ---
with st.sidebar:
    st.title("🛡️ แผงควบคุม")
    admin_password = st.text_input("รหัสผ่าน Admin", type="password")
    is_admin = (admin_password == "1234")
    app_mode = st.radio("เมนู", ["🛠️ จัดการข้อสอบ", "📝 ทำข้อสอบ"]) if is_admin else "📝 ทำข้อสอบ"

# --- 1. หน้าจัดการข้อสอบ (Admin) ---
if is_admin and app_mode == "🛠️ จัดการข้อสอบ":
    st.title("🛠️ จัดการข้อสอบ (Excel Cloud)")
    
    # ส่วนที่ 1: Download/Upload (ป้องกันข้อมูลหายบน Cloud)
    col_dl, col_ul = st.columns(2)
    with col_dl:
        st.subheader("1. นำข้อมูลออก")
        excel_data = to_excel_bytes(df)
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name="exam_data_backup.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.caption("โหลดไปแก้ในเครื่องได้เลย")

    with col_ul:
        st.subheader("2. นำข้อมูลเข้า")
        uploaded_file = st.file_uploader("อัปโหลดไฟล์ Excel ใหม่", type=["xlsx"])
        if uploaded_file:
            new_df = pd.read_excel(uploaded_file)
            new_df.to_excel(EXCEL_FILE, index=False)
            st.success("อัปโหลดและอัปเดตข้อสอบแล้ว!")
            time.sleep(1)
            st.rerun()

    st.divider()
    st.subheader("3. แก้ไขด่วนผ่านหน้าเว็บ")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True,
        column_config={
            "answer": st.column_config.SelectboxColumn("เฉลย", options=["ก", "ข", "ค", "ง"], required=True),
            "image_url": st.column_config.TextColumn("ลิงก์รูปภาพ")
        }
    )
    if st.button("💾 บันทึกการแก้ไขบนเว็บ"):
        edited_df.to_excel(EXCEL_FILE, index=False)
        st.success("บันทึกแล้ว!")
        st.rerun()

# --- 2. หน้าทำข้อสอบ (เหมือนเดิม) ---
else:
    if not st.session_state.exam_started:
        st.title("🏆 ระบบสอบออนไลน์")
        st.info(f"จำนวน {num_questions} ข้อ | เวลาข้อละ {TIME_LIMIT} วินาที")
        if st.button("🚀 เริ่มทำข้อสอบ", use_container_width=True):
            st.session_state.exam_started = True
            st.session_state.start_time = time.time()
            st.rerun()
    else:
        # โค้ดทำข้อสอบทีละข้อพร้อม Timer (จากเวอร์ชันก่อนหน้า)
        row = df.iloc[st.session_state.current_idx]
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, int(TIME_LIMIT - elapsed))

        col1, col2 = st.columns([4, 1])
        with col1: st.subheader(f"ข้อที่ {st.session_state.current_idx + 1} / {num_questions}")
        with col2: st.metric("⏳ เวลา", f"{remaining}s")

        st.write(f"#### {row['question']}")
        if pd.notna(row['image_url']) and str(row['image_url']).strip() != "":
            st.image(row['image_url'], width=400)

        options = {f"ก. {row['option_a']}": "ก", f"ข. {row['option_b']}": "ข", f"ค. {row['option_c']}": "ค", f"ง. {row['option_d']}": "ง"}
        current_val = st.session_state.user_answers.get(st.session_state.current_idx, None)
        def_idx = list(options.values()).index(current_val) if current_val in options.values() else None

        ans_choice = st.radio("เลือกคำตอบ:", list(options.keys()), index=def_idx, key=f"q_{st.session_state.current_idx}")
        if ans_choice: st.session_state.user_answers[st.session_state.current_idx] = options[ans_choice]

        st.divider()
        # ปุ่มควบคุม Next/Back และจบการสอบ
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.session_state.current_idx > 0:
                if st.button("⬅️ ย้อนกลับ"):
                    st.session_state.current_idx -= 1
                    st.session_state.start_time = time.time()
                    st.rerun()
        with c3:
            if st.session_state.current_idx < num_questions - 1:
                if st.button("ถัดไป ➡️"):
                    st.session_state.current_idx += 1
                    st.session_state.start_time = time.time()
                    st.rerun()
            else:
                if st.button("🏁 ส่งข้อสอบ", type="primary"):
                    st.session_state.exam_started = False
                    score = sum(1 for i, r in df.iterrows() if st.session_state.user_answers.get(i) == r['answer'])
                    st.balloons()
                    st.success(f"คะแนนของคุณคือ {score} / {num_questions}")

        if remaining > 0:
            time.sleep(1)
            st.rerun()