from pyhunter import PyHunter
import json
import pprint

hunter = PyHunter('a6498ae6a4371fd85d51cbfd9d8f8892b1b6f402')

domain_search = hunter.domain_search('cokodive.com')

domain_search_o = hunter.domain_search(company='Instagram', limit=5, offset=2, emails_type='personal')

pprint.pprint(domain_search)

