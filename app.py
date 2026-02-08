import streamlit as st
from docx import Document
from groq import Groq
import matplotlib.pyplot as plt

from datetime import datetime

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import re
import os

# ---------------------------------------
# App Configuration
# ---------------------------------------
st.set_page_config(
    page_title="AI Assignment Evaluation",
    layout="wide"
)

def brand_header():
    hcl_logo_path = "CSLogo.jfif"
   

    HCL_GRADIENT = "linear-gradient(90deg, #7C2AE8 0%, #0EA5EA 100%)"

    st.markdown(
        f"""
        <style>
            .brand-bar {{
                background: {HCL_GRADIENT};
                color: white;
                border-radius: 12px;
                padding: 10px;
                margin-bottom: 16px;
            }}

           
            .brand-title {{
                font-size: 23px;
                font-weight: 700;
                margin: 0;
            }}
            .brand-sub {{
                font-size: 13px;
                opacity: 0.9;
                margin: 0;
            }}
            .brand-right img {{
                height: 20px;
                margin-left: 8px;
                border-radius: 6px;
                background: rgba(255,255,255,0.05);
                padding: 6px;
            }}
            .stTabs [data-baseweb="tab"] {{
                background: #fff;
                border-radius: 10px;
                padding: 8px 12px;
                border: 1px solid #eef2f7;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([0.78, 0.22])

    with c1:
        st.markdown(
            """
            <div class="brand-bar">
                <p class="brand-title">Career Shaper™ — AI-Driven Document Evaluation System</p>
                <p class="brand-sub">Structured Academic Assessment Engine</p>
                
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown('<div class="brand-right" style="text-align:right;">', unsafe_allow_html=True)
        try: st.image(hcl_logo_path)
        except: pass
        st.markdown('</div>', unsafe_allow_html=True)

brand_header()


px.defaults.template = "plotly_white"
px.defaults.color_continuous_scale = px.colors.sequential.Blues


RESULT_FILE = "evaluation_results.xlsx"
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
tab1, tab2, tab3 = st.tabs(["📝 Evaluation", "📊 Analytics", "Report Card"])


with tab1:
    # ---------------------------------------
    # Helper Functions
    # ---------------------------------------
    def extract_text_from_docx(file):
        doc = Document(file)
        return "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())


    def evaluate_report(problem_statement, report_text):
        prompt = f"""
    You are an academic evaluator.

    PROBLEM STATEMENT:
    {problem_statement}

    Evaluate the learner submission strictly against the problem statement.

    For EACH section, assess:
    1. Marks
    2. Correctness (use of all required components)
    3. Completeness (coverage of all points)

    Scales:
    Correctness → Fully Aligned | Mostly Aligned | Partially Aligned | Misaligned
    Completeness → Comprehensive | Adequate | Limited | Incomplete

    Return the output EXACTLY in this format:

    SCORES:
    Executive Summary | Marks: x/15 | Correctness: <value> | Completeness: <value>
    Table of Contents | Marks: x/5 | Correctness: <value> | Completeness: <value>
    Key Challenges | Marks: x/15 | Correctness: <value> | Completeness: <value>
    AI Techniques Used | Marks: x/20 | Correctness: <value> | Completeness: <value>
    Benefits | Marks: x/15 | Correctness: <value> | Completeness: <value>
    Recommendation & Conclusion | Marks: x/15 | Correctness: <value> | Completeness: <value>
    Professional Quality | Marks: x/15 | Correctness: <value> | Completeness: <value>

    STRENGTHS:
    - Bullet points

    IMPROVEMENT_AREAS:
    - Bullet points

    OVERALL_SCORE: x

    LEARNER SUBMISSION:
    {report_text}
    """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content


    def parse_scores(text):
        pattern = (
            r"(.*?)\s*\|\s*Marks:\s*(\d+)/(\d+)\s*\|\s*"
            r"Correctness:\s*(.*?)\s*\|\s*Completeness:\s*(.*)"
        )

        matches = re.findall(pattern, text)
        rows = []

        for section, scored, total, correctness, completeness in matches:
            rows.append({
                "Section": section.strip(),
                "Marks Scored": int(scored),
                "Max Marks": int(total),
                "Correctness": correctness.strip(),
                "Completeness": completeness.strip()
            })

        return pd.DataFrame(rows)


    def extract_block(text, start, end):
        return text.split(start)[1].split(end)[0].strip()


    def flatten_section_scores(df):
        flat = {}
        for _, row in df.iterrows():
            key = row["Section"].replace(" ", "").replace("&", "")
            flat[f"{key}_Marks"] = row["Marks Scored"]
            flat[f"{key}_Correctness"] = row["Correctness"]
            flat[f"{key}_Completeness"] = row["Completeness"]
        return flat


    def save_to_excel(row_df):
        if os.path.exists(RESULT_FILE):
            existing = pd.read_excel(RESULT_FILE)
            final = pd.concat([existing, row_df], ignore_index=True)
        else:
            final = row_df

        final.to_excel(RESULT_FILE, index=False)


    # ---------------------------------------
    # Main Inputs (NO SIDEBAR)
    # ---------------------------------------
    st.markdown("## Learner & Assignment Details")

    col1, col2 = st.columns(2)
    with col1:
        learner_name = st.text_input("Learner Name")
        batch_name = st.text_input("Batch / Cohort")

    with col2:
        uploaded_file = st.file_uploader(
            "Upload Learner Report (.docx)", type=["docx"]
        )

    problem_statement = st.text_area(
        "Assignment Problem Statement",
        height=200
    )

    # ---------------------------------------
    # Evaluation Logic
    # ---------------------------------------
    if uploaded_file and learner_name and batch_name and problem_statement.strip():

        report_text = extract_text_from_docx(uploaded_file)

        if st.button("Evaluate Submission"):
            with st.spinner("Evaluating submission..."):
                evaluation_text = evaluate_report(
                    problem_statement, report_text
                )

            df_scores = parse_scores(evaluation_text)

            strengths = extract_block(
                evaluation_text, "STRENGTHS:", "IMPROVEMENT_AREAS:"
            )
            improvements = extract_block(
                evaluation_text, "IMPROVEMENT_AREAS:", "OVERALL_SCORE:"
            )
            overall_score = evaluation_text.split("OVERALL_SCORE:")[1].strip()

            st.markdown("---")
            st.markdown("## Evaluation Report")

            st.dataframe(df_scores, use_container_width=True)

            st.markdown("### Strengths")
            st.write(strengths)

            st.markdown("### Areas for Improvement")
            st.write(improvements)

            st.markdown(f"### Final Score: **{overall_score} / 100**")

            # ---------------------------------------
            # Excel Save (Section-wise)
            # ---------------------------------------
            section_data = flatten_section_scores(df_scores)

            result_row = {
                "Learner Name": learner_name,
                "Batch": batch_name,
                "Date": datetime.now().strftime("%d-%b-%Y"),
                "Overall Score": overall_score,
                "Strengths Summary": strengths[:300],
                "Improvement Summary": improvements[:300],
                "Problem Statement": problem_statement[:300]
            }
            result_row.update(section_data)

            save_to_excel(pd.DataFrame([result_row]))

            st.success(
                f"Evaluation stored successfully in `{RESULT_FILE}`"
            )

    else:
        st.info(
            "Please enter all required details and upload a report to proceed."
        )

with tab2:
    st.markdown("##  Evaluation Analytics Dashboard")
    st.caption("Performance insights, quality alignment, and learning outcomes")

    # --------------------------------------------------
    # Data Source Selection
    # --------------------------------------------------
    with st.container(border=True):
        source_option = st.radio(
            "Select Data Source",
            ["Use Stored Evaluation File", "Upload CSV / Excel"],
            horizontal=True
        )

        if source_option == "Use Stored Evaluation File":
            if not os.path.exists(RESULT_FILE):
                st.warning("No evaluation file found yet.")
                st.stop()
            df = pd.read_excel(RESULT_FILE)
        else:
            analytics_file = st.file_uploader(
                "Upload Evaluation File", type=["csv", "xlsx"]
            )
            if analytics_file is None:
                st.info("Please upload a file to continue.")
                st.stop()
            df = pd.read_csv(analytics_file) if analytics_file.name.endswith(".csv") else pd.read_excel(analytics_file)

    st.success(f"Loaded {len(df)} evaluation records")

    # --------------------------------------------------
    # Data Cleaning
    # --------------------------------------------------
    def clean_score(val):
        if pd.isna(val):
            return 0
        if isinstance(val, str) and "/" in val:
            return float(val.split("/")[0])
        return float(val)

    df["Overall Score Clean"] = df["Overall Score"].apply(clean_score)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    sections = sorted({c.replace("_Marks", "") for c in df.columns if c.endswith("_Marks")})

    # --------------------------------------------------
    # KPI SUMMARY
    # --------------------------------------------------
    st.markdown("### 🔑 Overall Performance Snapshot")

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Submissions", len(df))
    k2.metric("Learners", df["Learner Name"].nunique())
    k3.metric("Avg Score", f"{df['Overall Score Clean'].mean():.2f}")
    k4.metric("Max Score", df["Overall Score Clean"].max())
    k5.metric("Zero Scores", (df["Overall Score Clean"] == 0).sum())

    # --------------------------------------------------
    # BATCH PERFORMANCE
    # --------------------------------------------------
    with st.expander("### 🏫 Batch Performance"):

        batch_df = (
            df.groupby("Batch")["Overall Score Clean"]
            .agg(["count", "mean", "min", "max"])
            .reset_index()
            .rename(columns={
                "count": "Submissions",
                "mean": "Avg Score",
                "min": "Min",
                "max": "Max"
            })
        )
        # -----------------------------
        # Table (Full Width)
        # -----------------------------
        st.dataframe(
            batch_df.style.format({
                "Avg Score": "{:.2f}",
                "Min": "{:.0f}",
                "Max": "{:.0f}"
            }),
            use_container_width=True
        )

        st.markdown("---")

        # -----------------------------
        # Elegant Plotly Chart (Full Width)
        # -----------------------------
        fig = px.bar(
            batch_df,
            x="Batch",
            y="Avg Score",
            text="Avg Score",
            color="Avg Score",
            color_continuous_scale=[
                "#2E86C1",  # professional blue
                "#28B463",  # green
                "#F1C40F",  # yellow
                "#E67E22",  # orange
                "#C0392B"   # red
            ],
            title="Average Overall Score by Batch"
        )

        fig.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside"
        )

        fig.update_layout(
            height=420,
            title_x=0.5,
            xaxis_title="Batch",
            yaxis_title="Average Score",
            font=dict(size=14),
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)


    # --------------------------------------------------
    # LEARNER PERFORMANCE
    # --------------------------------------------------
    with st.expander("### 👤 Learner Performance Summary"):

        learner_df = (
            df.groupby("Learner Name")["Overall Score Clean"]
            .agg(["count", "mean", "max", "min"])
            .reset_index()
            .rename(columns={
                "count": "Attempts",
                "mean": "Avg Score",
                "max": "Best",
                "min": "Worst"
            })
        )

        st.dataframe(learner_df, use_container_width=True)

    # --------------------------------------------------
    # SECTION-WISE MARKS
    # --------------------------------------------------
    with st.expander("### 🧩 Section-Wise Marks Analysis"):

        section_df = pd.DataFrame([
            {
                "Section": sec,
                "Average Marks": df[f"{sec}_Marks"].fillna(0).mean(),
                "Max Marks": df[f"{sec}_Marks"].fillna(0).max(),
                "Min Marks": df[f"{sec}_Marks"].fillna(0).min()
            }
            for sec in sections
        ])

            # --------------------------------------------------
        # SECTION-WISE MARKS ANALYSIS
        # --------------------------------------------------
        section_df = pd.DataFrame([
            {
                "Section": sec,
                "Average Marks": df[f"{sec}_Marks"].fillna(0).mean(),
                "Max Marks": df[f"{sec}_Marks"].fillna(0).max(),
                "Min Marks": df[f"{sec}_Marks"].fillna(0).min()
            }
            for sec in sections
        ])

            # -----------------------------
            # Table (Full Width)
            # -----------------------------
        st.dataframe(
                section_df.style.format({
                    "Average Marks": "{:.2f}",
                    "Max Marks": "{:.0f}",
                    "Min Marks": "{:.0f}"
                }),
                use_container_width=True
            )

        st.markdown("---")

            # -----------------------------
            # Full-Width Horizontal Bar Chart
            # -----------------------------
        fig = px.bar(
                section_df.sort_values("Average Marks"),
                x="Average Marks",
                y="Section",
                orientation="h",
                text="Average Marks",
                color="Average Marks",
                color_continuous_scale=[
                    "#2E86C1",  # blue
                    "#5DADE2",
                    "#28B463",  # green
                    "#F4D03F",  # yellow
                    "#E67E22"
                ],
                title="Average Marks by Report Section"
            )

        fig.update_traces(
                texttemplate="%{text:.1f}",
                textposition="outside"
            )

        fig.update_layout(
                height=460,
                title_x=0.5,
                xaxis_title="Average Marks",
                yaxis_title="Section",
                font=dict(size=14),
                plot_bgcolor="white",
                paper_bgcolor="white",
                showlegend=False
            )

        st.plotly_chart(fig, use_container_width=True)


    # --------------------------------------------------
    # CORRECTNESS ALIGNMENT
    # --------------------------------------------------
    with st.expander("### ✅ Correctness Alignment Distribution"):

        alignment_df = pd.DataFrame([
            {
                "Section": sec,
                "Fully Aligned": (df[f"{sec}_Correctness"] == "Fully Aligned").mean() * 100,
                "Mostly Aligned": (df[f"{sec}_Correctness"] == "Mostly Aligned").mean() * 100,
                "Partially Aligned": (df[f"{sec}_Correctness"] == "Partially Aligned").mean() * 100,
                "Misaligned": (df[f"{sec}_Correctness"] == "Misaligned").mean() * 100
            }
            for sec in sections if f"{sec}_Correctness" in df.columns
        ]).round(2)

        alignment_long = alignment_df.melt(
            id_vars="Section",
            var_name="Alignment",
            value_name="Percentage"
        )

        fig = px.bar(
            alignment_long,
            x="Section",
            y="Percentage",
            color="Alignment",
            text="Percentage",
            title="Correctness Alignment by Section"
        )

        fig.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
        fig.update_layout(
            barmode="stack",
            height=520,
            title_x=0.5,
            font=dict(size=13),
            legend_title_text="Alignment Level"
        )

        st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # SCORE DISTRIBUTION
    # --------------------------------------------------
    with st.expander("### 📈 Overall Score Distribution"):

        fig = px.histogram(
            df,
            x="Overall Score Clean",
            nbins=10,
            color_discrete_sequence=["#636EFA"],
            title="Distribution of Overall Scores"
        )

        fig.update_layout(
            height=420,
            title_x=0.5,
            font=dict(size=14)
        )

        st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # QUALITATIVE INSIGHTS
    # --------------------------------------------------
    with st.expander("📝 Qualitative Feedback Snapshot"):
        st.dataframe(
            df[["Learner Name", "Strengths Summary", "Improvement Summary"]]
            .dropna()
            .head(10),
            use_container_width=True
        )

