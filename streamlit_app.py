# # import os
# # import re
# # from datetime import datetime
# # from pathlib import Path
# # from reportlab.lib.pagesizes import letter
# # from reportlab.pdfgen import canvas
# # import pandas as pd
# # import streamlit as st
# # from pymongo import MongoClient
# # from textwrap import wrap

# # # ------------ Page setup ------------
# # st.set_page_config(
# #     page_title="Admin & Office Facilities Feedback",
# #     page_icon="📝",
# #     layout="centered",
# # )

# # st.title("Admin & Office Facilities Feedback Form")
# # st.caption("Please share your feedback about office facilities, hygiene, ambience and admin support.")

# # # ------------ Constants ------------
# # DATA_PATH = Path("feedback.csv")

# # DB_NAME = "misc"
# # COLL_NAME = "feedback_admin2026"

# # RATING_OPTIONS = [
# #     (1, "1 - Poor"),
# #     (2, "2 - Fair"),
# #     (3, "3 - Good"),
# #     (4, "4 - Very Good"),
# #     (5, "5 - Excellent"),
# # ]

# # QUESTIONS = {
# #     1: "How would you rate the quality and quantity of furniture and office utilities such as tables, chairs, ACs, fans, lights, etc.?",
# #     2: "How would you rate the interior design, ventilation, workspace layout and overall comfort of the office?",
# #     3: "How would you rate the Pantry & its Utillities?",
# #     4: "How would you rate the conference hall & its facilities?",
# #     5: "How would you rate the hygiene, cleanliness and quality of washrooms?",
# #     6: "How would you rate the overall ambience of the office?",
# #     7: "How would you rate the admin's responsibility, responsiveness and support?",
# # }

# # SUMMARY_LABELS = {
# #     "Furniture & Utilities": "q1",
# #     "Interior & Ventilation": "q2",
# #     "Pantry & Utillities": "q3",
# #     "Conference Hall and its Facilities":"q4",
# #     "Washrooms": "q5",
# #     "Office Ambience": "q6",
# #     "Admin Responsibility": "q7",
# #     "Final Overall": "overall",
# # }

# # EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$")


# # # ------------ Sidebar ------------
# # if "mode" not in st.session_state:
# #     st.session_state.mode = "employee"

# # emp_btn = st.sidebar.button("🧑‍💼 Employee Feedback")
# # adm_btn = st.sidebar.button("🛡️ Admin Login / Review")

# # if emp_btn:
# #     st.session_state.mode = "employee"
# # if adm_btn:
# #     st.session_state.mode = "admin"

# # st.sidebar.markdown("---")
# # st.sidebar.write(":bulb: Use the buttons above to switch modes.")


# # # ------------ MongoDB ------------
# # # Recommended priority: Streamlit secrets -> environment variable -> fallback.
# # # Add this in .streamlit/secrets.toml:
# # # mongo_uri = "mongodb+srv://username:password@cluster-url/"
# # try:
# #     mongo_uri = st.secrets["mongo_uri"]
# # except Exception:
# #     mongo_uri = os.getenv(
# #         "MONGO_URI",
# #         "mongodb+srv://Vedsu:CVxB6F2N700cQ0qu@cluster0.thbmwqi.mongodb.net/",
# #     )

# # client = MongoClient(mongo_uri)
# # db = client[DB_NAME]
# # coll = db[COLL_NAME]


# # # ------------ Helpers ------------
# # def starbar(value: int, total: int = 5) -> str:
# #     """Return a string of filled and empty stars."""
# #     value = int(value or 0)
# #     return "★" * value + "☆" * (total - value)


# # def validate(subject: str, name: str, email: str, ratings: list[int | None]) -> list[str]:
# #     errors = []

# #     if not subject.strip():
# #         errors.append("Subject is required.")

# #     if not name.strip():
# #         errors.append("Name is required.")

# #     if not email.strip():
# #         errors.append("Email is required.")
# #     elif not EMAIL_REGEX.match(email.strip()):
# #         errors.append("Please enter a valid email address.")

# #     for idx, rating in enumerate(ratings, start=1):
# #         if rating is None:
# #             errors.append(f"Please select a rating for Q{idx}.")

# #     return errors


# # def draw_wrapped_text(c, text: str, x: int, y: int, width_chars: int = 80, line_gap: int = 15):
# #     """Draw wrapped text and return updated y position."""
# #     for line in wrap(str(text or ""), width=width_chars):
# #         c.drawString(x, y, line)
# #         y -= line_gap
# #     return y


# # def generate_pdf(row: dict, filename: str):
# #     """Generate a PDF for a single feedback response."""
# #     c = canvas.Canvas(filename, pagesize=letter)
# #     width, height = letter

# #     margin = 30
# #     c.setFont("Helvetica", 12)
# #     c.rect(margin, margin, width - 2 * margin, height - 2 * margin)

# #     def check_page_space(current_y):
# #         if current_y < 80:
# #             c.showPage()
# #             c.setFont("Helvetica", 12)
# #             c.rect(margin, margin, width - 2 * margin, height - 2 * margin)
# #             return height - 50
# #         return current_y

# #     y = height - 50

# #     c.setFont("Helvetica-Bold", 14)
# #     c.drawString(50, y, "Admin & Office Facilities Feedback")
# #     y -= 30

# #     c.setFont("Helvetica", 12)
# #     c.drawString(50, y, f"Feedback Submitted: {row.get('timestamp', '')}")
# #     y -= 25

# #     def draw_label_value(label, value):
# #         nonlocal y
# #         y = check_page_space(y)
# #         c.setFont("Helvetica-Bold", 12)
# #         c.drawString(50, y, f"{label}:")
# #         text_width = c.stringWidth(f"{label}:", "Helvetica-Bold", 12)
# #         c.setFont("Helvetica", 12)
# #         c.drawString(55 + text_width, y, str(value or ""))
# #         y -= 20

# #     draw_label_value("Name", row.get("name"))
# #     draw_label_value("Email", row.get("email"))
# #     draw_label_value("Subject", row.get("subject"))

# #     y -= 10
# #     c.setLineWidth(1)
# #     c.line(40, y, width - 40, y)
# #     y -= 30

