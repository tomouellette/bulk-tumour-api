import requests
import pandas as pd
from bs4 import BeautifulSoup
from .utils import delimiter_type
from dataclasses import dataclass, field

class ZenodoRepository:
    """
    A class that consolidates all functions and information related to parsing Zenodo repositories.
    
    Args:
        path (str): a string containing the path to a Zenodo repository.
    
    """
    def __init__(self, path="https://zenodo.org/record/6670391"):
        self.path = path if path[-1] != '/' else path[:-1]        
        if 'https://' in self.path:
            self.path = path
        else:
            self.path = 'https://' + path
    
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
        self.contents = [(i.contents[0], path + i['href']) for i in tags]
        
        return self.contents
    
    def get_database(self, database_name='database.tsv') -> pd.DataFrame:
        """
        Loads the database file from the target Zenodo repository if present.
        The database file provides information on the structure of the repository
        and dataset and sample identifiers for downloading sequencing data.
        
        Args:
            database_name (str): the name of the database file in target zenodo repository
        
        Example:
            >>> repo = ZenodoRepository(path="https://zenodo.org/record/5931436")
            >>> repo.get_database()
                
        """        
        self.database = pd.read_csv(self.path + database_name, delimiter=delimiter_type(database_name))
        return self.database
    
    def get_synthetic_datasets(self, synthetic_meta_name='synthetic.tsv') -> None:
        """
        Lists all available synthetic datasets with references and descriptions.
        """
        self.synthetic = pd.read_csv(self.path + synthetic_meta_name, delimiter=delimiter_type(synthetic_meta_name))
        return self.synthetic
    
    def download_synthetic_dataset(self, dataset_name: str, save_path: str):
        """
        Download one of the available synthetic datasets by name
        
        Args:
            dataset_name (str): the name of the synthetic dataset listed in .list_synthetic_datasets()
        """
        if self.synthetic['dataset'].str.contains(dataset_name):
            # Send a GET request
            response = requests.get(self.path + '/synthetic/' + dataset_name)
            
            # Download data if response was successful
            if response.ok:
                open(save_path, 'wb').write(response.content)
            else:
                response.raise_for_status()            
        else:
            raise ValueError('The dataset name provided does not exist in the synthetic dataset list.')
        