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
st.set_page_config(
    page_title="Admin & Office Facilities Feedback",
    page_icon="📝",
    layout="centered",
)

st.title("Admin & Office Facilities Feedback Form")
st.caption("Please share your feedback about office facilities, hygiene, ambience and admin support.")

# ------------ Constants ------------
DATA_PATH = Path("feedback.csv")

DB_NAME = "misc"
COLL_NAME = "feedback_admin2026"

RATING_OPTIONS = [
    (1, "1 - Poor"),
    (2, "2 - Fair"),
    (3, "3 - Good"),
    (4, "4 - Very Good"),
    (5, "5 - Excellent"),
]

QUESTIONS = {
    1: "How would you rate the quality and quantity of furniture and office utilities such as tables, chairs, ACs, fans, lights, etc.?",
    2: "How would you rate the interior design, ventilation, workspace layout and overall comfort of the office?",
    3: "How would you rate the conference hall facilities, including pantry?",
    4: "How would you rate the hygiene, cleanliness and quality of washrooms?",
    5: "How would you rate the overall ambience of the office?",
    6: "How would you rate the admin's responsibility, responsiveness and support?",
}

SUMMARY_LABELS = {
    "Furniture & Utilities": "q1",
    "Interior & Ventilation": "q2",
    "Pantry & Conference Hall": "q3",
    "Washrooms": "q4",
    "Office Ambience": "q5",
    "Admin Responsibility": "q6",
    "Final Overall": "overall",
}

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$")


# ------------ Sidebar ------------
if "mode" not in st.session_state:
    st.session_state.mode = "employee"

emp_btn = st.sidebar.button("🧑‍💼 Employee Feedback")
adm_btn = st.sidebar.button("🛡️ Admin Login / Review")

if emp_btn:
    st.session_state.mode = "employee"
if adm_btn:
    st.session_state.mode = "admin"

st.sidebar.markdown("---")
st.sidebar.write(":bulb: Use the buttons above to switch modes.")


# ------------ MongoDB ------------
# Recommended priority: Streamlit secrets -> environment variable -> fallback.
# Add this in .streamlit/secrets.toml:
# mongo_uri = "mongodb+srv://username:password@cluster-url/"
try:
    mongo_uri = st.secrets["mongo_uri"]
except Exception:
    mongo_uri = os.getenv(
        "MONGO_URI",
        "mongodb+srv://Vedsu:CVxB6F2N700cQ0qu@cluster0.thbmwqi.mongodb.net/",
    )

client = MongoClient(mongo_uri)
db = client[DB_NAME]
coll = db[COLL_NAME]


# ------------ Helpers ------------
def starbar(value: int, total: int = 5) -> str:
    """Return a string of filled and empty stars."""
    value = int(value or 0)
    return "★" * value + "☆" * (total - value)


def validate(subject: str, name: str, email: str, ratings: list[int | None]) -> list[str]:
    errors = []

    if not subject.strip():
        errors.append("Subject is required.")

    if not name.strip():
        errors.append("Name is required.")

    if not email.strip():
        errors.append("Email is required.")
    elif not EMAIL_REGEX.match(email.strip()):
        errors.append("Please enter a valid email address.")

    for idx, rating in enumerate(ratings, start=1):
        if rating is None:
            errors.append(f"Please select a rating for Q{idx}.")

    return errors


def draw_wrapped_text(c, text: str, x: int, y: int, width_chars: int = 80, line_gap: int = 15):
    """Draw wrapped text and return updated y position."""
    for line in wrap(str(text or ""), width=width_chars):
        c.drawString(x, y, line)
        y -= line_gap
    return y