# #     for i, q_text in QUESTIONS.items():
# #         y = check_page_space(y)

# #         c.setFont("Helvetica-Bold", 12)
# #         y = draw_wrapped_text(c, f"Q{i}. {q_text}", 50, y, width_chars=75, line_gap=15)

# #         c.setFont("Helvetica", 12)
# #         y = check_page_space(y)
# #         rating = row.get(f"q{i}", "")
# #         c.drawString(70, y, f"Rating: {rating} ({starbar(rating) if rating else ''})")
# #         y -= 20

# #         comment = row.get(f"q{i}_comment", "")
# #         y = check_page_space(y)
# #         if comment:
# #             y = draw_wrapped_text(c, f"Comment: {comment}", 70, y, width_chars=80, line_gap=14)
# #         else:
# #             c.drawString(70, y, "Comment: None")
# #             y -= 14

# #         y -= 12

# #     # --- Start Final Overall Rating and Additional Comments on a new page ---
# #     c.showPage()
# #     c.setFont("Helvetica", 12)
# #     c.rect(margin, margin, width - 2 * margin, height - 2 * margin)
# #     y = height - 50

# #     c.setFont("Helvetica-Bold", 14)
# #     c.drawString(50, y, "Final Feedback Summary")
# #     y -= 35

# #     c.setFont("Helvetica-Bold", 12)
# #     c.drawString(50, y, "Final Overall Rating:")
# #     c.setFont("Helvetica", 12)

# #     text_width = c.stringWidth("Final Overall Rating:", "Helvetica-Bold", 12)
# #     c.drawString(55 + text_width, y, f"{row.get('overall')} ({starbar(row.get('overall'))})")
# #     y -= 30

# #     additional_comment = row.get("additional_comment", "")

# #     c.setFont("Helvetica-Bold", 12)
# #     c.drawString(50, y, "Additional Comments:")
# #     y -= 18

# #     c.setFont("Helvetica", 12)

# #     if additional_comment:
# #         y = draw_wrapped_text(c, additional_comment, 70, y, width_chars=80, line_gap=14)
# #     else:
# #         c.drawString(70, y, "None")
# #         y -= 14

# #     y -= 20
# #     y = check_page_space(y)
# #     c.drawString(50, y, "Thank you for your valuable feedback!")

# #     c.save()


# # def generate_feedback_pdf(dataframe: pd.DataFrame, filename: str = "all_feedback.pdf"):
# #     """Generate a multi-page PDF summary for all feedback entries."""
# #     c = canvas.Canvas(filename, pagesize=letter)
# #     width, height = letter
# #     margin = 30

# #     def check_page(y):
# #         if y < 80:
# #             c.showPage()
# #             c.setFont("Helvetica", 12)
# #             c.rect(margin, margin, width - 2 * margin, height - 2 * margin)
# #             return height - 50
# #         return y

# #     c.setFont("Helvetica", 12)
# #     c.rect(margin, margin, width - 2 * margin, height - 2 * margin)

# #     y = height - 50

# #     c.setFont("Helvetica-Bold", 14)
# #     c.drawString(50, y, "Admin & Office Facilities Feedback Summary")
# #     y -= 35

# #     for idx, row in dataframe.iterrows():
# #         y = check_page(y)

# #         c.setFont("Helvetica-Bold", 12)
# #         c.drawString(50, y, f"#{idx + 1} Feedback - {row.get('name', '')}")
# #         y -= 20

# #         fields = [
# #             ("Timestamp", "timestamp"),
# #             ("Email", "email"),
# #             ("Subject", "subject"),
# #             ("Final Overall Rating", "overall"),
# #         ]

# #         for label, field in fields:
# #             y = check_page(y)
# #             c.setFont("Helvetica-Bold", 12)
# #             c.drawString(50, y, f"{label}:")
# #             text_width = c.stringWidth(f"{label}:", "Helvetica-Bold", 12)
# #             c.setFont("Helvetica", 12)
# #             c.drawString(55 + text_width, y, str(row.get(field, "")))
# #             y -= 18

# #         for i, q_text in QUESTIONS.items():
# #             y = check_page(y)
# #             c.setFont("Helvetica-Bold", 11)
# #             y = draw_wrapped_text(c, f"Q{i}. {q_text}", 60, y, width_chars=75, line_gap=13)

# #             c.setFont("Helvetica", 11)
# #             y = check_page(y)
# #             c.drawString(70, y, f"Rating: {row.get(f'q{i}', '')}")
# #             y -= 14

# #             comment = str(row.get(f"q{i}_comment", "") or "")
# #             if comment:
# #                 y = check_page(y)
# #                 y = draw_wrapped_text(c, f"Comment: {comment}", 70, y, width_chars=80, line_gap=12)
# #             y -= 8

# #         additional_comment = str(row.get("additional_comment", "") or "")
# #         y = check_page(y)
# #         c.setFont("Helvetica-Bold", 11)
# #         c.drawString(60, y, "Additional Comments:")
# #         y -= 14

# #         c.setFont("Helvetica", 11)
# #         if additional_comment:
# #             y = draw_wrapped_text(c, additional_comment, 70, y, width_chars=80, line_gap=12)
# #         else:
# #             c.drawString(70, y, "None")
# #             y -= 12

# #         y -= 8
# #         y = check_page(y)
# #         c.setLineWidth(1)
# #         c.line(40, y, width - 40, y)
# #         y -= 25

# #     c.save()


# # # ------------ Employee Feedback Mode ------------
# # if st.session_state.mode == "employee":
# #     st.subheader("Employee Feedback")

# #     with st.form("feedback_form", clear_on_submit=False):
# #         subject = st.text_input("Subject:", "Admin & Office Facilities Feedback 2026")

# #         col1, col2 = st.columns(2)
# #         with col1:
# #             name = st.text_input("Name:")
# #         with col2:
# #             email = st.text_input("Email:")

# #         st.divider()

# #         ratings = {}
# #         comments = {}

