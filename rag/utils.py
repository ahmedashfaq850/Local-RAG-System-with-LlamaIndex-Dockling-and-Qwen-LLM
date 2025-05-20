"""
Utility functions for handling Excel files and other common operations.
"""

import pandas as pd
import tempfile
import os
from typing import Tuple, Optional


def save_uploaded_file(uploaded_file) -> Tuple[str, str]:
    """
    Save an uploaded file to a temporary directory.

    Args:
        uploaded_file: The uploaded file object from Streamlit

    Returns:
        Tuple containing (temporary directory path, file path)
    """
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    return temp_dir, file_path


def display_excel(file) -> Optional[pd.DataFrame]:
    """
    Read and return an Excel file as a pandas DataFrame.

    Args:
        file: The file object to read

    Returns:
        pandas DataFrame containing the Excel data
    """
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None
