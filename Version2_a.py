import requests,re,sys
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import itertools
from time import gmtime, strftime
date_Time = strftime("%Y%m%d_%H%M%S", gmtime())
# import pandas as pd
http_proxy  = "http://"
https_proxy  = "https://"

proxyDict = { 
              "http"  : http_proxy, 
              "https"  : https_proxy
            }
# proxies=proxyDict

file_name = "Adhoc_"+str(date_Time)+".csv"
print ("File name :",file_name)
def extract_CssData(selected_css,soupContent,cssCount):
    data = soupContent.select(selected_css)
    fdata = ''
    if data:
        fdata = data[0].get_text()
        fdata = fdata.strip()
        fdata = re.sub('\s+\s+',' ',fdata)
    try:
        print ("CSS value - {}: {}".format(cssCount+1,fdata))
    except:
        pass
    return fdata
    
def extract_RegxData(regxx, content, regexCount):
    content = str(content)
    # with open ('REG.html','w') as ff:
        # ff.write(content)
    # input("----")
    value = re.findall (regxx,content,re.I)
    if value: value = value[0]
    else: value = ''
    print ("Rex value - {}: {}".format(regexCount + 1,value))
    # input("----")
    return value
##### URL Check #####
def UrlCheck(url, HomeURL):
   if re.search(r'^http[^>]*?',url,re.I):
       print ("URL checked Successful ")   
   else:
       url=urljoin(HomeURL,url)   
   return url
   
##### Cleaning Data ####   
def clean(data):
    data = re.sub('\s+\s+',' ',data)
    return data
    
##### No Navigation Crawling #####
def singlePage(mainBlocks,dataCssList):
    output_list = []
    for block in mainBlocks:
        output = []
        for count,data_css in enumerate(dataCssList):
    
            print ("data_css :",data_css)
            subpage_data1 = extract_CssData(data_css,block,count)
            subpage_data1 = clean(subpage_data1)
            output.append(subpage_data1)
        output_list.append(output)
    return output_list
    
##### One Navigation Crawling ######
def twoPages(mainBlocks,firstPageTitleCss,secondPageLink,dataCssList,dataReglist,domin,page):
    output_list = []
    print ("two navigation")
    blockCounts = len(mainBlocks)
    print ("No of Blocks :",blockCounts)
    for count,i in enumerate(mainBlocks):
        output = []
        print (count+1," Out of ",blockCounts," Page - ",page)
        firstPageTitle = extract_CssData(firstPageTitleCss,i,count)
        output.append(firstPageTitle)
        subLink = [a['href'] for a in i.select(secondPageLink)]
        if subLink:
            subLink = subLink[0]
            subLink = UrlCheck (subLink, domin)
        else:
            print ("Please enter valid Sublink")
        print ("SUBLINK :",subLink)
        subLink = UrlCheck (subLink, domin)
        subPageResponse = requests.get(subLink,allow_redirects=True)
        print ("SUB RESPONSE :",subPageResponse)
        
        subPageContent = subPageResponse.content.decode('utf-8',errors = 'ignore')
        subPageSoup = BeautifulSoup(subPageContent, 'html.parser')
        for dataCssCount,data_css in enumerate(dataCssList):
            subpage_data1 =  extract_CssData(data_css,subPageSoup,dataCssCount)
            subpage_data1 = clean(subpage_data1)
            output.append(subpage_data1)
        for dataRegCount,dataReg in enumerate(dataReglist):
            subPageRegData = extract_RegxData(dataReg,subPageSoup,dataRegCount)
            # subPageRegData = clean(subPageRegData)
            output.append(subPageRegData)
            
        output_list.append(output)
        # output_list.append(firstPageTitle)
        
        # print ("Output_list",output_list)
        print ("==================================")
    return output_list

def collectCssList():
    n_datas = input("Entert the N datas :")
    dataCssList = []
    for current_data in range(int(n_datas)):
        css_value = input("Please enter Css / Regex:")
        dataCssList.append(css_value)
    return dataCssList
     
def dataCollection(mainUrl,mainBlocksCss,firstPageTitlecss,N_navPages,domin,secondPageLink,nextPageCss,dataCssList,dataReglist,page):
    pageResponse = requests.get(mainUrl,allow_redirects=True)
    print ("Page :",pageResponse)
    pageContent = pageResponse.content.decode('utf-8')
    
    soup = BeautifulSoup(pageContent, 'html.parser')
    mainBlocks = soup.select(mainBlocksCss)
    N_navPages = int(N_navPages)
    
    if N_navPages == 0:
        dataCssList = collectCssList()
        singleNavdata = singlePage(mainBlocks,dataCssList)
        # print ("Single Nav data :",singleNavdata)
        myDatas.append(singleNavdata)
    elif N_navPages == 1:
        
        print ("*********Enter Page 2 ******Css List ")
        if not dataCssList:
            dataCssList = collectCssList()
        twoNavdata = twoPages(mainBlocks,firstPageTitlecss,secondPageLink,dataCssList,dataReglist,domin,page)
        myDatas.append(twoNavdata)
    else:
        pass 
    NextPageLink = [a['href'] for a in soup.select(nextPageCss)]
    print ("NEXT link DATA:",NextPageLink)        
    # input("Check for data")
    return myDatas,pageContent,NextPageLink,dataCssList

if __name__ == '__main__':
    try: 
        dataCssList = ''
        mainUrl = input("Main Url :")
        mainBlocksCss = input("Blocks :")
        N_navPages = input ('No. of nav pages :')
        domin = input("Enter Domin :")
        secondPageLink = input("Enter Subpage Link :")
        myDatas = []
        nextPageCss = input ("Enter next Page Css: ")
        firstPageTitlecss = input("Enter first Page Title Css :")
        regx = input("Enter regex avialble (Y/N) :")
        if regx == 'Y':
            dataReglist = collectCssList()
        else:
            dataReglist = []
        print ("Next Page :",nextPageCss)
        page = 1
        while True: 
            print ("Page :",page)
            myDatas, PageContent,NextPageLink,dataCssList = dataCollection(mainUrl,mainBlocksCss,firstPageTitlecss,N_navPages,domin,secondPageLink,nextPageCss,dataCssList,dataReglist,page)
            if NextPageLink: 
                NextPageLink = NextPageLink[0]
                mainUrl = UrlCheck(NextPageLink,domin)
                print ("Next Page Nav Start")
            else:
                print ("**************End**************")
                break
            page += 1
            # myDatas.append(myData)
        print ("File name :",file_name)
        finaldata = list(itertools.chain.from_iterable(myDatas))
        percentile_list = pd.DataFrame(finaldata)
        percentile_list.to_csv(file_name)
    except Exception as e:
        print ("Ërror ::",e)