# #         for i, question in QUESTIONS.items():
# #             st.subheader(f"Q{i}. {question}")
# #             ratings[i] = st.radio(
# #                 "Select one:",
# #                 RATING_OPTIONS,
# #                 format_func=lambda x: x[1],
# #                 horizontal=True,
# #                 index=None,
# #                 key=f"q{i}",
# #             )
# #             comments[i] = st.text_area("Additional comments:", key=f"q{i}c")

# #         st.divider()

# #         overall = st.slider("Final Overall Rating:", min_value=1, max_value=5, value=1)
# #         additional_comment = st.text_area("Any additional comments or suggestions?", key="additional_comment")

# #         submitted = st.form_submit_button("Submit")

# #     if submitted:
# #         def to_int(opt):
# #             return int(opt[0]) if opt else None

# #         rating_values = [to_int(ratings[i]) for i in QUESTIONS]

# #         errs = validate(subject, name, email, rating_values)
# #         if errs:
# #             for e in errs:
# #                 st.error(e)
# #             st.stop()

# #         row = {
# #             "timestamp": datetime.now().isoformat(timespec="seconds"),
# #             "subject": subject.strip(),
# #             "name": name.strip(),
# #             "email": email.strip().lower(),
# #             "overall": int(overall),
# #             "additional_comment": (additional_comment or "").strip(),
# #         }

# #         for i, rating_value in enumerate(rating_values, start=1):
# #             row[f"q{i}"] = rating_value
# #             row[f"q{i}_comment"] = (comments[i] or "").strip()

# #         try:
# #             coll.insert_one(row)
# #             st.success("Thank you! Your feedback has been recorded in our system.")

# #             pdf_file = f"feedback_{row['timestamp'].replace(':', '-')}.pdf"
# #             generate_pdf(row, pdf_file)

# #             with open(pdf_file, "rb") as f:
# #                 st.download_button(
# #                     label="Download your response (PDF)",
# #                     data=f,
# #                     file_name=pdf_file,
# #                     mime="application/pdf",
# #                 )

# #         except Exception as ex:
# #             st.error(f"Failed to store feedback in MongoDB: {ex}")

# #     st.info("To print this page, use your browser's **Print** option (Ctrl/Shift + P).")


# # # ------------ Admin Mode ------------
# # elif st.session_state.mode == "admin":
# #     st.subheader("Admin Login / Review")

# #     admin_user = "admin"
# #     try:
# #         admin_pass = st.secrets["admin_password"]
# #     except Exception:
# #         admin_pass = os.getenv("ADMIN_PASSWORD", "change_me")

# #     with st.sidebar.form("admin_login"):
# #         u = st.text_input("Username", value="", placeholder="admin")
# #         p = st.text_input("Password", type="password")
# #         ok = st.form_submit_button("Login")

# #     if ok:
# #         if u == admin_user and p == admin_pass:
# #             st.sidebar.success("Authenticated. Loading feedback...")

# #             query = {}
# #             docs = list(coll.find(query).sort("timestamp", -1))

# #             if docs:
# #                 for d in docs:
# #                     d.pop("_id", None)

# #             df = pd.DataFrame(docs)

# #             st.write(f"Total records: **{len(df)}**")

# #             if not df.empty:
# #                 st.dataframe(df, use_container_width=True)

# #                 csv_data = df.to_csv(index=False).encode("utf-8")
# #                 st.download_button(
# #                     "Download CSV",
# #                     data=csv_data,
# #                     file_name="admin_office_feedback.csv",
# #                     mime="text/csv",
# #                 )

# #                 pdf_filename = "all_admin_office_feedback.pdf"
# #                 generate_feedback_pdf(df, pdf_filename)

# #                 with open(pdf_filename, "rb") as f:
# #                     st.download_button(
# #                         "Download PDF",
# #                         data=f,
# #                         file_name=pdf_filename,
# #                         mime="application/pdf",
# #                     )

# #                 st.markdown("### Summary")
# #                 col1, col2 = st.columns(2)

# #                 with col1:
# #                     st.markdown("### Average Ratings")

# #                     avg_ratings = {}
# #                     for label, column in SUMMARY_LABELS.items():
# #                         if column in df.columns:
# #                             avg_ratings[label] = pd.to_numeric(df[column], errors="coerce").mean()

# #                     avg_df = pd.DataFrame.from_dict(
# #                         avg_ratings,
# #                         orient="index",
# #                         columns=["Average Rating"],
# #                     )
# #                     avg_df["Average Rating"] = avg_df["Average Rating"].map(
# #                         lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
# #                     )
# #                     st.table(avg_df)

# #                 with col2:
# #                     st.markdown("### Final Overall Rating Distribution")
# #                     if "overall" in df.columns:
# #                         overall_series = pd.to_numeric(df["overall"], errors="coerce")
# #                         agg = overall_series.groupby(overall_series).size().reindex(range(1, 6), fill_value=0)
# #                         st.bar_chart(agg)
# #                     else:
# #                         st.info("No final overall rating data found.")

# #             else:
# #                 st.info("No feedback found for the current filters.")

# #         else:
# #             st.sidebar.error("Invalid credentials.")
# import os
# import re
# from datetime import datetime

# import pandas as pd
# import streamlit as st
# from pymongo import MongoClient
# from reportlab.lib import colors
# from reportlab.lib.enums import TA_CENTER, TA_LEFT
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
# from reportlab.lib.units import inch
# from reportlab.platypus import (
#     SimpleDocTemplate,
#     Paragraph,
#     Spacer,
#     Table,
#     TableStyle,
#     PageBreak,
# )

# # ------------ Page setup ------------
# st.set_page_config(
#     page_title="Admin & Office Facilities Feedback",
#     page_icon="📝",
#     layout="centered",
# )

# st.title("Admin & Office Facilities Feedback Form")
# st.caption("Please share your feedback about office facilities, hygiene, ambience and admin support.")

# # ------------ Constants ------------
# DB_NAME = "misc"
# COLL_NAME = "feedback_admin2026"

# RATING_OPTIONS = [
#     (1, "1 - Poor"),
#     (2, "2 - Fair"),
#     (3, "3 - Good"),
#     (4, "4 - Very Good"),
#     (5, "5 - Excellent"),
# ]

