import streamlit as st
import requests
from pyunpack import Archive
import os
import shutil
from io import BytesIO
import zipfile
from urllib.parse import unquote
from pathlib import Path

# Function to download file from URL
def download_file(url, path):
    response = requests.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)

# Function to extract archive
def extract_archive(file_path, extract_to):
    Archive(file_path).extractall(extract_to)

# Function to list all files in a directory recursively
def list_files(directory):
    return [str(p) for p in Path(directory).rglob('*') if p.is_file()]

# Function to display files based on type
def display_file(file_path):
    file_extension = Path(file_path).suffix.lower()
    if file_extension in ['.pdf']:
        with open(file_path, "rb") as f:
            st.write(f"Displaying PDF: {file_path}")
            st.components.v1.iframe(
                src=f"data:application/pdf;base64,{base64.b64encode(f.read()).decode()}",
                width=700, height=600
            )
    elif file_extension in ['.txt']:
        with open(file_path, "r") as f:
            st.write(f"Displaying Text File: {file_path}")
            st.text(f.read())
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
        st.write(f"Displaying Image: {file_path}")
        st.image(file_path, use_column_width=True)
    elif file_extension in ['.mp4', '.avi', '.mov']:
        st.write(f"Displaying Video: {file_path}")
        st.video(file_path)
    else:
        st.write(f"Unsupported file type: {file_extension}")

# Function to search files
def search_files(files, query):
    return [f for f in files if query.lower() in Path(f).name.lower()]

# Main app
def main():
    st.set_page_config(layout="wide")
    st.title("Enhanced Online File Viewer")

    # Sidebar
    st.sidebar.header("Input and Controls")
    url = st.sidebar.text_input("Enter the URL of the file:")
    search_query = st.sidebar.text_input("Search files:")

    # Download and extract button
    if st.sidebar.button("Download and Extract"):
        if url:
            temp_dir = "temp_files"
            os.makedirs(temp_dir, exist_ok=True)
            file_name = unquote(Path(url).name)
            file_path = os.path.join(temp_dir, file_name)
            download_file(url, file_path)
            if file_name.endswith(('.zip', '.rar', '.7z', '.tar.gz')):
                extract_dir = os.path.join(temp_dir, Path(file_name).stem)
                os.makedirs(extract_dir, exist_ok=True)
                extract_archive(file_path, extract_dir)
                files = list_files(extract_dir)
                filtered_files = search_files(files, search_query)
                st.session_state.files = filtered_files
            else:
                st.session_state.files = [file_path]
        else:
            st.sidebar.error("Please enter a URL.")

    # Main area
    tabs = st.tabs(["File Viewer", "Downloads"])

    with tabs[0]:
        if 'files' in st.session_state:
            st.header("File Viewer")
            selected_file = st.selectbox("Select a file to view:", st.session_state.files)
            display_file(selected_file)

    with tabs[1]:
        st.header("Downloads")
        if 'files' in st.session_state:
            selected_files = st.multiselect("Select files to download:", st.session_state.files)
            if st.button("Download Selected Files"):
                if selected_files:
                    with BytesIO() as buffer:
                        with zipfile.ZipFile(buffer, 'w') as zf:
                            for file in selected_files:
                                zf.write(file, Path(file).name)
                        st.download_button(
                            label="Download Selected Files",
                            data=buffer.getvalue(),
                            file_name="selected_files.zip",
                            mime="application/zip"
                        )
            if st.button("Download All Files"):
                with BytesIO() as buffer:
                    with zipfile.ZipFile(buffer, 'w') as zf:
                        for file in st.session_state.files:
                            zf.write(file, Path(file).name)
                    st.download_button(
                        label="Download All Files",
                        data=buffer.getvalue(),
                        file_name="all_files.zip",
                        mime="application/zip"
                    )

    # Cleanup
    if 'files' in st.session_state:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
