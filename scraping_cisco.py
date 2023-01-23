import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import file
import testim 

class Scraper:
    def __init__(self, username: str, password: str, path: str):
        self.username = username
        self.password = password
        self.path = path
        self.driver = webdriver.Chrome(path)
        self.category_links=[]
        self.links = []
        self.category_names=[]
        self.json_file = {}
        self.count=0
        self.array=[]
        
    def connect(self, url: str):
        try:
            self.driver.get(url)
            time.sleep(2)
        except TimeoutException:
            print('new connection try')
            self.driver.get(url)
            time.sleep(2)
            
    def get_links_from_one_page(self):
        """
        To collect links for each product  from one page with category names
        """
        
        try:
            element=WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'tr')))
            elements = element.find_elements(By.TAG_NAME, 'a')
          
        except:
            print("Faild to get links from first page")
            
        for e in elements:# this loop get all the webpages link and store into 'category_links' list.
            self.category_links.append(e.get_attribute('href'))
                
        return self.category_links
    
    def get_all_links(self):
        
        if(self.driver.find_elements(By.CSS_SELECTOR,'a.link-url')):
            elements = self.driver.find_elements(By.CSS_SELECTOR,'a.link-url')
            for elem in elements:
                href = elem.get_attribute('href')
                self.links.append(href)
        if(self.driver.find_elements(By.XPATH,'//*[@id="prodByAlpha"]/li[*]/a')):      
            a=self.driver.find_elements(By.XPATH,'//*[@id="prodByAlpha"]/li[*]/a')
            for a_z_elem in a:
                href = a_z_elem.get_attribute('href')
                self.links.append(href)
        if(self.driver.find_elements(By.CLASS_NAME,'modelitem_product')):
            d=self.driver.find_elements(By.CLASS_NAME,'modelitem_product')
            for i in d:
                href = i.get_attribute('href')
                self.links.append(href)
        if(self.driver.find_element(By.CLASS_NAME,'col')):
            self.driver.find_elements(By.CLASS_NAME,'col')
            d=self.driver.find_elements(By.XPATH,'//*[@id="fw-content"]/div[2]/div[2]/div[3]/ul/li[*]/a')
            for i in d:
                href = i.get_attribute('href')
                self.links.append(href)     
        else:
            print("Cannot scrap product link")
    
               
    def unix_path(self,l):#add backslash to path 
        """
        change the string to unix path with backslash
        """
        string=l
        newstr=""
        for i in range (len(string)-1):
            
            if(string[i].isupper() and  not string[i-1].isspace() 
            and not string[i+1].isupper()
            and not string[i-1]=="(" 
            and not string[i+1].isspace()
            
            ):
                
                newstr +="/"
                newstr+=string[i]
            
            else:
                newstr+=string[i]
        
        newstr+=string[i+1]
        return newstr
    
    def find_product_category(self):
        try:
            
            self.json_file.update({"Category":self.driver.find_element(By.XPATH,'//*[@id="fw-breadcrumb"]/ul/li[4]/a/span').text})
        except NoSuchElementException:
            try:
                self.json_file.update({"Category":self.driver.find_element(By.XPATH,'//*[@id="fw-breadcrumb"]/ul/li[3]/a').text})
            except NoSuchElementException:
                    print("Error finding element")
                    pass
                
                
    def update_json_file(self,url):
        l = self.driver.find_element(By.XPATH,'//*[@id="fw-breadcrumb"]/ul').text # this path not unix
        new_str = self.unix_path(l) #call function to change the path to unix path 
        self.json_file.update({'path':new_str})
        self.json_file.update({'url':url}) 
        if(self.driver.find_element(By.TAG_NAME,"h1").text):
            model=self.driver.find_element(By.TAG_NAME,"h1").text
            self.json_file.update({'Model':model})# dictionary method 'update'  add the key-value pair 'Model':model to the dictionary 'self.json_file'.
        else:
            print("Model name not exist no information to scraping")
        
   
    
        
    def insert_all_info(self):
        keys_list = [] #find elements with title and there detail and save as keys \values 
        values_list = []
        if(self.driver.find_elements(By.TAG_NAME, 'tr')):
                element = self.driver.find_elements(By.TAG_NAME, 'tr')
                for e in element:#loop the table row element
                    if(e.find_elements(By.TAG_NAME,'th')):#if element exist
                        elements=e.find_elements(By.TAG_NAME,'th')#find the keys to dictionary
                        
                        for i in elements:  #loop for save the keys of the product       
                            keys_list.append(i.text)
                            
                            #print("KEYD: ",i.text)
                        discription=e.find_elements(By.TAG_NAME,'td')#find the values to dictionary 
                        for y in discription:#loop for save the values of the product
                            values_list.append(y.text)
                            #print("Value: ",y.text)
                    else:
                        ("No product to scrap")
                for key, value in zip(keys_list, values_list):
                    if key=='Series Release Date' or key=='Release Date': 
                        self.json_file[key]=self.timeStemp(value)#format to timestamp from "13-NOV-2012"... 
                    elif key=='End-of-Sale Date':
                         self.json_file[key]=self.timeStemp(value)
                    elif key=='End-of-Support Date':
                         self.json_file[key]=self.timeStemp(value)
                    else :
                         self.json_file[key] = value
                        
                
                self.json_file.update(zip(keys_list,values_list))
                
                print("product number : ", self.count)             
        else:
            print("No product to scrap!")
       
                            
    def scraping_products(self,url):
        
        """scraping for product information"""
       # print("______Scraping _______\n")
        if(self.driver.find_elements(By.TAG_NAME, 'tr')):
            self.update_json_file(url)
            self.find_product_category()
            self.downloads_information()
            self.insert_all_info()              
            self.increment()       
            self.print_to_console()                          
            data={scraper.count: scraper.json_file}
            scraper.array.append(data)   
        else:
            print("No product to scrap!")     
            
             
    def print_to_console(self):
        """
        print model ,category and series
        """
        if "Model" in self.json_file:
            print("Model: ",self.json_file.get('Model'))
        if "Series" in self.json_file:
            print("Series : "+self.json_file.get('Series')) 
        if "Category" in self.json_file:
            print("Category :",self.json_file.get('Category'))  
        if"all" in self.json_file:
            print("all",self.json_file.get("all"))
        print("________________________________________") 
        
    def increment(self):
       
        self.count+=1
        
    def timeStemp(self, value: str):
        for a in value:
            if a.isspace():
                new_value = value.split(' ', 2)
                value = new_value[0]
        if not value[0].isdigit():
            new_value = value.split('-', 2)
            value = new_value[1]
            return value
        dt_format = datetime.strptime(value ,'%d-%b-%Y')
        return dt_format
    
    def downloads_information(self):
        """function to click the download button and find downloads link  """
       
        try:
            if(self.driver.find_element(By.XPATH, '//*[@id="drawertab-tab-downloads"]')):
                
                myElem = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button#drawertab-tab-downloads')))
                self.driver.execute_script("arguments[0].click();", myElem)
                #myElem.click()
            else: 
                print("There are no downloads for this product.")
                self.json_file.update({"all":"There are no downloads for this product."})
            try:
                if(self.driver.find_element(By.CSS_SELECTOR, 'a.download-all-releases')):
                    my_d=WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.download-all-releases')))
                    href = my_d.get_attribute('href')
                    self.json_file.update({"all":href})
                   
                else:
                    print("There are no downloads for this product.")
                    self.json_file.update({"all":"There are no downloads for this product."})
            except NoSuchElementException:

                self.json_file.update({"all":"There are no downloads for this product."})
               
        except (TimeoutException,NoSuchElementException):
            print("Loading took too much time!")
            
            
    def login(self):

        self.connect('https://cloudsso.cisco.com/as/authorization.oauth2?response_type=code&code_challenge=aJtIbmKJdguXMmRp941s7RfRY8jAd1KLiIMetowdIi8&code_challenge_method=S256&client_id=wam_prod_ac&redirect_uri=https%3A%2F%2Fwww.cisco.com%2Fpa%2Foidc%2Fcb&state=eyJ6aXAiOiJERUYiLCJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2Iiwia2lkIjoibVVtS0VmV2ctUmRtYjFkX1hWeUZIMWMza0c4Iiwic3VmZml4IjoicDRETEg3LjE2NzE4OTc0MTkifQ..NpLHYgZgs-qJHtf4Ykz_zg.ecP1CcHG8wDV9hASsrYvcxHKhdwjqxjZSfVUw-JWRwYBUP0j-TAdthlHWXbKJI15uG_wdo7eYQGTY3XCJkbgPP6N8JwJdIB1PuTBeoiDrOEK1o2hzvEj3GirJqe2hPYxJncepzW-X0GtDMb3kwumAX_nXokertfqOVMJtO1_tQo.ExirK3IYIrZhls2L9LOEQQ&nonce=H3qukgGFDPyvslTzXPRm9Sdm0mMegoTBSS-Y5ODZ5hk&acr_values=stdnomfa&scope=openid%20profile%20address%20email%20phone&vnd_pi_requested_resource=https%3A%2F%2Fwww.cisco.com%2Fcgi-bin%2Flogin&vnd_pi_application_name=CDCprod-www-cgi-bi')
        
        self.driver.find_element(By.XPATH, '//*[@id="userInput"]').send_keys(self.username)
        button=self.driver.find_element(By.XPATH,'//*[@id="login-button"]')
        button.click()
        time.sleep(15)
        self.driver.find_element(By.XPATH,'//*[@id="okta-signin-password"]').send_keys(self.password)
        login_button=self.driver.find_element(By.XPATH,'//*[@id="okta-signin-submit"]')
        login_button.click()
        time.sleep(5)
        

     
 
scraper = Scraper(username="christina0147@gmail.com", password="dW2P.QyVpv55.Uy", path="C:\Program Files (x86)\chromedriver.exe")
scraper.login()
scraper.connect("https://www.cisco.com/c/en/us/support/all-products.html")
product_links=scraper.get_links_from_one_page()
#'https://www.cisco.com/c/en/us/support/optical-networking/index.html'
"""product_links=[
            'https://www.cisco.com/c/en/us/support/data-center-analytics/index.html',
          
            ]"""
for u in product_links:
    scraper.connect(u)#load every webpage category link
    scraper.category_names.append(scraper.driver.find_element(By.ID,'fw-pagetitle').text)
    category_names=scraper.driver.find_element(By.ID,'fw-pagetitle').text
    scraper.get_all_links()
    

        
for i in scraper.links:#load all the products links and save products data
    print("\n")
    scraper.connect(i)
    scraper.scraping_products(i)
    
    
file.create_json_file(scraper.array)    
testim.test_fields()