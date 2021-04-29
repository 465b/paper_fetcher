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
	for ii,entry in enumerate(data):
		title = fetch_titles_from_xml(entry)
		authors = fetch_authors_from_xml(entry)
		journal = fetch_journal_from_xml(entry)
		yield {"title": title,"authors": authors,"journal": journal}


def fetch_doi_from_crossref(item):
	cr = Crossref()
	
	# link titles with dois

	# goes thru all the papers and checks via crossref
	query = '"' + item["title"] + '"'\
	+ " " + flatten(item["authors"])
	print(query)
	query_result = cr.works(query = query,limit=3)

	title = query_result['message']['items'][0]['title'][0]
	doi = query_result['message']['items'][0]['DOI']
	print(title)
	print(doi)
	return doi


def download_from_scihub(doi,output_folder='papers',temp_folder='temp',
						 naming_scheme='doi'):
	try:
		SciHub(doi,temp_folder).download(choose_scihub_url_index=3)
		path = os.getcwd()
		filenames = os.listdir(os.path.join(path,temp_folder))
		if naming_scheme == 'doi':
			for filename in filenames:
				os.rename(os.path.join(path,temp_folder, filename),
				os.path.join(path,output_folder,doi.replace('/','_')))
		elif naming_scheme =='title':
			pass
		return 0,doi
	
	except AttributeError:
		print(f'----------------------')
		print(f'[INFO] Paper {doi} not found.')
		print(f'----------------------')
		return 404,doi

	except KeyError:
		print(doi+" available on libgen")
		return 101,doi



def clean_up(temp_folder='temp'):
	try:
		os.rmdir(temp_folder)
	except:
		pass


def download_papers(path,naming_scheme='doi'):

	scihub_invalid_dois = []
	scihub_valid_dois = []
	
	prepare_folders()
	record = load_data_from_xml(path)
	for item in record:
		doi = fetch_doi_from_crossref(item)
		output_code, doi = download_from_scihub(doi)
		if output_code == 0:
			scihub_valid_dois.append(doi)
		else:
			scihub_invalid_dois.append(doi)
		
	with open('invalid_dois.csv','w') as g:
		write = csv.writer(g)
		write.writerows([scihub_invalid_dois])
	
	clean_up()


if __name__ == "__main__":
	path = "Articles_P37916_0421_A5483.xml"
	download_papers(path,naming_scheme='title')