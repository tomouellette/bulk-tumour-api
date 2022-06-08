from .utils import list_zenodo_contents
from dataclasses import dataclass, field

class ZenodoRepository:
    """
    A class that consolidates all functions and information related to parsing Zenodo repositories.
    
    Args:
        path (str): a string containing the path to a Zenodo repository.
        example (bool): if True, a pre-defined path is used.
    """
    def __init__(self, path=None, example=False):
        if example == False:
            self.path = path
        else:
            self.path = "https://zenodo.org/record/5931436"
    
    def contents(self) -> list:
        """
        List all files in the current repository
        """
        return list_zenodo_contents(path = self.path)