def generate_pdf(row: dict, filename: str):
    """Generate a PDF for a single feedback response."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    margin = 30
    c.setFont("Helvetica", 12)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin)

    def check_page_space(current_y):
        if current_y < 80:
            c.showPage()
            c.setFont("Helvetica", 12)
            c.rect(margin, margin, width - 2 * margin, height - 2 * margin)
            return height - 50
        return current_y

    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Admin & Office Facilities Feedback")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Feedback Submitted: {row.get('timestamp', '')}")
    y -= 25

    def draw_label_value(label, value):
        nonlocal y
        y = check_page_space(y)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"{label}:")
        text_width = c.stringWidth(f"{label}:", "Helvetica-Bold", 12)
        c.setFont("Helvetica", 12)
        c.drawString(55 + text_width, y, str(value or ""))
        y -= 20

    draw_label_value("Name", row.get("name"))
    draw_label_value("Email", row.get("email"))
    draw_label_value("Subject", row.get("subject"))

    y -= 10
    c.setLineWidth(1)
    c.line(40, y, width - 40, y)
    y -= 30

    for i, q_text in QUESTIONS.items():
        y = check_page_space(y)

        c.setFont("Helvetica-Bold", 12)
        y = draw_wrapped_text(c, f"Q{i}. {q_text}", 50, y, width_chars=75, line_gap=15)

        c.setFont("Helvetica", 12)
        y = check_page_space(y)
        rating = row.get(f"q{i}", "")
        c.drawString(70, y, f"Rating: {rating} ({starbar(rating) if rating else ''})")
        y -= 20

        comment = row.get(f"q{i}_comment", "")
        y = check_page_space(y)
        if comment:
            y = draw_wrapped_text(c, f"Comment: {comment}", 70, y, width_chars=80, line_gap=14)
        else:
            c.drawString(70, y, "Comment: None")
            y -= 14

        y -= 12

    # --- Start Final Overall Rating and Additional Comments on a new page ---
    c.showPage()
    c.setFont("Helvetica", 12)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin)
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Final Feedback Summary")
    y -= 35

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Final Overall Rating:")
    c.setFont("Helvetica", 12)

    text_width = c.stringWidth("Final Overall Rating:", "Helvetica-Bold", 12)
    c.drawString(55 + text_width, y, f"{row.get('overall')} ({starbar(row.get('overall'))})")
    y -= 30

    additional_comment = row.get("additional_comment", "")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Additional Comments:")
    y -= 18

    c.setFont("Helvetica", 12)

    if additional_comment:
        y = draw_wrapped_text(c, additional_comment, 70, y, width_chars=80, line_gap=14)
    else:
        c.drawString(70, y, "None")
        y -= 14

    y -= 20
    y = check_page_space(y)
    c.drawString(50, y, "Thank you for your valuable feedback!")

    c.save()


def generate_feedback_pdf(dataframe: pd.DataFrame, filename: str = "all_feedback.pdf"):
    """Generate a multi-page PDF summary for all feedback entries."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    margin = 30

    def check_page(y):
        if y < 80:
            c.showPage()
            c.setFont("Helvetica", 12)
            c.rect(margin, margin, width - 2 * margin, height - 2 * margin)
            return height - 50
        return y

    c.setFont("Helvetica", 12)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin)

    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Admin & Office Facilities Feedback Summary")
    y -= 35

    for idx, row in dataframe.iterrows():
        y = check_page(y)

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"#{idx + 1} Feedback - {row.get('name', '')}")
        y -= 20

        fields = [
            ("Timestamp", "timestamp"),
            ("Email", "email"),
            ("Subject", "subject"),
            ("Final Overall Rating", "overall"),
        ]

        for label, field in fields:
            y = check_page(y)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"{label}:")
            text_width = c.stringWidth(f"{label}:", "Helvetica-Bold", 12)
            c.setFont("Helvetica", 12)
            c.drawString(55 + text_width, y, str(row.get(field, "")))
            y -= 18

        for i, q_text in QUESTIONS.items():
            y = check_page(y)
            c.setFont("Helvetica-Bold", 11)
            y = draw_wrapped_text(c, f"Q{i}. {q_text}", 60, y, width_chars=75, line_gap=13)

            c.setFont("Helvetica", 11)
            y = check_page(y)
            c.drawString(70, y, f"Rating: {row.get(f'q{i}', '')}")
            y -= 14

            comment = str(row.get(f"q{i}_comment", "") or "")
            if comment:
                y = check_page(y)
                y = draw_wrapped_text(c, f"Comment: {comment}", 70, y, width_chars=80, line_gap=12)
            y -= 8

        additional_comment = str(row.get("additional_comment", "") or "")
        y = check_page(y)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y, "Additional Comments:")
        y -= 14

        c.setFont("Helvetica", 11)
        if additional_comment:
            y = draw_wrapped_text(c, additional_comment, 70, y, width_chars=80, line_gap=12)
        else:
            c.drawString(70, y, "None")
            y -= 12

        y -= 8
        y = check_page(y)
        c.setLineWidth(1)
        c.line(40, y, width - 40, y)
        y -= 25

    c.save()


