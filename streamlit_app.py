import os
import re
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import streamlit as st
from pymongo import MongoClient
from textwrap import wrap

# ------------ Page setup ------------
st.set_page_config(page_title="Feedback Form", page_icon="📝", layout="centered")
st.title("Feedback Form for Employee")
st.caption("A simple feedback form / rating page inspired by the Diwali Party!")

# ------------ Helpers ------------
DATA_PATH = Path("feedback.csv")

RATING_OPTIONS = [
    (1, "1 - Poor"),
    (2, "2 - Fair"),
    (3, "3 - Good"),
    (4, "4 - Very Good"),
    (5, "5 - Excellent"),
]

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$")
# ---------------- Sidebar (two buttons) ----------------
if "mode" not in st.session_state:
    st.session_state.mode = "employee" # default


emp_btn = st.sidebar.button("🧑‍💼 Employee Feedback")
adm_btn = st.sidebar.button("🛡️ Admin Login / Review")
if emp_btn:
    st.session_state.mode = "employee"
if adm_btn:
    st.session_state.mode = "admin"


st.sidebar.markdown("---")
st.sidebar.write(":bulb: Use the buttons above to switch modes.")

# ---------------- MongoDB ----------------
# Connection order of precedence: st.secrets -> ENV -> localhost
mongo_uri = "mongodb+srv://Vedsu:CVxB6F2N700cQ0qu@cluster0.thbmwqi.mongodb.net/"



client = MongoClient(mongo_uri)
DB_NAME = "misc"
COLL_NAME = "feedback_diwali2025"
db = client[DB_NAME]
coll = db[COLL_NAME]
# ---------------- Helpers ----------------
def starbar(value: int, total: int = 5) -> str:
    """Return a string of filled and empty stars."""
    value = int(value or 0)
    return "★" * value + "☆" * (total - value)


def validate(subject: str, name: str, email: str) -> list[str]:
    errors = []
    if not subject.strip():
        errors.append("Subject is required.")
    if not name.strip():
        errors.append("Name is required.")
    if not email.strip():
        errors.append("Email is required.")
    elif not EMAIL_REGEX.match(email.strip()):
        errors.append("Please enter a valid email address.")
    return errors

def generate_pdf(row: dict, filename: str):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)
    # --- Draw a neat page border ---
    margin = 30
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin)

    # Helper function for automatic page breaking
    def check_page_space(current_y, decrement=0):
        """If near bottom margin, start a new page and redraw border."""
        if current_y < 80:
            c.showPage()
            c.setFont("Helvetica", 12)
            c.rect(margin, margin, width - 2 * margin, height - 2 * margin)
            return height - 50  # reset y for new page
        return current_y - decrement

    y = height - 50
    c.drawString(50, y, f"Feedback Submitted: {row.get('timestamp')}")
    y = check_page_space(y, 30)
    
     # --- Bold labels only ---
    def draw_label_value(label, value):
        nonlocal y
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"{label}:")
        text_width = c.stringWidth(f"{label}:", "Helvetica-Bold", 12)
        c.setFont("Helvetica", 12)
        c.drawString(55 + text_width, y, str(value or ""))
        y = check_page_space(y, 20)

    draw_label_value("Name", row.get("name"))
    draw_label_value("Email", row.get("email"))
    draw_label_value("Subject", row.get("subject"))


    
    # --- Add a horizontal line just after Subject ---
    y -= 10
    c.setLineWidth(1)
    c.line(40, y, width - 40, y)
    y -= 30

    # --- Questions Q1–Q6 ---
    for i in range(1, 7):
        if i ==1:
            q_text = "How would you rate the venue of Diwali Party?"
        elif i==2: 
            q_text = "How would you rate enjoyment in pool?"
        elif i==3:
            q_text = "How would you rate decoration and Puja on Diwali at Office?"
        elif i==4:
            q_text = "How would you rate the food on Diwali Party?"
        elif i==5:
            q_text = "How would you rate the initiative on Pick up and drop facility?"
        elif i==6:
            q_text = "How would you rate the Diwali Gifts?"
        
        

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Q{i} - {q_text}")
        c.setFont("Helvetica", 12)
        y = check_page_space(y, 20)

        c.drawString(70, y, f"Rating: {row.get(f'q{i}', '')}")
        y = check_page_space(y, 20)

        comment = row.get(f"q{i}_comment", "")
        if comment:
            wrapped = wrap(f"Comment: {comment}", width=80)
            for line in wrapped:
                c.drawString(70, y, line)
                y = check_page_space(y, 15)
        else:
            c.drawString(70, y, "Comment: None")
            y = check_page_space(y, 15)

        y = check_page_space(y, 10)

    # --- Line before Overall Rating ---
    c.setLineWidth(1)
    c.line(40, y, width - 40, y)
    y = check_page_space(y, 20)

    # --- Overall Rating ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Overall Rating:")
    c.setFont("Helvetica", 12)
    text_width = c.stringWidth("Overall Rating:", "Helvetica-Bold", 12)
    c.drawString(55 + text_width, y, f"{row.get('overall')} ({starbar(row.get('overall'))})")
    y = check_page_space(y, 40)

    c.drawString(50, y, "Thank you for your valuable feedback!")
    c.save()


