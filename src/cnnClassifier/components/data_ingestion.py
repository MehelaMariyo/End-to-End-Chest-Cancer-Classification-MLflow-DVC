import os
import zipfile
import gdown
import re
from src.cnnClassifier import logger
from src.cnnClassifier.utils.common import get_size
from src.cnnClassifier.entity.config_entity import DataIngestionConfig

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_file(self):
        '''
        Fetch data from the Google Drive URL, bypassing the 
        "Download anyway" virus scan warning for large files.
        '''
        try:
            dataset_url = self.config.source_URL
            zip_download_dir = self.config.local_data_file
            
            # Ensure target directory exists
            os.makedirs(os.path.dirname(zip_download_dir), exist_ok=True)
            logger.info(f"Downloading data from {dataset_url} into file {zip_download_dir}")

            # Robust Regex to extract Google Drive File ID from ANY format:
            # Works for: /d/FILE_ID/view, id=FILE_ID, or open?id=FILE_ID
            match = re.search(r'(r?id=|=/d/|/d/)([A-Za-z0-9_-]{33,})', dataset_url)
            
            if match:
                file_id = match.group(2)
            else:
                # Fallback if it's already just the clean ID string
                file_id = dataset_url

            logger.info(f"Extracted Google Drive File ID: {file_id}")

            # gdown handles the 'Download anyway' token natively when using the id parameter
            # setting fuzzy=True allows gdown to handle messy URLs as well
            gdown.download(id=file_id, output=zip_download_dir, quiet=False, fuzzy=True)
            
            logger.info(f"Successfully downloaded data into file {zip_download_dir}")

        except Exception as e:
            logger.error(f"Error occurred during file download: {str(e)}")
            raise e
    
    def extract_zip_file(self):
        '''
        zip_file_path: str
        Extract the zip file into the data directory
        Function return None
        '''
        unzip_path = self.config.unzip_dir
        os.makedirs(unzip_path, exist_ok=True)
        with zipfile.ZipFile(self.config.local_data_file, 'r') as zip_ref:
            zip_ref.extractall(unzip_path)