# ------------ Employee Feedback Mode ------------
if st.session_state.mode == "employee":
    st.subheader("Employee Feedback")

    with st.form("feedback_form", clear_on_submit=False):
        subject = st.text_input("Subject:", "Admin & Office Facilities Feedback 2026")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name:")
        with col2:
            email = st.text_input("Email:")

        st.divider()

        ratings = {}
        comments = {}

        for i, question in QUESTIONS.items():
            st.subheader(f"Q{i}. {question}")
            ratings[i] = st.radio(
                "Select one:",
                RATING_OPTIONS,
                format_func=lambda x: x[1],
                horizontal=True,
                index=None,
                key=f"q{i}",
            )
            comments[i] = st.text_area("Additional comments:", key=f"q{i}c")

        st.divider()

        overall = st.slider("Final Overall Rating:", min_value=1, max_value=5, value=1)
        additional_comment = st.text_area("Any additional comments or suggestions?", key="additional_comment")

        submitted = st.form_submit_button("Submit")

    if submitted:
        def to_int(opt):
            return int(opt[0]) if opt else None

        rating_values = [to_int(ratings[i]) for i in QUESTIONS]

        errs = validate(subject, name, email, rating_values)
        if errs:
            for e in errs:
                st.error(e)
            st.stop()

        row = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "subject": subject.strip(),
            "name": name.strip(),
            "email": email.strip().lower(),
            "overall": int(overall),
            "additional_comment": (additional_comment or "").strip(),
        }

        for i, rating_value in enumerate(rating_values, start=1):
            row[f"q{i}"] = rating_value
            row[f"q{i}_comment"] = (comments[i] or "").strip()

        try:
            coll.insert_one(row)
            st.success("Thank you! Your feedback has been recorded in our system.")

            pdf_file = f"feedback_{row['timestamp'].replace(':', '-')}.pdf"
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

    st.info("To print this page, use your browser's **Print** option (Ctrl/Shift + P).")


# ------------ Admin Mode ------------
elif st.session_state.mode == "admin":
    st.subheader("Admin Login / Review")

    admin_user = "admin"
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
            st.sidebar.success("Authenticated. Loading feedback...")

            query = {}
            docs = list(coll.find(query).sort("timestamp", -1))

            if docs:
                for d in docs:
                    d.pop("_id", None)

            df = pd.DataFrame(docs)

            st.write(f"Total records: **{len(df)}**")

            if not df.empty:
                st.dataframe(df, use_container_width=True)

                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download CSV",
                    data=csv_data,
                    file_name="admin_office_feedback.csv",
                    mime="text/csv",
                )

                pdf_filename = "all_admin_office_feedback.pdf"
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

                with col1:
                    st.markdown("### Average Ratings")

                    avg_ratings = {}
                    for label, column in SUMMARY_LABELS.items():
                        if column in df.columns:
                            avg_ratings[label] = pd.to_numeric(df[column], errors="coerce").mean()

                    avg_df = pd.DataFrame.from_dict(
                        avg_ratings,
                        orient="index",
                        columns=["Average Rating"],
                    )
                    avg_df["Average Rating"] = avg_df["Average Rating"].map(
                        lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
                    )
                    st.table(avg_df)

                with col2:
                    st.markdown("### Final Overall Rating Distribution")
                    if "overall" in df.columns:
                        overall_series = pd.to_numeric(df["overall"], errors="coerce")
                        agg = overall_series.groupby(overall_series).size().reindex(range(1, 6), fill_value=0)
                        st.bar_chart(agg)
                    else:
                        st.info("No final overall rating data found.")

            else:
                st.info("No feedback found for the current filters.")

        else:
            st.sidebar.error("Invalid credentials.")
