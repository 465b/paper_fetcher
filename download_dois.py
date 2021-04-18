from scidownl.scihub import SciHub
import numpy as np
import os
import csv

def download_dois(path):
	
	output_folder = 'papers'
	temp_folder = 'temp'

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
	
	with open(path) as f:
		DOIs = f.read().splitlines()
	
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

if __name__ == "__main__":
	download_dois('dois.csv')