def generate_feedback_pdf(dataframe, filename="all_feedback.pdf"):
    """Generate a multi-page PDF summary for all feedback entries."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    margin = 30
    c.setFont("Helvetica", 12)

    def check_page(y):
        """Automatically move to next page when out of space."""
        if y < 80:
            c.showPage()
            c.setFont("Helvetica", 12)
            c.rect(margin, margin, width - 2 * margin, height - 2 * margin)
            return height - 50
        return y

    c.rect(margin, margin, width - 2 * margin, height - 2 * margin)
    y = height - 50

    for idx, row in dataframe.iterrows():
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"#{idx + 1} Feedback - {row.get('name', '')}")
        y -= 20
        c.setFont("Helvetica", 12)

        fields = ["timestamp", "email", "subject", "overall"]
        for f in fields:
            label = f.capitalize()
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"{label}:")
            text_width = c.stringWidth(f"{label}:", "Helvetica-Bold", 12)
            c.setFont("Helvetica", 12)
            c.drawString(55 + text_width, y, str(row.get(f, '')))
            y -= 20
            y = check_page(y)

        for i in range(1, 7):
            if f"q{i}" in row:
                q = f"Q{i}: Rating - {row.get(f'q{i}', '')}"
                c.drawString(60, y, q)
                y -= 15
                comment = str(row.get(f"q{i}_comment", "") or "")
                if comment:
                    wrapped = wrap(f"Comment: {comment}", width=80)
                    for line in wrapped:
                        c.drawString(70, y, line)
                        y -= 12
                        y = check_page(y)
                y -= 8
                y = check_page(y)

        c.setLineWidth(1)
        c.line(40, y, width - 40, y)
        y -= 20
        y = check_page(y)

    c.save()
# ---------------- Employee Feedback Mode ----------------
if st.session_state.mode == "employee":
    st.subheader("Employee Feedback")
    with st.form("feedback_form", clear_on_submit=False):
        subject = st.text_input("Subject:", "Diwali Celebration Feedback")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name:")
        with col2:
            email = st.text_input("Email:")

        st.divider()

        st.subheader("Q1. How would you rate the venue of Diwali Party?")
        q1 = st.radio("Select one:", RATING_OPTIONS, format_func=lambda x: x[1], horizontal=True, index=None, key="q1")
        q1_comment = st.text_area("Additional comments:", key="q1c")

        st.subheader("Q2. How would you rate enjoyment in pool?")
        q2 = st.radio("Select one:", RATING_OPTIONS, format_func=lambda x: x[1], horizontal=True, index=None, key="q2")
        q2_comment = st.text_area("Additional comments:", key="q2c")

        st.subheader("Q3. How would you rate decoration and Puja on Diwali at Office?")
        q3 = st.radio("Select one:", RATING_OPTIONS, format_func=lambda x: x[1], horizontal=True, index=None, key="q3")
        q3_comment = st.text_area("Additional comments:", key="q3c")

        st.subheader("Q4. How would you rate the food on Diwali Party?")
        q4 = st.radio("Select one:", RATING_OPTIONS, format_func=lambda x: x[1], horizontal=True, index=None, key="q4")
        q4_comment = st.text_area("Additional comments:", key="q4c")

        
        st.subheader("Q5. How would you rate the initiative on Pick up and drop facility?")
        q5 = st.radio("Select one:", RATING_OPTIONS, format_func=lambda x: x[1], horizontal=True, index=None, key="q5")
        q5_comment = st.text_area("Additional comments:", key="q5c")

        st.subheader("Q6. How would you rate the Diwali Gifts?")
        q6 = st.radio("Select one:", RATING_OPTIONS, format_func=lambda x: x[1], horizontal=True, index=None, key="q6")
        q6_comment = st.text_area("Additional comments:", key="q6c")
        
        st.divider()

        overall = st.slider("Overall Rating:", min_value=1, max_value=5, value=3)
        st.markdown(f"**Your stars:** {starbar(overall)}")

        submitted = st.form_submit_button("Submit")

    # ------------ Handle submit ------------
    if submitted:
        # Unpack selected options (radio returns tuple or None)
        def to_int(opt):
            return int(opt[0]) if opt else None

        q1v, q2v, q3v, q4v, q5v, q6v = map(to_int, (q1, q2, q3, q4, q5, q6))

        errs = validate(subject, name, email)
        if errs:
            for e in errs:
                st.error(e)
            st.stop()

        row = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "subject": subject.strip(),
            "name": name.strip(),
            "email": email.strip().lower(),
            "q1": q1v,
            "q1_comment": (q1_comment or "").strip(),
            "q2": q2v,
            "q2_comment": (q2_comment or "").strip(),
            "q3": q3v,
            "q3_comment": (q3_comment or "").strip(),
            "q4": q4v,
            "q4_comment": (q4_comment or "").strip(),
            "q5": q5v,
            "q5_comment": (q5_comment or "").strip(),
            "q6": q6v,
            "q6_comment": (q6_comment or "").strip(),
            "overall": int(overall),
        }

        try:
            coll.insert_one(row)
            st.success("Thank you! Your feedback has been recorded in our system.")
            # Generate PDF download
            pdf_file = f"feedback_{row['timestamp'].replace(':','-')}.pdf"
            generate_pdf(row, pdf_file)
            with open(pdf_file, "rb") as f:
                st.download_button(
                label="Download your response (PDF)",
                data=f,
                file_name=pdf_file,
                mime="application/pdf",
                )
        except Exception as ex:
            st.error(f"Failed to store feedback in MongoDB: {ex}")

    # ------------ Utility: Print hint ------------
    st.info("To print this page, use your browser's **Print** option (Ctrl/Shift + P).")

#---------------- Admin Mode ----------------
elif st.session_state.mode == "admin":
    st.subheader("Admin Login / Review")


    # Credentials from secrets or env
    admin_user = "admin"
    admin_pass = "feedback2025"
    try:
        admin_pass = st.secrets["admin_password"]
    except Exception:
        admin_pass = os.getenv("ADMIN_PASSWORD", "change_me")


    with st.sidebar.form("admin_login"):
        u = st.text_input("Username", value="", placeholder="admin")
        p = st.text_input("Password", type="password")
        ok = st.form_submit_button("Login")


    if ok:
        if u == admin_user and p == admin_pass:
            st.sidebar.success("Authenticated. Loading feedback…")


       


        # Build query
        query = {}
        


        # Fetch
        docs = list(coll.find(query).sort("timestamp", -1))
        if docs:
            for d in docs:
                d.pop("_id", None)
        df = pd.DataFrame(docs)


        st.write(f"Total records: **{len(df)}**")
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            # Download all as CSV
            dl = df.to_csv(index=False).encode("utf-8")
            # Download as PDF
            pdf_filename = "all_feedback.pdf"
            generate_feedback_pdf(df, pdf_filename)
            with open(pdf_filename, "rb") as f:
                st.download_button(
                    "Download PDF",
                    data=f,
                    file_name=pdf_filename,
                    mime="application/pdf",
                )

            st.markdown("### Summary")
            col1, col2 = st.columns(2)
            # Quick aggregates
            with col1:
                st.markdown("### Average Ratings")
                avg_ratings = {
                    "Venue": df["q1"].mean(),
                    "Pool Enjoyment": df["q2"].mean(),
                    "Decoration & Puja": df["q3"].mean(),
                    "Food": df["q4"].mean(),
                    "Pickup & Drop": df["q5"].mean(),
                    "Gifts": df["q6"].mean(),
                    "Overall": df["overall"].mean(),
                }
                avg_df = pd.DataFrame.from_dict(avg_ratings, orient="index", columns=["Average Rating"])
                avg_df["Average Rating"] = avg_df["Average Rating"].map(lambda x: f"{x:.2f}")
                st.table(avg_df)
            
            with col2:
                st.markdown("### Overall Rating Distribution")
                agg = df.groupby("overall").size().reindex(range(1,6), fill_value=0)
                st.bar_chart(agg)


        else:
            st.info("No feedback found for the current filters.")
    else:
        st.sidebar.error("Invalid credentials.")