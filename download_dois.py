from scidownl.scihub import SciHub
import numpy as np
import os
import csv
from habanero import Crossref

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

def load_data_from_csv(path,doi_or_title,seperator=','):
    if doi_or_title == 'doi':
        with open(path) as f:
            dois = f.read().splitlines()

    elif doi_or_title == 'title':
        
        # read lines from csv file
        with open(path) as csvfile:
            items = []
            #item = f.read().splitlines()
            reader = csv.reader(csvfile, delimiter='|', quotechar='<')
            for row in reader:
                items.append(row)
        items.pop(0) #removes header
        
        cr = Crossref()
        dois = items.copy()
        # link titles with dois
        for ii,item in enumerate(items):
            # goes thru all the papers and checks via crossref
            query_result = cr.works(query = item[2] + ' ' + item[3],limit=3)
            
            title = query_result['message']['items'][0]['title'][0]
            doi = query_result['message']['items'][0]['DOI']
            print(title)
            print(doi)
            dois[ii] = doi
                
    return dois

def fetch_dois_from_crossref(records):
    cr = Crossref()
    dois = records.copy()
    
    # link titles with dois
    for ii,item in enumerate(records):
        # goes thru all the papers and checks via crossref
        query_result = cr.works(query = item[2] + ' ' + item[3],limit=3)

        title = query_result['message']['items'][0]['title'][0]
        doi = query_result['message']['items'][0]['DOI']
        print(title)
        print(doi)
        dois[ii] = doi


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


def download_papers(path,doi_or_title,seperator):

    prepare_folders()
    DOIs = load_data_from_csv(path,doi_or_title,seperator='|')
    download_from_scihub(DOIs,output_folder='papers',temp_folder='temp')
    clean_up()


if __name__ == "__main__":
	path = "Articles_P37916_0418_A5420.csv"
	download_papers(path,'title','|')