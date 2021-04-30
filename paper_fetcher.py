import os
import csv
import time

import numpy as np
from habanero import Crossref
from scidownl.scihub import SciHub
from termcolor import colored

from xml_reader import load_data_from_xml
from csv_reader import load_data_from_csv


STD_INFO = colored('[INFO] ', 'green')
STD_ERROR = colored('[ERROR] ', 'red')
STD_WARNING = colored('[WARNING] ', 'yellow')
STD_INPUT = colored('[INPUT] ', 'blue')


def prepare_folders(output_folder='papers',mismatch_folder='mismatch',
					temp_folder='temp'):

	try:
		os.mkdir(output_folder)
	except FileExistsError:
		pass

	try:
		os.mkdir(mismatch_folder)
	except FileExistsError:
		pass

	try:
		os.mkdir(temp_folder)
	except FileExistsError:
		files = os.listdir(temp_folder)
		for file in files:
			os.remove(os.path.join(temp_folder,file))
			
	return output_folder
			
			
def flatten(list_of_strings):
	if type(list_of_strings) == list:
		string = ""
		for item in list_of_strings:
			string += " "+item
		return string
	else:
		return list_of_strings


def fetch_doi_from_crossref(item):
	""" link titles with dois """
	cr = Crossref()
	

	# goes thru all the papers and checks via crossref
	query = '"' + item["title"] + '"'\
	+ " " + flatten(item["authors"])
	print(STD_INFO + query)
	server_reached = False
	while server_reached == False:
		try:
			query_result = cr.works(query = query,limit=3)
			server_reached = True
		except:
			#HTTPError (Service Unavailable)
			print(STD_WARNING + "CrossRef server unavailable. Retry in 5 seconds")
			time.sleep(5)

	title = query_result['message']['items'][0]['title'][0]
	doi = query_result['message']['items'][0]['DOI']
	return doi,title


def download_from_scihub(item,naming_scheme='doi',
						 output_folder='papers',temp_folder='temp'):

	doi = item['doi']
	try:
		SciHub(doi,temp_folder).download(choose_scihub_url_index=3)
		path = os.getcwd()
		filenames = os.listdir(os.path.join(path,temp_folder))
		if naming_scheme == 'doi':
			for filename in filenames:
				os.rename(os.path.join(path,temp_folder, filename),
					os.path.join(path,output_folder,doi.replace('/','_')))
		elif naming_scheme =='title':
			for filename in filenames:
				os.rename(os.path.join(path,temp_folder, filename),
					os.path.join(path,output_folder,item['title']))
		return 0
	
	except AttributeError:
		print(f'{STD_WARNING} Paper {doi} not found.')
		return 404

	except KeyError:
		print(doi+" available on libgen")
		return 101


def comparte_titles(data_title,query_title,verbose=True):
	if data_title == query_title:
		if verbose == True:
			print(STD_INFO + "Successfull crossref lookup. Titles match")
		return 0
	else:
		if verbose == True:
			print(STD_WARNING + "Crossref lookup failed. Titles not matched")
		return 1


def clean_up(temp_folder='temp'):
	try:
		os.rmdir(temp_folder)
	except:
		pass


def load_data(path):
	if path[-3:] == 'xml':
		record = load_data_from_xml(path)
	elif path[-3:] == 'csv':
		record = load_data_from_csv(path)
	return record


def download_papers(path,naming_scheme='doi',force_download=False,
					output_folder='papers',mismatch_folder='mismatch',
					temp_folder='temp'):

	successful_lookups = []
	unsuccessful_lookups = []
	
	prepare_folders(output_folder,mismatch_folder,temp_folder)

	record = load_data(path)
	
	for ii,item in enumerate(record):
		print(STD_INFO + colored('#'+str(ii), attrs=['bold']))
		
		item['doi'],item['cr_title'] = fetch_doi_from_crossref(item)
		item['cr_output_code'] = comparte_titles(item['title'],item['cr_title'])
		
		if item['cr_output_code'] == 0:
			# doi found - trying to fetch from scihub
			scihub_output_code = download_from_scihub(item,naming_scheme,
													output_folder,temp_folder)
			
			if scihub_output_code == 0:
				successful_lookups.append({'title': item['title']})
			else:
				unsuccessful_lookups.append({'error': 'SciHub',
											'title': item['title']})
		
		if item['cr_output_code'] == 1:
			if force_download == False:
			# doi not found - skipping download attempt
				unsuccessful_lookups.append({'error': 'CrossRef',
											 'title': item['title']})
			else:	
				scihub_output_code = \
					download_from_scihub(item,naming_scheme,
						output_folder=mismatch_folder,temp_folder=temp_folder)
											
				if scihub_output_code == 0:
					successful_lookups.append({'title': item['title']})
				else:
					unsuccessful_lookups.append({'error': 'SciHub',
												'title': item['title']})

	with open('unsuccessful_lookups.csv','w') as g:
		write = csv.writer(g)
		for item in unsuccessful_lookups:
			write.writerow([item['error']+', '+item['title']])
	
	clean_up()



if __name__ == "__main__":
	path = "demo_data/Articles_P37916_0430_A5795.csv"
	download_papers(path,naming_scheme='title',force_download=True)