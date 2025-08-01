import streamlit as st
import pandas as pd
import PyPDF2
from io import BytesIO, StringIO
from docx import Document

def file_uploader_component(label="Upload a file", key=None):
    st.write("📥 File uploader initialized.")

    uploaded_file = st.file_uploader(
        label,
        type=["csv", "xlsx", "pdf", "txt", "docx"],
        label_visibility="collapsed",
        key=key
    )

    df = None
    pdf_text = None
    doc_text = None

    print("📂 File uploader component created.")
    print(f"Uploaded file: {uploaded_file.name if uploaded_file else 'None'}")
    if uploaded_file is not None:
        print(f"📂 File uploaded: {uploaded_file.name} ({uploaded_file.type})")
        st.write(f"📄 Uploaded: `{uploaded_file.name}` — `{uploaded_file.type}`")
        file_type = uploaded_file.name.split('.')[-1].lower()
        st.write(f"🧾 Detected extension: `{file_type}`")

        try:
            if file_type == "csv":
                df = pd.read_csv(uploaded_file)
                st.success("✅ CSV loaded.")
                st.dataframe(df.head())

            elif file_type in ["xlsx", "xls"]:
                df = pd.read_excel(uploaded_file)
                st.success("✅ Excel loaded.")
                st.dataframe(df.head())

            elif file_type == "pdf":
                reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = "".join(page.extract_text() or "" for page in reader.pages)
                if pdf_text.strip():
                    st.success("✅ PDF text extracted.")
                    st.text_area("PDF Preview", pdf_text[:2000], height=300)
                else:
                    st.warning("⚠️ PDF loaded but no extractable text found.")

            elif file_type == "txt":
                content = uploaded_file.read()
                doc_text = content.decode("utf-8", errors="ignore")
                st.success("✅ TXT loaded.")
                st.text_area("TXT Preview", doc_text[:2000], height=300)

            elif file_type == "docx":
                document = Document(uploaded_file)
                doc_text = "\n".join([p.text for p in document.paragraphs])
                st.success("✅ DOCX loaded.")
                st.text_area("DOCX Preview", doc_text[:2000], height=300)

            else:
                st.warning(f"⚠️ File type `{file_type}` not supported.")
        except Exception as e:
            pass
        
    else:
        st.info("📂 No file uploaded yet.")
    

    return uploaded_file, df, pdf_text or doc_text
