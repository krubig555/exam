import streamlit as st
import time

# ข้อมูลข้อสอบ
questions = [
    {"q": "Python เป็นภาษาประเภทใด?", "options": ["Compiled", "Interpreted", "Assembly", "Machine"], "ans": "Interpreted"},
    {"q": "2 + 2 * 2 เท่ากับเท่าไหร่?", "options": ["8", "6", "4", "2"], "ans": "6"},
    # เพิ่มข้อสอบให้ครบ 10 ข้อที่นี่
]

def main():
    st.title("ระบบทำข้อสอบออนไลน์ (30 วินาทีต่อข้อ)")

    # เก็บสถานะต่างๆ ไว้ใน session_state
    if 'current_q' not in st.session_state:
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.start_time = time.time()

    if st.session_state.current_q < len(questions):
        q_idx = st.session_state.current_q
        q_data = questions[q_idx]

        # คำนวณเวลาที่เหลือ
        elapsed_time = time.time() - st.session_state.start_time
        remaining_time = max(0, 30 - int(elapsed_time))

        # แสดงแถบความคืบหน้าของเวลา
        st.progress(remaining_time / 30)
        st.write(f"⏳ เวลาที่เหลือ: {remaining_time} วินาที")

        # แสดงโจทย์
        st.subheader(f"ข้อที่ {q_idx + 1}: {q_data['q']}")
        choice = st.radio("เลือกคำตอบ:", q_data['options'], key=f"q_{q_idx}")

        if st.button("ส่งคำตอบ") or remaining_time == 0:
            if remaining_time == 0:
                st.warning("หมดเวลาสำหรับข้อนี้!")
            elif choice == q_data['ans']:
                st.success("ถูกต้อง!")
                st.session_state.score += 1
            else:
                st.error(f"ผิด! คำตอบที่ถูกคือ {q_data['ans']}")
            
            # ไปข้อถัดไป
            time.sleep(1) # ให้คนดูเฉลยแป๊บหนึ่ง
            st.session_state.current_q += 1
            st.session_state.start_time = time.time()
            st.rerun()

        # สั่งให้หน้าเว็บ Refresh ทุก 1 วินาทีเพื่ออัปเดตตัวเลขเวลา
        if remaining_time > 0:
            time.sleep(1)
            st.rerun()
    else:
        st.balloons()
        st.header("จบการทำข้อสอบ!")
        st.write(f"คะแนนของคุณคือ: {st.session_state.score} / {len(questions)}")
        if st.button("เริ่มใหม่"):
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.rerun()

if __name__ == "__main__":
    main()