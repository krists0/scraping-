import unittest
from scraping_cisco import Scraper
import requests
import file
import json
import jsonschema
class ScraperTest(unittest.TestCase):
   
    
    def setUp(self):
        with open('Output2copy.json') as json_f:
            self.data = json.load(json_f)
        print("typeof self.data",type(self.data))
        print(self.data)
    
    def test_category(self):
        for product in self.data:
            for key in product:
                self.assertEqual(product[key]['Category'], "Optical Networking")

   
    def test_path_format(self):
        for product in self.data:
            for key in product:
                path = product[key]['path']
                print("product:",product)
                print("key in product:",key)
                self.assertTrue(path.startswith('/'), "Path does not start with /")
                self.assertFalse('\\' in path, "Path contains a backslash, should use forward slashes")

    def test_url(self):
        for product in self.data:
            for key in product:
                try:
                    response = requests.get(product[key]['url'])
                    self.assertEqual(response.status_code, 200)
                except (requests.exceptions.InvalidURL,requests.exceptions.InvalidSchema) as e:
                    print(f"Error: {e}")
                
                
                
if __name__ == '__main__':
    
    unittest.main()
    
    
   