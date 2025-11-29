#!/usr/bin/env python3
"""Download model files from GitHub LFS if they don't exist or are invalid."""
import os
import sys
import urllib.request

MODEL_FILES = {
    'grape_model.h5': 'https://huggingface.co/Sanchit6303/disease-models/resolve/main/grape_model.h5',
    'grape_leaf_disease_model.h5': 'https://huggingface.co/Sanchit6303/disease-models/resolve/main/grape_leaf_disease_model.h5',
    'grape_variety_model.pkl': 'https://huggingface.co/Sanchit6303/disease-models/resolve/main/grape_variety_model.pkl'
}

def is_lfs_pointer(filepath):
    """Check if file is a Git LFS pointer file."""
    if not os.path.exists(filepath):
        return False
    
    # Check file size - LFS pointers are very small (< 200 bytes)
    file_size = os.path.getsize(filepath)
    if file_size < 500:  # Real model files are much larger
        return True
    
    # Also check content
    try:
        with open(filepath, 'rb') as f:
            first_line = f.readline()
            if first_line.startswith(b'version https://git-lfs.github.com'):
                return True
    except:
        pass
    
    return False

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
    print("=" * 60)
    print("Checking model files...")
    print("=" * 60)
    
    success_count = 0
    for filename, url in MODEL_FILES.items():
        if not os.path.exists(filename):
            print(f"⚠ File {filename} not found.")
            if download_file(url, filename):
                success_count += 1
        elif is_lfs_pointer(filename):
            file_size = os.path.getsize(filename)
            print(f"⚠ File {filename} is a Git LFS pointer ({file_size} bytes), downloading actual file...")
            # Remove the LFS pointer file first
            os.remove(filename)
            if download_file(url, filename):
                success_count += 1
        else:
            file_size = os.path.getsize(filename)
            print(f"✓ {filename} already exists ({file_size:,} bytes)")
            success_count += 1
    
    print("=" * 60)
    print(f"Model files check complete! {success_count}/{len(MODEL_FILES)} files ready")
    print("=" * 60)
    
    if success_count < len(MODEL_FILES):
        print("⚠ WARNING: Some model files are missing!")
        sys.exit(1)

if __name__ == '__main__':
    main()
