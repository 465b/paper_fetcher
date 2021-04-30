import xml.etree.ElementTree as ET

def load_data_from_xml(path):
	tree = ET.parse(path)
	root = tree.getroot()

	data = fetch_entry_in_xml(root)
	for ii,entry in enumerate(data):
		title = fetch_titles_from_xml(entry)
		authors = fetch_authors_from_xml(entry)
		journal = fetch_journal_from_xml(entry)
		yield {"title": title,"authors": authors,"journal": journal}


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