# QUESTIONS = {
#     1: "How would you rate the quality and quantity of furniture and office utilities such as tables, chairs, ACs, fans, lights, etc.?",
#     2: "How would you rate the interior design, ventilation, workspace layout and overall comfort of the office?",
#     3: "How would you rate the pantry and its utilities?",
#     4: "How would you rate the conference hall and its facilities?",
#     5: "How would you rate the hygiene, cleanliness and quality of washrooms?",
#     6: "How would you rate the overall ambience of the office?",
#     7: "How would you rate the admin team's responsibility, responsiveness and support?",
# }

# SUMMARY_LABELS = {
#     "Furniture & Utilities": "q1",
#     "Interior & Ventilation": "q2",
#     "Pantry & Utilities": "q3",
#     "Conference Hall & Facilities": "q4",
#     "Washrooms": "q5",
#     "Office Ambience": "q6",
#     "Admin Responsibility": "q7",
#     "Final Overall": "overall",
# }

# EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$")

# # ------------ Sidebar ------------
# if "mode" not in st.session_state:
#     st.session_state.mode = "employee"

# if "admin_authenticated" not in st.session_state:
#     st.session_state.admin_authenticated = False

# emp_btn = st.sidebar.button("🧑‍💼 Employee Feedback")
# adm_btn = st.sidebar.button("🛡️ Admin Login / Review")

# if emp_btn:
#     st.session_state.mode = "employee"
# if adm_btn:
#     st.session_state.mode = "admin"

# st.sidebar.markdown("---")
# st.sidebar.write(":bulb: Use the buttons above to switch modes.")

# # ------------ MongoDB ------------
# try:
#     mongo_uri = st.secrets["mongo_uri"]
# except Exception:
#     mongo_uri = os.getenv(
#         "MONGO_URI",
#         "mongodb+srv://Vedsu:CVxB6F2N700cQ0qu@cluster0.thbmwqi.mongodb.net/",
#     )

# client = MongoClient(mongo_uri)
# db = client[DB_NAME]
# coll = db[COLL_NAME]

# # ------------ Helpers ------------
# def starbar(value, total=5):
#     value = int(value or 0)
#     return "★" * value + "☆" * (total - value)


# def to_rating_int(option):
#     return int(option[0]) if option else None


# def format_timestamp(value):
#     return str(value or "").replace("T", " ")


# def validate(subject, name, email, ratings):
#     errors = []

#     if not subject.strip():
#         errors.append("Subject is required.")

#     if not name.strip():
#         errors.append("Name is required.")

#     if not email.strip():
#         errors.append("Email is required.")
#     elif not EMAIL_REGEX.match(email.strip()):
#         errors.append("Please enter a valid email address.")

#     for idx, rating in enumerate(ratings, start=1):
#         if rating is None:
#             errors.append(f"Please select a rating for Q{idx}.")

#     return errors


# def get_pdf_styles():
#     styles = getSampleStyleSheet()

#     styles.add(
#         ParagraphStyle(
#             name="ReportTitle",
#             parent=styles["Title"],
#             fontName="Helvetica-Bold",
#             fontSize=18,
#             leading=22,
#             alignment=TA_CENTER,
#             textColor=colors.HexColor("#243447"),
#             spaceAfter=14,
#         )
#     )

#     styles.add(
#         ParagraphStyle(
#             name="SectionTitle",
#             parent=styles["Heading2"],
#             fontName="Helvetica-Bold",
#             fontSize=13,
#             leading=16,
#             textColor=colors.HexColor("#243447"),
#             spaceBefore=10,
#             spaceAfter=8,
#         )
#     )

#     styles.add(
#         ParagraphStyle(
#             name="QuestionText",
#             parent=styles["Normal"],
#             fontName="Helvetica-Bold",
#             fontSize=10,
#             leading=13,
#             textColor=colors.HexColor("#1F2937"),
#         )
#     )

#     styles.add(
#         ParagraphStyle(
#             name="SmallText",
#             parent=styles["Normal"],
#             fontName="Helvetica",
#             fontSize=9,
#             leading=12,
#             textColor=colors.HexColor("#374151"),
#             alignment=TA_LEFT,
#         )
#     )

#     styles.add(
#         ParagraphStyle(
#             name="FooterText",
#             parent=styles["Normal"],
#             fontName="Helvetica",
#             fontSize=9,
#             leading=11,
#             alignment=TA_CENTER,
#             textColor=colors.HexColor("#6B7280"),
#         )
#     )

#     return styles


# def pdf_page_frame(canvas_obj, doc):
#     canvas_obj.saveState()
#     width, height = letter

#     canvas_obj.setStrokeColor(colors.HexColor("#CBD5E1"))
#     canvas_obj.setLineWidth(1)
#     canvas_obj.rect(0.45 * inch, 0.45 * inch, width - 0.9 * inch, height - 0.9 * inch)

#     canvas_obj.setFillColor(colors.HexColor("#243447"))
#     canvas_obj.rect(0.45 * inch, height - 0.95 * inch, width - 0.9 * inch, 0.5 * inch, fill=1, stroke=0)

#     canvas_obj.setFillColor(colors.white)
#     canvas_obj.setFont("Helvetica-Bold", 10)
#     canvas_obj.drawString(0.65 * inch, height - 0.75 * inch, "Vedsu Admin & Office Facilities Feedback")

#     canvas_obj.setFillColor(colors.HexColor("#6B7280"))
#     canvas_obj.setFont("Helvetica", 8)
#     canvas_obj.drawRightString(width - 0.65 * inch, 0.25 * inch, f"Page {doc.page}")

#     canvas_obj.restoreState()


# def make_key_value_table(rows):
#     table_data = []
#     styles = get_pdf_styles()

#     for label, value in rows:
#         table_data.append([
#             Paragraph(f"<b>{label}</b>", styles["SmallText"]),
#             Paragraph(str(value or ""), styles["SmallText"]),
#         ])

#     table = Table(table_data, colWidths=[1.55 * inch, 4.85 * inch])
#     table.setStyle(
#         TableStyle(
#             [
#                 ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2F7")),
#                 ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
#                 ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
#                 ("VALIGN", (0, 0), (-1, -1), "TOP"),
#                 ("LEFTPADDING", (0, 0), (-1, -1), 8),
#                 ("RIGHTPADDING", (0, 0), (-1, -1), 8),
#                 ("TOPPADDING", (0, 0), (-1, -1), 6),
#                 ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
#             ]
#         )
#     )
#     return table


