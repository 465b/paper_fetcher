import pandas as pd

def load_data_from_csv(path):
	data = pd.read_csv(path)

	try:
		stack = zip(data['Title'],data['DOI'])

		for item in stack:
			record = {"title": item[0],"doi": item[1]}
			yield record
			
	except:
		stack = zip(data['Title'],data['Authors'],data['Journal'],data['Abstract'])
	
		for item in stack:
			record = {"title": item[0],"authors": item[1],
					"journal": item[2],"abstract": item[3]}
			yield record