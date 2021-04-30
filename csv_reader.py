import pandas as pd

def load_data_from_csv(path):
	data = pd.read_csv(path)
	stack = zip(data['Title'],data['Authors'],data['Journal'])
	
	for item in stack:
		record = {"title": item[0],"authors": item[1],"journal": item[2]}
		yield record