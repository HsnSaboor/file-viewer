import streamlit as st
import requests
import shutil
import os
from pathlib import Path
import py7zr

# Function to download file from URL
def download_file(url, path):
    response = requests.get(url)
    if response.status_code == 200 and response.content:
        with open(path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {url} to {path}")
    else:
        print(f"Failed to download {url}. Status code: {response.status_code}")
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

# Main app
def main():
    st.set_page_config(layout="wide")
    st.title("Enhanced Online File Viewer")

    # Sidebar
    st.sidebar.header("Input and Controls")
    url = st.sidebar.text_input("Enter the URL of the file:")

    # Download and extract button
    if st.sidebar.button("Download and Extract"):
        if url:
            temp_dir = Path.cwd() / "temp_files"
            temp_dir.mkdir(parents=True, exist_ok=True)
            file_name = Path(url).name
            file_path = temp_dir / file_name
            download_file(url, file_path)
            if file_path.exists() and file_path.is_file():
                if str(file_name).endswith(('.zip', '.rar', '.7z', '.tar.gz')):
                    extract_dir = temp_dir / Path(file_name).stem
                    extract_dir.mkdir(parents=True, exist_ok=True)
                    extract_archive(file_path, extract_dir)
                    files = list_files(extract_dir)
                    filtered_files = search_files(files, "")
                    st.session_state.files = [str(f) for f in filtered_files]
                else:
                    st.warning(f"File {file_name} is not an archive.")
            else:
                st.error(f"File not found: {file_path}")
        else:
            st.sidebar.error("Please enter a URL.")

    # Main area
    if 'files' in st.session_state:
        st.header("File Viewer")
        selected_file = st.selectbox("Select a file to view:", st.session_state.files)
        # Add display_file function here as needed

if __name__ == "__main__":
    main()
