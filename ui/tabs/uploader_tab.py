import streamlit as st
import requests
import json
from ui.components.ui_helpers import render_section_header, render_status_message, render_clean_button

def render_uploader_tab():
    """Render the File Uploader tab."""
    render_section_header("File Upload", "")
    
    from ui.components.file_uploader import file_uploader_component
    uploaded_file, df, extracted_text = file_uploader_component()

    if df is not None:
        render_status_message("DataFrame loaded. Ready for agents.", "success")
        st.session_state["uploaded_df"] = df

    elif extracted_text:
        render_status_message("Document text extracted. Ready to index.", "success")
        st.text_area("Extracted Content", value=extracted_text[:1000] + "...", height=200, disabled=True)

        if render_clean_button("Index to Vultr Vectorstore", "index_to_vultr", use_container_width=True):
            api_key = st.secrets.get("VULTR_API_KEY")
            collection_name = st.secrets.get("VULTR_COLLECTION_NAME")
            
            if not api_key or not collection_name:
                render_status_message(
                    "Missing `VULTR_API_KEY` or `VULTR_COLLECTION_NAME` in environment.", 
                    "error"
                )
            else:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "content": extracted_text,
                    "description": f"Content from {uploaded_file.name if uploaded_file else 'uploaded file'}",
                    "auto_chunk": True,
                    "auto_embed": True
                }

                try:
                    response = requests.post(
                        f"https://api.vultrinference.com/v1/vector_store/{collection_name}/items",
                        headers=headers,
                        data=json.dumps(payload)
                    )

                    if response.status_code == 200:
                        render_status_message("Submitted successfully!", "success")
                    elif response.status_code == 403:
                        render_status_message(
                            "Unauthorized: Please check your API key or collection name.", 
                            "error"
                        )
                    else:
                        render_status_message("Failed to submit to the vector store.", "error")

                except Exception as e:
                    render_status_message("Could not connect to the vector store API.", "error")

    else:
        render_status_message("Upload a file to begin.", "info")
