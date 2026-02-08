# EvalAI Studio

DocEvalAI Studio is an AI-driven academic evaluation application built using Streamlit and large language models.  
It enables educators and evaluators to assess learner submissions objectively against a defined problem statement and rubric.

The tool supports structured, section-wise evaluation with qualitative feedback and persistent result storage.

---

## Key Features

- Upload learner reports in **Microsoft Word (.docx) format**
- Enter assignment problem statement dynamically
- AI-based evaluation using structured academic rubrics
- Section-wise scoring with correctness and completeness assessment
- Overall score calculation with qualitative strengths and improvement areas
- Automatic storage of evaluation results in Excel format
- Append-only result tracking for batch-level analysis

---

## Evaluation Dimensions

Each submission is evaluated across multiple sections, including:
- Executive Summary
- Table of Contents
- Key Challenges
- AI Techniques Used
- Benefits
- Recommendation and Conclusion
- Professional Quality

Each section is assessed on:
- Marks
- Correctness (alignment with requirements)
- Completeness (coverage of expected points)

---

## Technology Stack

- **Streamlit** – Web application framework
- **Groq LLM API** – AI-based evaluation engine
- **python-docx** – Word document text extraction
- **Pandas & OpenPyXL** – Result storage and management

---

## Output

- On-screen structured evaluation report
- Section-wise score table
- Qualitative feedback summaries
- Excel file (`evaluation_results.xlsx`) for record keeping

---

## Use Cases

- Academic assignments and projects
- Faculty-assisted evaluation
- AI-supported grading workflows
- Training programs and certifications
- Moderation and audit-ready assessments

---

## Note

EvalAI Studio is designed as a **decision-support tool** for evaluators.  
Final grading authority always remains with the faculty or assessor.

---

## License

This project is intended for educational and academic use.
