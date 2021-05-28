import os
import csv
import time
import string
from difflib import SequenceMatcher

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


#def slugify(value, allow_unicode=False):
#    """
#    Taken from https://github.com/django/django/blob/master/django/utils/text.py
#    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
#    dashes to single dashes. Remove characters that aren't alphanumerics,
#    underscores, or hyphens. Convert to lowercase. Also strip leading and
#    trailing whitespace, dashes, and underscores.
#    """
#    value = str(value)
#    if allow_unicode:
#        value = unicodedata.normalize('NFKC', value)
#    else:
#        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
#    value = re.sub(r'[^\w\s-]', '', value.lower())
#    return re.sub(r'[-\s]+', '-', value).strip('-_')




def prepare_folders(output_path,output_folder='papers',mismatch_folder='mismatch',
					temp_folder='temp'):

	try:
		os.mkdir(os.path.join(output_path,output_folder))
	except FileExistsError:
		pass

	try:
		os.mkdir(os.path.join(output_path,mismatch_folder))
	except FileExistsError:
		pass

	try:
		os.mkdir(os.path.join(output_path,temp_folder))
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
	try:
		query = '"' + item["title"] + '"'\
		+ " " + flatten(item["authors"])
	except TypeError:
		# No author information available (probably)
		query = '"' + item["title"] + '"'

	
	
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

	try:
		title = query_result['message']['items'][0]['title'][0]
	except KeyError:
		title = 'None'
	
	doi = query_result['message']['items'][0]['DOI']
	return doi,title


def download_from_scihub(item,path,export_naming_scheme='doi',
						 output_folder='papers',temp_folder='temp'):

	doi = item['doi']
	temp = os.path.join(path,temp_folder)
	output = os.path.join(path,output_folder)
	server_reached = False
	while server_reached == False:
		try:
			SciHub(doi,temp).download(choose_scihub_url_index=3)
			
			filenames = os.listdir(temp)
			if export_naming_scheme == 'doi':
				for filename in filenames:
					os.rename(os.path.join(temp,filename),
							  os.path.join(output,doi.replace('/','_'))+'.pdf')
			elif export_naming_scheme =='title':
				for filename in filenames:
					os.rename(os.path.join(temp,filename),
						os.path.join(output_folder,item['title'].replace('/','_'))
						+'.pdf')
			return 0
		
		except AttributeError as identifier:
			server_reached = True
			print(f'{STD_WARNING} Paper {doi} not found.')
			return 1

		except KeyError as identifier:
			if identifier.args[0] == 'cache-control':
				print(STD_WARNING + 'SciHub server not reached. Retrying...')
				time.sleep(5)
			else:
				server_reached = True
				print(f'{STD_WARNING} Paper {doi} not found.')
				print(STD_WARNING + doi+" available on libgen")
				return 2
		
		except ConnectionError as identifier:
			print(STD_WARNING + 'SciHub server not reached. Retrying...')
			time.sleep(5)
		


def prepare_titles_to_compare(title):
	title = title.lower()
	title = "".join(title.split())
	punctuation = string.punctuation+'–'
	title = "".join([char for char in title if char not in punctuation])

	return title


def string_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def comparte_titles(data_title,query_title,verbose=True,similarity_threshold=0.9):

	data_title = prepare_titles_to_compare(data_title)
	query_title = prepare_titles_to_compare(query_title)

	if data_title == query_title:
		if verbose == True:
			print(STD_INFO + "Successfull crossref lookup. Titles match")
		return 0
	else:
		similarity = string_similarity(data_title,query_title)
		if similarity > similarity_threshold:
			print(STD_INFO + "Successfull crossref lookup. Titles similarity"
				  +str(similarity))
			return 0
		if verbose == True:
			print(STD_WARNING + "Crossref lookup failed. Title mismatch " 
				  + str(1-similarity))
			print(data_title); print(query_title)
		return 1-similarity


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


def download_papers(path,output_path=None,
					export_naming_scheme='doi', import_naming_scheme='title',
					force_download=False, output_folder='match',
					mismatch_folder='mismatch', temp_folder='temp'):

	if output_path is None:
		output_path = os.getcwd()
	#prepare folder structure for file storage and renaming
	prepare_folders(output_path,output_folder,mismatch_folder,temp_folder)

	
	# load the data set containting the papers which shall be downloaded
	record = load_data(path)

	for ii,item in enumerate(record):
		print(STD_INFO + colored('#'+str(ii), attrs=['bold']))

		# logging
		f = open('full_log.csv','a')
		log = csv.writer(f)

		if import_naming_scheme == 'title':

			try:
				item['doi'],item['cr_title'] = fetch_doi_from_crossref(item)

				# this is a very basic way to check if the papers match
				# doesn't work (when it should) e.g if any special characters are present
				item['cr_output_code'] = comparte_titles(item['title'],item['cr_title'])

				if item['cr_output_code'] == 0:
					# doi found - trying to fetch from scihub
					item['scihub_output_code'] = \
						download_from_scihub(item,output_path,export_naming_scheme,
											output_folder,temp_folder)
					log.writerow([ii,'CrossRef','success',item['title'],
								item['authors'],item['journal'],
								item['abstract']])

					# writes down that paper couldn't be downloaded
					if item['scihub_output_code'] != 0:
						log.writerow([ii,'SciHub','error',item['title'],
									item['authors'],item['journal'],
									item['abstract']])
					else:
						log.writerow([ii,'SciHub','success',item['title'],
									item['authors'],item['journal'],
									item['abstract']])

				if item['cr_output_code'] != 0:
					# writes down that paper wasn't found on crossref
					log.writerow([ii,'CrossRef','error',item['title'],
								item['authors'],item['journal'],
								item['abstract']])
					if force_download == True:
						item['scihub_output_code'] = \
							download_from_scihub(item,output_path,export_naming_scheme,
												output_folder=mismatch_folder,
												temp_folder=temp_folder)

						# writes down that paper couldn't be downloaded
						if item['scihub_output_code'] != 0:
							log.writerow([ii,'SciHub','error',item['title'],
								item['authors'],item['journal'],
								item['abstract']])
						else:
							log.writerow([ii,'SciHub','success',item['title'],
								item['authors'],item['journal'],
								item['abstract']])
					else:	
						# doi not found - skipping download attempt
						pass

			except TypeError as identifier:
				# Handles corrupt items in input data
				print(STD_WARNING + "Corrupted data line. Logged.")
				print(STD_WARNING + identifier)
				log.writerow(ii,'Corrupt Data',' ')

				f.close()

		elif import_naming_scheme == 'doi':
			item['scihub_output_code'] = \
						download_from_scihub(item,output_path,export_naming_scheme,
											output_folder,temp_folder)
			# writes down that paper couldn't be downloaded
			if item['scihub_output_code'] != 0:
				log.writerow([ii,'SciHub','error',item['title'],
							item['authors'],item['journal'],
							item['abstract']])
			else:
				log.writerow([ii,'SciHub','success',item['title'],
							item['authors'],item['journal'],
							item['abstract']])

	clean_up()



if __name__ == "__main__":
	path = "demo_data/third_test.csv"
	download_papers(path,export_naming_scheme='title',force_download=True)
