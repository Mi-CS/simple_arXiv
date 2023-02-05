import os
import urllib
from typing import Optional
import pandas as pd


def pdf_download(dataframe: pd.DataFrame,
                 path: str,
                 max_pdfs: Optional[int] = None) -> None: 
    
    """Download the pdf files given a dataframe retrieved from
    ArXiv using the 'retrieve_results()' method. It catches the OSErrors
    and indicates for which manuscripts the error occurred. It saves 
    the pdfs as '[authors](year)title.pdf' and creates a new column
    in the present dataframe with the path to the pdf file.

    Parameters: 
            dataframe (pd.DataFrame): pandas dataframe obtained from
            the retrieve_results() method. It contains a pdf_link
            column with the link to download the pdf. 
            path (string): path to where save the downloaded pdfs.
            max_pdfs (int) [def. None]: Maximum number of pdfs downloaded. 
                If None, download all possible ones in 'dataframe'. 
    """
    
    max_pdfs = max_pdfs if max_pdfs else dataframe.shape[0]
    n_errors = []
    path_list = []
    

    if not os.path.exists(path): 
        raise FileNotFoundError(f"{path} does not exists.")

    for i, paper in dataframe[:max_pdfs].iterrows():
           
        auth = paper.authors
        if len(auth) > 2: 
            auth = f'{auth[0]}, et. al'
        elif len(auth) == 2: 
            auth = f'{auth[0]}, {auth[1]}'
        else:
            auth = f'{auth[0]}'

        year = paper.published[:4]
        title = paper.title[:60]

        file = f'[{auth}]({year}){title}.pdf'

        errors = "No errors." if not n_errors else f"Errors at {n_errors}."
        print(f'{i+1}/{max_pdfs} papers downloaded at {path}. {errors}',
            end='\r')

        try: 
            urllib.request.urlretrieve(paper.pdf_link,
                                    path+file)
            path_list.append(path+file)
        except OSError: 
            n_errors.append(i)
            path_list.append(None)

    # Add column inplace
    dataframe['path_to_pdf'] = path_list