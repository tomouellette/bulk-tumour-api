import requests
from bs4 import BeautifulSoup

def list_zenodo_contents(path: str) -> list:
    """
    Given a Zenodo repository URL, return a (i) a list of all filenames in the
    repository and (ii) the download links for each file in the repository.
    
    Args:
        path (str): a string containing the path to a Zenodo repository.
    
    Example:
        >>> list_zenodo_contents(path = "https://zenodo.org/record/5931436/")
    
    """
    # Send a GET request
    response = requests.get(path)
    
    # Check if the response was successful
    if response.ok:
        text = response.text
    else:
        response.raise_for_status()
    
    # Convert text to parsable HTML
    soup = BeautifulSoup(text, 'html.parser')
    
    # Subset only <a> tags that store file information
    tags = soup.find_all("a", {"class": "filename"})
    
    # Modify path name to build download links
    path = path[:-1] if path[-1] == '/' else path
    
    return [(i.contents[0], path + i['href']) for i in tags]