# def make_question_table(question_no, question, rating, comment):
#     styles = get_pdf_styles()
#     comment_text = comment if comment else "None"

#     table_data = [
#         [
#             Paragraph(f"Q{question_no}. {question}", styles["QuestionText"]),
#         ],
#         [
#             Paragraph(f"<b>Rating:</b> {rating} / 5 &nbsp;&nbsp; {starbar(rating)}", styles["SmallText"]),
#         ],
#         [
#             Paragraph(f"<b>Comment:</b> {comment_text}", styles["SmallText"]),
#         ],
#     ]

#     table = Table(table_data, colWidths=[6.4 * inch])
#     table.setStyle(
#         TableStyle(
#             [
#                 ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF2F7")),
#                 ("BACKGROUND", (0, 1), (-1, -1), colors.white),
#                 ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
#                 ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
#                 ("VALIGN", (0, 0), (-1, -1), "TOP"),
#                 ("LEFTPADDING", (0, 0), (-1, -1), 8),
#                 ("RIGHTPADDING", (0, 0), (-1, -1), 8),
#                 ("TOPPADDING", (0, 0), (-1, -1), 7),
#                 ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
#             ]
#         )
#     )
#     return table


# def generate_pdf(row, filename):
#     """Generate a clean individual response PDF.

#     Final Overall Rating and Additional Comments start on a fresh page.
#     """
#     styles = get_pdf_styles()
#     doc = SimpleDocTemplate(
#         filename,
#         pagesize=letter,
#         rightMargin=0.75 * inch,
#         leftMargin=0.75 * inch,
#         topMargin=1.15 * inch,
#         bottomMargin=0.7 * inch,
#     )

#     story = []
#     story.append(Paragraph("Admin & Office Facilities Feedback", styles["ReportTitle"]))
#     story.append(Paragraph("Individual Feedback Response", styles["FooterText"]))
#     story.append(Spacer(1, 14))

#     story.append(Paragraph("Employee Details", styles["SectionTitle"]))
#     story.append(
#         make_key_value_table(
#             [
#                 ("Submitted On", format_timestamp(row.get("timestamp"))),
#                 ("Name", row.get("name")),
#                 ("Email", row.get("email")),
#                 ("Subject", row.get("subject")),
#             ]
#         )
#     )
#     story.append(Spacer(1, 16))

#     story.append(Paragraph("Category-wise Ratings", styles["SectionTitle"]))

#     for i, question in QUESTIONS.items():
#         story.append(
#             make_question_table(
#                 i,
#                 question,
#                 row.get(f"q{i}", ""),
#                 row.get(f"q{i}_comment", ""),
#             )
#         )
#         story.append(Spacer(1, 9))

#     story.append(PageBreak())

#     story.append(Paragraph("Final Feedback Summary", styles["ReportTitle"]))
#     story.append(Paragraph("Overall rating and additional comments", styles["FooterText"]))
#     story.append(Spacer(1, 18))

#     overall = row.get("overall", "")
#     final_table = Table(
#         [
#             [Paragraph("<b>Final Overall Rating</b>", styles["SmallText"]), Paragraph(f"<b>{overall} / 5</b> &nbsp;&nbsp; {starbar(overall)}", styles["SmallText"])],
#             [Paragraph("<b>Additional Comments</b>", styles["SmallText"]), Paragraph(row.get("additional_comment", "") or "None", styles["SmallText"])],
#         ],
#         colWidths=[2.0 * inch, 4.4 * inch],
#     )
#     final_table.setStyle(
#         TableStyle(
#             [
#                 ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2F7")),
#                 ("BACKGROUND", (1, 0), (1, -1), colors.white),
#                 ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
#                 ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
#                 ("VALIGN", (0, 0), (-1, -1), "TOP"),
#                 ("LEFTPADDING", (0, 0), (-1, -1), 10),
#                 ("RIGHTPADDING", (0, 0), (-1, -1), 10),
#                 ("TOPPADDING", (0, 0), (-1, -1), 10),
#                 ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
#             ]
#         )
#     )

#     story.append(final_table)
#     story.append(Spacer(1, 26))
#     story.append(Paragraph("Thank you for your valuable feedback.", styles["FooterText"]))

#     doc.build(story, onFirstPage=pdf_page_frame, onLaterPages=pdf_page_frame)


# def generate_feedback_pdf(dataframe, filename="all_admin_office_feedback.pdf"):
#     """Generate a clean multi-page admin PDF summary for all feedback entries."""
#     styles = get_pdf_styles()
#     doc = SimpleDocTemplate(
#         filename,
#         pagesize=letter,
#         rightMargin=0.75 * inch,
#         leftMargin=0.75 * inch,
#         topMargin=1.15 * inch,
#         bottomMargin=0.7 * inch,
#     )

#     story = []
#     story.append(Paragraph("Admin & Office Facilities Feedback Summary", styles["ReportTitle"]))
#     story.append(Paragraph("All submitted responses", styles["FooterText"]))
#     story.append(Spacer(1, 14))

#     story.append(Paragraph("Summary", styles["SectionTitle"]))

#     avg_rows = [[Paragraph("<b>Category</b>", styles["SmallText"]), Paragraph("<b>Average Rating</b>", styles["SmallText"])] ]
#     for label, column in SUMMARY_LABELS.items():
#         if column in dataframe.columns:
#             avg = pd.to_numeric(dataframe[column], errors="coerce").mean()
#             avg_text = f"{avg:.2f}" if pd.notna(avg) else "N/A"
#             avg_rows.append([Paragraph(label, styles["SmallText"]), Paragraph(avg_text, styles["SmallText"])])

#     summary_table = Table(avg_rows, colWidths=[4.8 * inch, 1.6 * inch])
#     summary_table.setStyle(
#         TableStyle(
#             [
#                 ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243447")),
#                 ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
#                 ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
#                 ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
#                 ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
#                 ("VALIGN", (0, 0), (-1, -1), "TOP"),
#                 ("LEFTPADDING", (0, 0), (-1, -1), 8),
#                 ("RIGHTPADDING", (0, 0), (-1, -1), 8),
#                 ("TOPPADDING", (0, 0), (-1, -1), 6),
#                 ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
#             ]
#         )
#     )

