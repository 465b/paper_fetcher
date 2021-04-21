from scidownl.scihub import SciHub
import numpy as np
import os
import csv
from habanero import Crossref
import xml.etree.ElementTree as ET

def prepare_folders(output_folder='papers',temp_folder='temp'):

	try:
		os.mkdir(output_folder)
	except FileExistsError:
		pass

	try:
		os.mkdir(temp_folder)
	except FileExistsError:
		files = os.listdir(temp_folder)
		for file in files:
			os.remove(os.path.join(temp_folder,file))
            
	return output_folder


def fetch_entry_in_xml(root):
    for ii,item in enumerate(root.iter('record')):
        yield item
        

def fetch_titles_from_xml(root):
    for ii,item in enumerate(root.iter('titles')):
        for jj,sub_item in enumerate(item.iter('title')):
            for jj,subsub_item in enumerate(item.iter('style')):
                return subsub_item.text       
            
            
def fetch_authors_from_xml(root):
    for ii,item in enumerate(root.iter('contributors')):
        for jj,sub_item in enumerate(item.iter('authors')):
            authors = []
            for kk,subsub_item in enumerate(sub_item.iter('author')):
                for ll,subsubsub_item in enumerate(subsub_item.iter('style')):
                    authors.append(subsubsub_item.text)
            return authors
        
        
def fetch_journal_from_xml(root):
    for ii,item in enumerate(root.iter('titles')):
        for jj,sub_item in enumerate(item.iter('secondary-title')):
            for jj,subsub_item in enumerate(sub_item.iter('style')):
                return subsub_item.text
            
            
def flatten(list_of_strings):
    string = ""
    for item in list_of_strings:
        string += " "+item
    return string


def load_data_from_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()

    data = fetch_entry_in_xml(root)
    record = []
    for ii,entry in enumerate(data):
        title = fetch_titles_from_xml(entry)
        authors = fetch_authors_from_xml(entry)
        journal = fetch_journal_from_xml(entry)
        record.append({"title": title,"authors": authors,"journal": journal})
    
    dois = fetch_dois_from_crossref(record)    
    return dois


def fetch_dois_from_crossref(records):
    cr = Crossref()
    dois = records.copy()
    
    # link titles with dois
    for ii,item in enumerate(records):

        # goes thru all the papers and checks via crossref
        query = '"' + item["title"] + '"'\
              + " " + flatten(item["authors"])
        print(query)
        query_result = cr.works(query = query,limit=3)

        title = query_result['message']['items'][0]['title'][0]
        doi = query_result['message']['items'][0]['DOI']
        print(title)
        print(doi)
        dois[ii] = doi
    
    return dois


def download_from_scihub(DOIs,output_folder='papers',temp_folder='temp'):
	invalid_dois = []
	valid_dois = []
	for doi in DOIs:
		try:
			SciHub(doi,temp_folder).download(choose_scihub_url_index=3)
			path = os.getcwd()

			filenames = os.listdir(os.path.join(path,temp_folder))
			for filename in filenames:
				os.rename(os.path.join(path,temp_folder, filename),
				os.path.join(path,output_folder,doi.replace('/','_')))
			valid_dois.append(doi)
		
		except AttributeError:
			print(f'----------------------')
			print(f'[INFO] Paper {doi} not found.')
			print(f'----------------------')
			invalid_dois.append(doi)
	with open('invalid_dois.csv','w') as g:
		write = csv.writer(g)
		write.writerows([invalid_dois])


def clean_up(temp_folder='temp'):
    try:
        os.rmdir(temp_folder)
    except:
        pass


def download_papers(path):

    prepare_folders()
    dois = load_data_from_xml(path)
    download_from_scihub(dois,output_folder='papers',temp_folder='temp')
    clean_up()


if __name__ == "__main__":
	path = "Articles_P37916_0421_A5483.xml"
	download_papers(path)