with tab3:
    st.markdown("## Learner Evaluation Report Card")

    # ---------------------------------------
    # Filters (Batch → Learner Dependency)
    # ---------------------------------------
    fcol1, fcol2 = st.columns(2)

    with fcol1:
        selected_batch = st.selectbox(
            "Select Batch",
            sorted(df["Batch"].dropna().unique())
        )

    filtered_df = df[df["Batch"] == selected_batch]

    with fcol2:
        selected_learner = st.selectbox(
            "Select Learner",
            sorted(filtered_df["Learner Name"].dropna().unique())
        )

    learner_df = filtered_df[filtered_df["Learner Name"] == selected_learner]

    if learner_df.empty:
        st.warning("No records found for selected learner.")
        st.stop()

    record = learner_df.iloc[0]

    # ---------------------------------------
    # KPI Report Card
    # ---------------------------------------
    st.markdown("### 📊 Performance Summary")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Overall Score", record["Overall Score Clean"])
    k2.metric("Batch", record["Batch"])
    k3.metric("Evaluation Date", record["Date"].strftime("%d %b %Y"))
    k4.metric("Attempt", learner_df.shape[0])

    # ---------------------------------------
    # Section-wise Score Breakdown
    # ---------------------------------------
    st.markdown("### 🧩 Section Performance Overview")

    col_left, col_right = st.columns([1.4, 1])

    # ---------------------------------------
    # LEFT: Section-wise Marks
    # ---------------------------------------
    with col_left:
        section_scores = [
            {
                "Section": sec,
                "Marks": record.get(f"{sec}_Marks", 0)
            }
            for sec in sections
        ]

        section_score_df = pd.DataFrame(section_scores)

        fig_marks = px.bar(
            section_score_df,
            x="Marks",
            y="Section",
            orientation="h",
            text="Marks",
            color="Marks",
            color_continuous_scale=px.colors.sequential.Blues,
            title="Section-wise Marks"
        )

        fig_marks.update_traces(
            texttemplate="%{text:.0f}",
            textposition="outside"
        )

        fig_marks.update_layout(
            height=420,
            title_x=0.5,
            font=dict(size=14),
            showlegend=False,
            margin=dict(l=40, r=20, t=60, b=40)
        )

        st.plotly_chart(fig_marks, use_container_width=True)

    # ---------------------------------------
    # RIGHT: Correctness Alignment
    # ---------------------------------------
    with col_right:
        alignment_rows = []
        for sec in sections:
            corr_col = f"{sec}_Correctness"
            if corr_col in df.columns:
                alignment_rows.append({
                    "Section": sec,
                    "Alignment": record.get(corr_col, "Not Available")
                })

        if alignment_rows:
            align_df = pd.DataFrame(alignment_rows)

            fig_align = px.pie(
                align_df,
                names="Alignment",
                hole=0.5,
                title="Correctness Alignment"
            )

            fig_align.update_layout(
                height=420,
                title_x=0.5,
                font=dict(size=13),
                legend_title_text="Alignment Level"
            )

            st.plotly_chart(fig_align, use_container_width=True)
        else:
            st.info("Correctness alignment data not available.")

    # ---------------------------------------
    # Qualitative Feedback
    # ---------------------------------------
    st.markdown("### 🗒️ Qualitative Feedback")

    f1, f2 = st.columns(2)

    with f1:
        st.markdown("**Strengths**")
        st.info(record.get("Strengths Summary", "Not provided"))

    with f2:
        st.markdown("**Areas for Improvement**")
        st.warning(record.get("Improvement Summary", "Not provided"))
