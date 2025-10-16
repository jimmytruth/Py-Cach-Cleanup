import os
import shutil
import logging
from pathlib import Path
import time

# Configure logging
logging.basicConfig(
    filename='pycache_cleanup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_logger():
    """Set up the logger with a console handler."""
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)

def is_safe_path(path):
    """Check if the path is safe to delete (avoid system-critical directories)."""
    unsafe_dirs = [
        'Windows', 'System32', 'Program Files', 'Program Files (x86)',
        'Users', 'AppData', '$Recycle.Bin', 'Recovery'
    ]
    path_str = str(path).lower()
    return not any(unsafe_dir.lower() in path_str for unsafe_dir in unsafe_dirs)

def remove_pycache(root_dir):
    """Recursively find and remove __pycache__ directories and .pyc/.pyo files."""
    removed_count = 0
    errors = 0
    start_time = time.time()

    logging.info(f"Starting cleanup in {root_dir}")

    try:
        for root, dirs, files in os.walk(root_dir, topdown=True):
            # Check for __pycache__ directories
            if '__pycache__' in dirs and is_safe_path(Path(root) / '__pycache__'):
                pycache_path = Path(root) / '__pycache__'
                try:
                    shutil.rmtree(pycache_path)
                    logging.info(f"Removed directory: {pycache_path}")
                    removed_count += 1
                except Exception as e:
                    logging.error(f"Failed to remove {pycache_path}: {e}")
                    errors += 1
                # Remove __pycache__ from dirs to avoid descending into it
                dirs.remove('__pycache__')

            # Check for .pyc and .pyo files
            for file in files:
                if file.endswith(('.pyc', '.pyo')) and is_safe_path(Path(root) / file):
                    file_path = Path(root) / file
                    try:
                        os.remove(file_path)
                        logging.info(f"Removed file: {file_path}")
                        removed_count += 1
                    except Exception as e:
                        logging.error(f"Failed to remove {file_path}: {e}")
                        errors += 1

    except Exception as e:
        logging.error(f"Error walking directory {root_dir}: {e}")
        errors += 1

    elapsed_time = time.time() - start_time
    logging.info(f"Cleanup in {root_dir} completed. Removed {removed_count} items. Errors: {errors}. Time: {elapsed_time:.2f} seconds")
    return removed_count, errors

def main():
    """Main function to clean __pycache__ from C: and D: drives."""
    setup_logger()
    logging.info("Starting __pycache__ cleanup script")

    drives = ['C:\\', 'D:\\']
    total_removed = 0
    total_errors = 0

    for drive in drives:
        if not os.path.exists(drive):
            logging.warning(f"Drive {drive} does not exist or is not accessible")
            continue
        removed, errors = remove_pycache(drive)
        total_removed += removed
        total_errors += errors

    logging.info(f"Total items removed: {total_removed}. Total errors: {total_errors}")
    print(f"Cleanup completed. Removed {total_removed} items. Errors: {total_errors}. Check pycache_cleanup.log for details.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Script interrupted by user")
        print("Cleanup interrupted by user. Check pycache_cleanup.log for details.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"An unexpected error occurred. Check pycache_cleanup.log for details.")