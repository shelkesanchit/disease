#!/usr/bin/env python3
"""Download model files from GitHub LFS if they don't exist or are invalid."""
import os
import sys
import urllib.request

MODEL_FILES = {
    'grape_model.h5': 'https://media.githubusercontent.com/media/shelkesanchit/disease/main/grape_model.h5',
    'grape_leaf_disease_model.h5': 'https://media.githubusercontent.com/media/shelkesanchit/disease/main/grape_leaf_disease_model.h5',
    'grape_variety_model.pkl': 'https://media.githubusercontent.com/media/shelkesanchit/disease/main/grape_variety_model.pkl'
}

def is_lfs_pointer(filepath):
    """Check if file is a Git LFS pointer file."""
    if not os.path.exists(filepath):
        return False
    with open(filepath, 'rb') as f:
        first_line = f.readline()
        return first_line.startswith(b'version https://git-lfs.github.com')

def download_file(url, filepath):
    """Download a file from URL."""
    print(f"Downloading {filepath} from {url}...")
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"✓ Successfully downloaded {filepath}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {filepath}: {e}")
        return False

def main():
    """Download all required model files."""
    print("Checking model files...")
    
    for filename, url in MODEL_FILES.items():
        if not os.path.exists(filename):
            print(f"File {filename} not found.")
            download_file(url, filename)
        elif is_lfs_pointer(filename):
            print(f"File {filename} is a Git LFS pointer, downloading actual file...")
            download_file(url, filename)
        else:
            print(f"✓ {filename} already exists")
    
    print("Model files check complete!")

if __name__ == '__main__':
    main()
