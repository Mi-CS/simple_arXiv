import urllib, urllib.request
import xml.etree.ElementTree as ET
import pandas as pd
from typing import Optional, Tuple


def retrieve_results(query: str,
                      max_results: int,
                      ids: Optional[Tuple[str]] = None,
                      clean_abstract: bool = True,
                      first_result: Optional[int] = 0): 
    """
    Returns a pandas dataframe with the query results via ArXiv API, contaning 
    the specified fields. It retrieves the max_results manuscripts ordered by 
    'last update'.

    Parameters: 
            query (str): query to search via arXiv API.
            max_results (int): maximum number of papers to be retrieved.
            ids (tuple(str)) [def. None]: Tuple contaning the specified fields to
                retrieve. If 'None', the following are used to build the dataframe:
                ('id', 'updated', 'published', 'title', 'summary', 'author', 'link', 'category')
            clean_abstract (bool) [def. True]: whether to lowcase and remove initial
                whitespaces in the 'summary' field. 
            first_result (int) [def. 0]: whether to ignore the first 'first_result' papers.

    Returns: 
            paper_dataframe (pd.DataFrame): pandas dataframe with the specified fields
                for the papers retrieved. 
    """

    if not ids: 
        ids = ('id', 'updated', 'published', 'title', 'summary', 'author', 'link', 'category')
    

    papers_list = []

    # Retrieve papers in groups of 10 000
    qn = (i for i in range(first_result, first_result + max_results, 1000))
    for start in qn: 
        end = min(1000, max_results-start+first_result)

        base_url = 'http://export.arxiv.org/api/'
        query_url = f'query?search_query=all:{query}'
        results_url = f'&start={start}&max_results={end}'
        order_url = '&sortBy=lastUpdatedDate&sortOrder=descending'
        url = base_url + query_url + results_url + order_url
        
        with urllib.request.urlopen(url) as rr:
            data = rr.read().decode('utf-8')
        
        root = ET.fromstring(data)
        papers_list.extend(_add_papers(root, ids, clean=clean_abstract))
        
    return pd.DataFrame(papers_list)


def _add_papers(root, ids, clean): 
    """
    Returns a list of the entries as dictionaries from an
    Element Tree object.
    """
    
    all_papers = []
    ns = {'r':'http://www.w3.org/2005/Atom'} # xml namespace
    entries = root.findall('r:entry', namespaces=ns)

    # Iterate over entries and save selected fields (ids)
    for entry in entries:
        curr_entry = {}
        for ell in entry: 
            tag = ell.tag.replace('{' + ns['r'] + '}', '')

            if tag not in ids:
                continue

            if tag == 'author': 
                if 'authors' not in curr_entry: 
                    curr_entry['authors'] = [ell[0].text]
                else:
                    curr_entry['authors'].append(ell[0].text)

            elif tag == 'link': 
                if 'title' in ell.attrib and ell.attrib['title'] == 'pdf':
                    address = ell.attrib['href']
                    export_split = address.find('://')+3
                    curr_entry['pdf_link'] = address[:export_split] +\
                         'export.' + address[export_split:]
            
            elif clean and tag == 'summary': 
                abstract = ell.text.lower().replace('\n', ' ')
                abstract = abstract if abstract[:2]!='  ' else abstract[2:]
                curr_entry[tag] = abstract
        
            elif tag == 'category':
                if 'category' not in curr_entry:
                    curr_entry['category'] = [ell.attrib['term']]
                else:
                    curr_entry['category'].append(ell.attrib['term'])
      
            else:
                curr_entry[tag] = ell.text
        all_papers.append(curr_entry)
    return all_papers