#     story.append(make_key_value_table([("Total Records", len(dataframe))]))
#     story.append(Spacer(1, 12))
#     story.append(summary_table)
#     story.append(PageBreak())

#     for idx, row in dataframe.iterrows():
#         story.append(Paragraph(f"Response #{idx + 1} - {row.get('name', '')}", styles["SectionTitle"]))
#         story.append(
#             make_key_value_table(
#                 [
#                     ("Submitted On", format_timestamp(row.get("timestamp"))),
#                     ("Email", row.get("email", "")),
#                     ("Subject", row.get("subject", "")),
#                     ("Final Overall Rating", f"{row.get('overall', '')} / 5"),
#                 ]
#             )
#         )
#         story.append(Spacer(1, 10))

#         for i, question in QUESTIONS.items():
#             story.append(
#                 make_question_table(
#                     i,
#                     question,
#                     row.get(f"q{i}", ""),
#                     row.get(f"q{i}_comment", ""),
#                 )
#             )
#             story.append(Spacer(1, 7))

#         story.append(
#             make_key_value_table(
#                 [
#                     ("Additional Comments", row.get("additional_comment", "") or "None"),
#                 ]
#             )
#         )
#         story.append(PageBreak())

#     if story and isinstance(story[-1], PageBreak):
#         story.pop()

#     doc.build(story, onFirstPage=pdf_page_frame, onLaterPages=pdf_page_frame)


# # ------------ Employee Feedback Mode ------------
# if st.session_state.mode == "employee":
#     st.subheader("Employee Feedback")

#     with st.form("feedback_form", clear_on_submit=False):
#         subject = st.text_input("Subject:", "Admin & Office Facilities Feedback 2026")

#         col1, col2 = st.columns(2)
#         with col1:
#             name = st.text_input("Name:")
#         with col2:
#             email = st.text_input("Email:")

#         st.divider()

#         ratings = {}
#         comments = {}

#         for i, question in QUESTIONS.items():
#             st.subheader(f"Q{i}. {question}")
#             ratings[i] = st.radio(
#                 "Select one:",
#                 RATING_OPTIONS,
#                 format_func=lambda x: x[1],
#                 horizontal=True,
#                 index=None,
#                 key=f"q{i}",
#             )
#             comments[i] = st.text_area("Additional comments:", key=f"q{i}c")

#         st.divider()

#         overall = st.slider("Final Overall Rating:", min_value=1, max_value=5, value=1)
#         additional_comment = st.text_area("Any additional comments or suggestions?", key="additional_comment")

#         submitted = st.form_submit_button("Submit")

#     if submitted:
#         rating_values = [to_rating_int(ratings[i]) for i in QUESTIONS]

#         errs = validate(subject, name, email, rating_values)
#         if errs:
#             for e in errs:
#                 st.error(e)
#             st.stop()

#         row = {
#             "timestamp": datetime.now().isoformat(timespec="seconds"),
#             "subject": subject.strip(),
#             "name": name.strip(),
#             "email": email.strip().lower(),
#             "overall": int(overall),
#             "additional_comment": (additional_comment or "").strip(),
#         }

#         for i, rating_value in enumerate(rating_values, start=1):
#             row[f"q{i}"] = rating_value
#             row[f"q{i}_comment"] = (comments[i] or "").strip()

#         try:
#             coll.insert_one(row)
#             st.success("Thank you! Your feedback has been recorded in our system.")

#             pdf_file = f"feedback_{row['timestamp'].replace(':', '-')}.pdf"
#             generate_pdf(row, pdf_file)

#             with open(pdf_file, "rb") as f:
#                 st.download_button(
#                     label="Download your response (PDF)",
#                     data=f,
#                     file_name=pdf_file,
#                     mime="application/pdf",
#                 )

#         except Exception as ex:
#             st.error(f"Failed to store feedback in MongoDB: {ex}")

#     st.info("To print this page, use your browser's **Print** option (Ctrl/Shift + P).")


# # ------------ Admin Mode ------------
# elif st.session_state.mode == "admin":
#     st.subheader("Admin Login / Review")

#     admin_user = "admin"
#     try:
#         admin_pass = st.secrets["admin_password"]
#     except Exception:
#         admin_pass = os.getenv("ADMIN_PASSWORD", "change_me")

#     if not st.session_state.admin_authenticated:
#         with st.sidebar.form("admin_login"):
#             u = st.text_input("Username", value="", placeholder="admin")
#             p = st.text_input("Password", type="password")
#             ok = st.form_submit_button("Login")

#         if ok:
#             if u == admin_user and p == admin_pass:
#                 st.session_state.admin_authenticated = True
#                 st.sidebar.success("Authenticated. Loading feedback...")
#             else:
#                 st.sidebar.error("Invalid credentials.")

#     if st.session_state.admin_authenticated:
#         if st.sidebar.button("Logout"):
#             st.session_state.admin_authenticated = False
#             st.rerun()

#         query = {}
#         docs = list(coll.find(query).sort("timestamp", -1))

#         if docs:
#             for d in docs:
#                 d.pop("_id", None)

#         df = pd.DataFrame(docs)
#         st.write(f"Total records: **{len(df)}**")

#         if not df.empty:
#             preferred_columns = (
#                 ["timestamp", "subject", "name", "email"]
#                 + [f"q{i}" for i in QUESTIONS]
#                 + [f"q{i}_comment" for i in QUESTIONS]
#                 + ["overall", "additional_comment"]
#             )
#             display_columns = [col for col in preferred_columns if col in df.columns]
#             remaining_columns = [col for col in df.columns if col not in display_columns]
#             df = df[display_columns + remaining_columns]

#             st.dataframe(df, use_container_width=True)

#             csv_data = df.to_csv(index=False).encode("utf-8")
#             st.download_button(
#                 "Download CSV",
#                 data=csv_data,
#                 file_name="admin_office_feedback.csv",
#                 mime="text/csv",
#             )

