import requests
from bs4 import BeautifulSoup

def delimiter_type(filename: str) -> str:
    """
    Returns the delimiter type when loading a formatted text file.
    
    Args:
        filename (str): a string that includes the filename at end of string 
    """
    try:
        if filename[-4:] == ".csv":
            return ","
        if filename[-4:] in [".tsv", ".txt"]:
            return "\t"
    except:
        raise SyntaxError("The database file must be in .csv, .tsv, or .txt format.")