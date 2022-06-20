import os
import requests
import pandas as pd
from typing import Union
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from .utils import delimiter_type, record_date
from dataclasses import dataclass, field

class ZenodoRepository:
    """
    A class that consolidates all functions and information related to parsing Zenodo repositories.
    
    Args:
        path (str): a string containing the path to a Zenodo repository.
    
    """
    def __init__(self,
            path="https://zenodo.org/record/6670391", 
            synthetic_datasets_name = "synthetic_datasets.tsv", 
            synthetic_samples_name = "synthetic_samples.tsv"
        ) -> None:       
        # Format path
        self.path = path if path[-1] != '/' else path[:-1]        
        if 'https://' in self.path:
            self.path = path
        else:
            self.path = 'https://' + path
            
        # Store names of meta and sample information files
        self.synthetic_datasets_name = synthetic_datasets_name
        self.synthetic_samples_name = synthetic_samples_name
    
    def get_contents(self) -> list:
        """
        Given a Zenodo repository URL, return a (i) a list of all filenames in the
        repository and (ii) the download links for each file in the repository.
        
        Example:
            >>> repo = ZenodoRepository(path="https://zenodo.org/record/5931436")
            >>> repo.get_contents()
                
        """
        # Send a GET request
        response = requests.get(self.path)
        
        # Check if the response was successful
        if response.ok:
            text = response.text
        else:
            response.raise_for_status()
        
        # Convert text to parsable HTML
        soup = BeautifulSoup(text, 'html.parser')
        
        # Subset only <a> tags that store file information
        tags = soup.find_all("a", {"class": "filename"})
        
        # Create a list of tuples containing the file name and download link
        self.contents = [(i.contents[0], self.path + i['href']) for i in tags]
        
        return self.contents
    
    def get_database(self, database_name='database.tsv') -> pd.DataFrame:
        """
        Loads the database file from the target Zenodo repository if present.
        The database file provides information on the structure of the repository
        and dataset and sample identifiers for downloading sequencing data.
        
        Args:
            database_name (str): the name of the database file in target zenodo repository
        
        Example:
            >>> repo = ZenodoRepository(path="https://zenodo.org/record/6670391")
            >>> repo.get_database()
                
        """        
        self.database = pd.read_csv(self.path + database_name, delimiter=delimiter_type(database_name))
        return self.database
    
    def list_synthetic_datasets(self) -> pd.DataFrame:
        """
        Lists all available synthetic datasets with references and descriptions.
        
        Args:
            synthetic_meta_name (str): the name of the synthetic datasets file in target zenodo repository
        
        Example:
            >>> datasets = repo.get_synthetic_datasets()
        
        """
        self.synthetic_datasets = pd.read_csv(self.path + '/files/' + self.synthetic_datasets_name, delimiter=delimiter_type(self.synthetic_datasets_name))
        return self.synthetic_datasets
    
    def list_synthetic_samples(self) -> pd.DataFrame:
        """
        Lists all the synthetic samples with corresponding summary statistics and metadata
        
        Args:
            synthetic_samples_name (str): the name of the synthetic samples file in target zenodo repository
        
        Example:
            >>> samples = repo.get_synthetic_samples()
        
        """
        self.synthetic_samples = pd.read_csv(self.path + '/files/' + self.synthetic_samples_name, delimiter=delimiter_type(self.synthetic_samples_name))
        return self.synthetic_samples
    
    def download_synthetic_dataset(self, dataset_name: str, save_path: str) -> None:
        """
        Download all samples in one of the available synthetic datasets
        
        Args:
            dataset_name (str): the name of the synthetic dataset listed in .list_synthetic_datasets()
            save_path (str): the output directory where downloaded dataset will be saved
            synthetic_meta_name (str): the name of the synthetic dataset metadata file in target zenodo repository
            synthetic_samples_name (str): the name of the synthetic dataset samples file in target zenodo repository
            
        Example:
            >>> repo.download_synthetic_dataset(dataset_name='timing', save_path='/home/user/data/')
        
        """
        # Format save_path string
        save_path = save_path if save_path[-1] != '/' else save_path[:-1]
        
        # Load synthetic dataset metadata if not "cached"
        if not hasattr(self, 'synthetic_datasets'):
            self.synthetic_datasets = pd.read_csv(self.path + '/files/' + self.synthetic_datasets_name, delimiter=delimiter_type(self.synthetic_datasets_name))            
        
        # Check if dataset name is valid and download all the data if true
        if dataset_name in list(self.synthetic['dataset']):
            # Load samples data frame
            samples = pd.read_csv(self.path + '/files/' +  self.synthetic_samples_name, delimiter=delimiter_type(self.synthetic_samples_name))
            
            # Filter samples by dataset name
            samples = samples.loc[samples['dataset'] == dataset_name, :]
            
            # Download all the samples
            print("\033[1mbulk-tumour-api\033[0m\n" + f"Downloading synthetic dataset: {dataset_name}\nNumber of files: {len(samples['file'])}")
            for sample in tqdm(samples['file']):
                timestamp = record_date()
                
                # Check if data path already exists
                if not os.path.exists(save_path + '/' + dataset_name + '_' + timestamp):
                    os.makedirs(save_path + '/' + dataset_name + '_' + timestamp)
                
                # Load and save sample data
                pd.read_csv(self.path + '/files/' +  sample, delimiter=delimiter_type(sample)).to_csv(
                    save_path + '/' + dataset_name + '_' + timestamp + '/' + sample,
                    index = False
                )
            
        else:
            raise ValueError(
                'The provided dataset name does not exist in the synthetic dataset list. \
                Please call .get_synthetic_datasets() to see the available synthetic datasets.'
            )
        
    def get_synthetic_sample(self, sample: str) -> dict:
        # Load synthetic dataset metadata if not "cached"
        if not hasattr(self, 'synthetic_samples'):
            self.synthetic_samples = pd.read_csv(self.path + '/files/' + self.synthetic_samples_name, delimiter=delimiter_type(self.synthetic_samples_name))
        
        # Extract length of 1 list
        if (type(samples) == list) & (len(samples) == 1):
            samples = samples[0]
        
        # Single sample loading
        if (type(samples) == str):
            # Filter sample
            sample = self.synthetic_samples.loc[self.synthetic_samples['file'] == samples, :]
            
            # Grabs all files associated with sample (if has_meta = True <=> same identifier)
            all_files = self.synthetic_samples.loc[self.synthetic_samples['identifier'] == list(sample['identifier'])[0], :]
            
            # Loadall sample data into a list
            all_files = {
                f: pd.read_csv(self.path + '/files/' +  f, delimiter=delimiter_type(f))
                for f in all_files['file']
            }
            
            return all_files
                