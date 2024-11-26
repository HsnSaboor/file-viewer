import streamlit as st
import requests
import shutil
import os
import base64
import zipfile
import io
from pathlib import Path
import py7zr

# Define lists of supported extensions
archive_extensions = ['.zip', '.rar', '.7z', '.tar.gz']
image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
video_extensions = ['.mp4', '.avi', '.mov']
text_extensions = ['.txt', '.html', '.js', '.css', '.json', '.py']
pdf_extensions = ['.pdf']

# Function to download file from URL
def download_file(url, path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {url} to {path}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        st.error(f"Failed to download file from {url}")
    except Exception as e:
        print(f"Error downloading file: {e}")
        st.error(f"Failed to download file from {url}")

# Function to extract archive
def extract_archive(file_path, extract_dir):
    try:
        if str(file_path).endswith('.7z'):
            with py7zr.SevenZipFile(str(file_path), mode='r') as z:
                z.extractall(path=str(extract_dir))
            print(f"Extracted {file_path} to {extract_dir}")
        else:
            shutil.unpack_archive(str(file_path), str(extract_dir))
            print(f"Extracted {file_path} to {extract_dir}")
    except Exception as e:
        print(f"Error extracting archive: {e}")
        st.error(f"Error extracting archive: {e}")

# Function to list all files in a directory recursively
def list_files(directory):
    return [str(p) for p in Path(directory).rglob('*') if p.is_file()]

# Function to search files
def search_files(files, query):
    return [f for f in files if query.lower() in Path(f).name.lower()]

# Function to display files based on type
def display_file(file_path):
    file_extension = Path(file_path).suffix.lower()
    if file_extension in ['.pdf']:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
            st.components.v1.html(pdf_display)
    elif file_extension in image_extensions:
        st.image(file_path, use_container_width=True)

    elif file_extension in video_extensions:
        st.video(file_path)
    elif file_extension in text_extensions:
        with open(file_path, "r") as f:
            st.code(f.read(), language=file_extension[1:] if file_extension[1:] else "text")
    else:
        st.warning(f"Unsupported file type: {file_extension}")
        st.download_button(
            label=f"Download {Path(file_path).name}",
            data=open(file_path, "rb").read(),
            file_name=Path(file_path).name,
            mime="application/octet-stream"
        )

# Main app
def main():
    st.set_page_config(layout="wide")
    st.title("Universal File Viewer and Downloader")

    # Create a unique temp directory for each session
    temp_dir = Path.cwd() / "temp_files"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Sidebar
    st.sidebar.header("Input and Controls")
    url = st.sidebar.text_input("Enter the URL of the file:")
    search_query = st.sidebar.text_input("Search files:")

    # Download and process button
    if st.sidebar.button("Download and Process"):
        if url:
            file_name = Path(url).name
            file_path = temp_dir / file_name
            download_file(url, file_path)
            if file_path.exists() and file_path.is_file():
                # Determine file type and handle accordingly
                if file_name.lower().endswith(tuple(archive_extensions)):
                    extract_dir = temp_dir / Path(file_name).stem
                    extract_dir.mkdir(parents=True, exist_ok=True)
                    extract_archive(file_path, extract_dir)
                    files = list_files(extract_dir)
                    filtered_files = search_files(files, search_query)
                    st.session_state.files = [str(f) for f in filtered_files]
                    st.success(f"Extracted {len(st.session_state.files)} files.")
                elif file_name.lower().endswith(tuple(image_extensions + video_extensions + text_extensions + pdf_extensions)):
                    st.session_state.files = [str(file_path)]
                    st.success(f"File ready to view or download.")
                else:
                    st.warning(f"Unsupported file type for {file_name}")
            else:
                st.error(f"File not found: {file_path}")
        else:
            st.sidebar.error("Please enter a URL.")

    # Main area
    if 'files' in st.session_state:
        st.header("File Browser")
        selected_file = st.selectbox("Select a file:", st.session_state.files)
        display_file(selected_file)
        # Download button for individual files
        st.download_button(
            label=f"Download {Path(selected_file).name}",
            data=open(selected_file, "rb").read(),
            file_name=Path(selected_file).name,
            mime="application/octet-stream"
        )

    # Cleanup temp directory at the end of the session
    if temp_dir.exists() and temp_dir.is_dir():
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