#             pdf_filename = "all_admin_office_feedback.pdf"
#             generate_feedback_pdf(df, pdf_filename)

#             with open(pdf_filename, "rb") as f:
#                 st.download_button(
#                     "Download PDF",
#                     data=f,
#                     file_name=pdf_filename,
#                     mime="application/pdf",
#                 )

#             st.markdown("### Summary")
#             col1, col2 = st.columns(2)

#             with col1:
#                 st.markdown("### Average Ratings")

#                 avg_ratings = {}
#                 for label, column in SUMMARY_LABELS.items():
#                     if column in df.columns:
#                         avg_ratings[label] = pd.to_numeric(df[column], errors="coerce").mean()

#                 avg_df = pd.DataFrame.from_dict(
#                     avg_ratings,
#                     orient="index",
#                     columns=["Average Rating"],
#                 )
#                 avg_df["Average Rating"] = avg_df["Average Rating"].map(
#                     lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
#                 )
#                 st.table(avg_df)

#             with col2:
#                 st.markdown("### Final Overall Rating Distribution")
#                 if "overall" in df.columns:
#                     overall_series = pd.to_numeric(df["overall"], errors="coerce")
#                     agg = overall_series.groupby(overall_series).size().reindex(range(1, 6), fill_value=0)
#                     st.bar_chart(agg)
#                 else:
#                     st.info("No final overall rating data found.")

#         else:
#             st.info("No feedback found for the current filters.")

import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st
from pymongo import MongoClient
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

# ------------ Page setup ------------
st.set_page_config(
    page_title="Admin & Office Facilities Feedback",
    page_icon="📝",
    layout="centered",
)

st.title("Admin & Office Facilities Feedback Form")
st.caption("Please share your feedback about office facilities, hygiene, ambience and admin support.")

# ------------ Constants ------------
DB_NAME = "misc"
COLL_NAME = "feedback_admin2026"

RATING_OPTIONS = [
    (1, "1 - Poor"),
    (2, "2 - Fair"),
    (3, "3 - Good"),
    (4, "4 - Very Good"),
    (5, "5 - Excellent"),
]

# Q1, Q2 and the earlier ambience question have been merged into 2 questions.
# Final structure: 6 questions + final overall rating + additional comments.
QUESTIONS = {
    1: "How would you rate the office infrastructure and utilities, including furniture, chairs, tables, ACs, fans, lights and ventilation?",
    2: "How would you rate the interior design, workspace layout, comfort and overall ambience of the office?",
    3: "How would you rate the pantry and its utilities?",
    4: "How would you rate the conference hall and its facilities?",
    5: "How would you rate the hygiene, cleanliness and quality of washrooms?",
    6: "How would you rate the admin team's responsibility, responsiveness and support?",
}

SUMMARY_LABELS = {
    "Office Infrastructure, Utilities & Ventilation": "q1",
    "Interior, Layout, Comfort & Ambience": "q2",
    "Pantry & Utilities": "q3",
    "Conference Hall & Facilities": "q4",
    "Washrooms": "q5",
    "Admin Responsibility": "q6",
    "Final Overall": "overall",
}

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$")

# ------------ Sidebar ------------
if "mode" not in st.session_state:
    st.session_state.mode = "employee"

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

emp_btn = st.sidebar.button("🧑‍💼 Employee Feedback")
adm_btn = st.sidebar.button("🛡️ Admin Login / Review")

if emp_btn:
    st.session_state.mode = "employee"

if adm_btn:
    st.session_state.mode = "admin"

st.sidebar.markdown("---")
st.sidebar.write(":bulb: Use the buttons above to switch modes.")

# ------------ MongoDB ------------
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
def starbar(value, total=5):
    value = int(value or 0)
    return "★" * value + "☆" * (total - value)


def to_rating_int(option):
    return int(option[0]) if option else None


def format_timestamp(value):
    return str(value or "").replace("T", " ")


def validate(subject, name, email, ratings):
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


# ------------ PDF helpers ------------
def get_pdf_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#243447"),
            spaceAfter=14,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#243447"),
            spaceBefore=10,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="QuestionText",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#1F2937"),
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#374151"),
            alignment=TA_LEFT,
        )
    )

    styles.add(
        ParagraphStyle(
            name="FooterText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#6B7280"),
        )
    )

    return styles


def pdf_page_frame(canvas_obj, doc):
    canvas_obj.saveState()
    width, height = letter

    canvas_obj.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas_obj.setLineWidth(1)
    canvas_obj.rect(0.45 * inch, 0.45 * inch, width - 0.9 * inch, height - 0.9 * inch)

    canvas_obj.setFillColor(colors.HexColor("#243447"))
    canvas_obj.rect(0.45 * inch, height - 0.95 * inch, width - 0.9 * inch, 0.5 * inch, fill=1, stroke=0)

    canvas_obj.setFillColor(colors.white)
    canvas_obj.setFont("Helvetica-Bold", 10)
    canvas_obj.drawString(0.65 * inch, height - 0.75 * inch, "Vedsu Admin & Office Facilities Feedback")

    canvas_obj.setFillColor(colors.HexColor("#6B7280"))
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.drawRightString(width - 0.65 * inch, 0.25 * inch, f"Page {doc.page}")

    canvas_obj.restoreState()


