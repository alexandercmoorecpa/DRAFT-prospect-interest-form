import streamlit as st
from datetime import date
from io import BytesIO
from fpdf import FPDF

def create_summary_pdf(summary_text, today):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Prospective Client Interest Summary", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, f"""
Date: {today}

This is a preliminary summary from the initial interest form.

Summary of responses:
{summary_text}

Note: This is not a formal engagement or signed document.
No sensitive or identifying information was collected.

Next steps will be discussed after review.
""")

    # Fixed output method
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_output = BytesIO(pdf_bytes)
    pdf_output.seek(0)
    return pdf_output


st.set_page_config(page_title="Initial Interest Form", layout="wide")

st.title("CPA Services – Initial Interest Form")
st.markdown("""
This short, no-commitment form helps me understand a bit about your situation  
so I can prepare for a useful conversation.  

No names, dates, account numbers, or personal details are requested.  
Use it to tell me what you're thinking about — we'll explore from there.
""")

if "step" not in st.session_state:
    st.session_state.step = 1
if "responses" not in st.session_state:
    st.session_state.responses = {}

if st.session_state.step == 1:
    st.subheader("Step 1: General Situation")

    with st.form("step1"):
        situation = st.selectbox(
            "Which best describes why you're reaching out?",
            [
                "Looking for help with personal or family taxes",
                "Need guidance on business or self-employment taxes",
                "Exploring tax planning or year-end strategies",
                "Dealing with a recent life event that may affect taxes (for myself or a family member)",
                "Other / just exploring CPA services",
                "Not sure yet – want to discuss options"
            ]
        )

        timeline = st.radio(
            "How soon are you hoping to get started or get answers?",
            ["Immediately / within the next 30 days",
             "Within the next 3–6 months",
             "No firm timeline yet – gathering information",
             "Just researching for future reference"]
        )

        complexity = st.slider(
            "How complicated do you think your tax situation might be?",
            min_value=1, max_value=5, value=3, step=1,
            format="Level %d",
            help="1 = Very straightforward\n5 = Quite involved / multiple factors"
        )

        submitted = st.form_submit_button("Continue →")

    if submitted:
        st.session_state.responses.update({
            "situation": situation,
            "timeline": timeline,
            "complexity": complexity
        })
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.subheader("Step 2: A Few More Details")

    with st.form("step2"):
        main_concern = st.text_area(
            "What is your biggest question or concern right now? (optional)",
            height=100,
            placeholder="Examples: deadlines, deductions, planning ahead, estimated costs, what services you offer..."
        )

        contact_pref = st.selectbox(
            "Preferred way to discuss next steps",
            ["Email", "Phone call", "Video call (Zoom/Teams)", "No preference"]
        )

        email = st.text_input(
            "Email address (optional – only if you'd like me to follow up)",
            placeholder="your.email@example.com"
        )

        phone = st.text_input(
            "Phone number (optional – only if you'd like me to follow up)",
            placeholder="(XXX) XXX-XXXX"
        )

        interest_confirm = st.checkbox(
            "**I understand this is a preliminary form only.**  \n"
            "I am interested in learning more about your CPA services.",
            help="Checking this helps prioritize follow-up."
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("← Back"):
                st.session_state.step = 1
                st.rerun()
        with col2:
            submit_final = st.form_submit_button("Review & Generate Summary", type="primary")

    if submit_final:
        if not interest_confirm:
            st.warning("Please confirm interest to continue.")
        else:
            st.session_state.responses.update({
                "main_concern": main_concern,
                "contact_pref": contact_pref,
                "email": email.strip() if email.strip() else None,
                "phone": phone.strip() if phone.strip() else None,
                "interest_confirm": interest_confirm
            })
            st.session_state.step = 3
            st.rerun()

elif st.session_state.step == 3:
    st.subheader("Step 3: Review Your Responses")

    resp = st.session_state.responses

    st.markdown(f"""
**Main reason for reaching out:** {resp.get('situation', '—')}  
**Timeline:** {resp.get('timeline', '—')}  
**Perceived complexity:** Level {resp.get('complexity', '—')} / 5  

**Biggest question/concern:**  
{resp.get('main_concern', 'Not provided')}

**Preferred contact method:** {resp.get('contact_pref', '—')}

**Contact info provided (optional):**  
- Email: {resp.get('email') or 'Not provided'}  
- Phone: {resp.get('phone') or 'Not provided'}
""")

    st.markdown("---")

    today_str = date.today().strftime("%B %d, %Y")

    if st.button("Generate Summary PDF & Finish", type="primary"):
        summary_lines = [
            f"Reason for reaching out: {resp.get('situation')}",
            f"Timeline: {resp.get('timeline')}",
            f"Complexity level: {resp.get('complexity')}/5",
            f"Main concern: {resp.get('main_concern') or 'None provided'}",
            f"Preferred contact: {resp.get('contact_pref')}",
            f"Email: {resp.get('email') or 'Not provided'}",
            f"Phone: {resp.get('phone') or 'Not provided'}"
        ]
        summary_text = "\n".join(summary_lines)

        pdf_bytes = create_summary_pdf(summary_text, today_str)

        st.success("Summary PDF created!")
        st.download_button(
            label="Download Preliminary Summary (PDF)",
            data=pdf_bytes,
            file_name=f"CPA_Interest_Summary_{today_str}.pdf",
            mime="application/pdf"
        )

        st.info("Thank you! This summary will help me prepare for a productive conversation.")

        if st.button("Start Over (new prospect)"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()