def make_key_value_table(rows):
    table_data = []
    styles = get_pdf_styles()

    for label, value in rows:
        table_data.append(
            [
                Paragraph(f"<b>{label}</b>", styles["SmallText"]),
                Paragraph(str(value or ""), styles["SmallText"]),
            ]
        )

    table = Table(table_data, colWidths=[1.75 * inch, 4.65 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2F7")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def make_question_table(question_no, question, rating, comment):
    styles = get_pdf_styles()
    comment_text = comment if comment else "None"

    table_data = [
        [Paragraph(f"Q{question_no}. {question}", styles["QuestionText"])],
        [Paragraph(f"<b>Rating:</b> {rating} / 5 &nbsp;&nbsp; {starbar(rating)}", styles["SmallText"])],
        [Paragraph(f"<b>Comment:</b> {comment_text}", styles["SmallText"])],
    ]

    table = Table(table_data, colWidths=[6.4 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF2F7")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def generate_pdf(row, filename):
    """Generate a clean individual response PDF.

    Final Overall Rating and Additional Comments start on a fresh page.
    """
    styles = get_pdf_styles()
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=1.15 * inch,
        bottomMargin=0.7 * inch,
    )

    story = []
    story.append(Paragraph("Admin & Office Facilities Feedback", styles["ReportTitle"]))
    story.append(Paragraph("Individual Feedback Response", styles["FooterText"]))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Employee Details", styles["SectionTitle"]))
    story.append(
        make_key_value_table(
            [
                ("Submitted On", format_timestamp(row.get("timestamp"))),
                ("Name", row.get("name")),
                ("Email", row.get("email")),
                ("Subject", row.get("subject")),
            ]
        )
    )
    story.append(Spacer(1, 16))

    story.append(Paragraph("Category-wise Ratings", styles["SectionTitle"]))

    for i, question in QUESTIONS.items():
        story.append(
            make_question_table(
                i,
                question,
                row.get(f"q{i}", ""),
                row.get(f"q{i}_comment", ""),
            )
        )
        story.append(Spacer(1, 9))

    story.append(PageBreak())

    story.append(Paragraph("Final Feedback Summary", styles["ReportTitle"]))
    story.append(Paragraph("Overall rating and additional comments", styles["FooterText"]))
    story.append(Spacer(1, 18))

    overall = row.get("overall", "")
    final_table = Table(
        [
            [
                Paragraph("<b>Final Overall Rating</b>", styles["SmallText"]),
                Paragraph(f"<b>{overall} / 5</b> &nbsp;&nbsp; {starbar(overall)}", styles["SmallText"]),
            ],
            [
                Paragraph("<b>Additional Comments</b>", styles["SmallText"]),
                Paragraph(row.get("additional_comment", "") or "None", styles["SmallText"]),
            ],
        ],
        colWidths=[2.0 * inch, 4.4 * inch],
    )
    final_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2F7")),
                ("BACKGROUND", (1, 0), (1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )

    story.append(final_table)
    story.append(Spacer(1, 26))
    story.append(Paragraph("Thank you for your valuable feedback.", styles["FooterText"]))

    doc.build(story, onFirstPage=pdf_page_frame, onLaterPages=pdf_page_frame)


def generate_feedback_pdf(dataframe, filename="all_admin_office_feedback.pdf"):
    """Generate a clean multi-page admin PDF summary for all feedback entries."""
    styles = get_pdf_styles()
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=1.15 * inch,
        bottomMargin=0.7 * inch,
    )

    story = []
    story.append(Paragraph("Admin & Office Facilities Feedback Summary", styles["ReportTitle"]))
    story.append(Paragraph("All submitted responses", styles["FooterText"]))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Summary", styles["SectionTitle"]))

    avg_rows = [
        [
            Paragraph("<b>Category</b>", styles["SmallText"]),
            Paragraph("<b>Average Rating</b>", styles["SmallText"]),
        ]
    ]

    for label, column in SUMMARY_LABELS.items():
        if column in dataframe.columns:
            avg = pd.to_numeric(dataframe[column], errors="coerce").mean()
            avg_text = f"{avg:.2f}" if pd.notna(avg) else "N/A"
            avg_rows.append([Paragraph(label, styles["SmallText"]), Paragraph(avg_text, styles["SmallText"])])

    summary_table = Table(avg_rows, colWidths=[4.8 * inch, 1.6 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243447")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(make_key_value_table([("Total Records", len(dataframe))]))
    story.append(Spacer(1, 12))
    story.append(summary_table)
    story.append(PageBreak())

    for idx, row in dataframe.iterrows():
        story.append(Paragraph(f"Response #{idx + 1} - {row.get('name', '')}", styles["SectionTitle"]))
        story.append(
            make_key_value_table(
                [
                    ("Submitted On", format_timestamp(row.get("timestamp"))),
                    ("Email", row.get("email", "")),
                    ("Subject", row.get("subject", "")),
                    ("Final Overall Rating", f"{row.get('overall', '')} / 5"),
                ]
            )
        )
        story.append(Spacer(1, 10))

        for i, question in QUESTIONS.items():
            story.append(
                make_question_table(
                    i,
                    question,
                    row.get(f"q{i}", ""),
                    row.get(f"q{i}_comment", ""),
                )
            )
            story.append(Spacer(1, 7))

        story.append(
            make_key_value_table(
                [
                    ("Additional Comments", row.get("additional_comment", "") or "None"),
                ]
            )
        )
        story.append(PageBreak())

    if story and isinstance(story[-1], PageBreak):
        story.pop()

    doc.build(story, onFirstPage=pdf_page_frame, onLaterPages=pdf_page_frame)


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
        rating_values = [to_rating_int(ratings[i]) for i in QUESTIONS]

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

    if not st.session_state.admin_authenticated:
        with st.sidebar.form("admin_login"):
            u = st.text_input("Username", value="", placeholder="admin")
            p = st.text_input("Password", type="password")
            ok = st.form_submit_button("Login")

        if ok:
            if u == admin_user and p == admin_pass:
                st.session_state.admin_authenticated = True
                st.sidebar.success("Authenticated. Loading feedback...")
            else:
                st.sidebar.error("Invalid credentials.")

    if st.session_state.admin_authenticated:
        if st.sidebar.button("Logout"):
            st.session_state.admin_authenticated = False
            st.rerun()

        query = {}
        docs = list(coll.find(query).sort("timestamp", -1))

        if docs:
            for d in docs:
                d.pop("_id", None)

        df = pd.DataFrame(docs)
        st.write(f"Total records: **{len(df)}**")

        if not df.empty:
            preferred_columns = (
                ["timestamp", "subject", "name", "email"]
                + [f"q{i}" for i in QUESTIONS]
                + [f"q{i}_comment" for i in QUESTIONS]
                + ["overall", "additional_comment"]
            )
            display_columns = [col for col in preferred_columns if col in df.columns]
            remaining_columns = [col for col in df.columns if col not in display_columns]
            df = df[display_columns + remaining_columns]

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

