#! python3

"""priceTracker.py - A program that accepts a file path, from the command line, for a .txt
file containing URLs, extracts product name, current price and availabaility from each
URL and writes/updates an Excel workbook, in a path obtained from the command line, with
the results. It also generates a log file with info, warnings and errors for each run."""

import logging, shelve, os, sys, requests, bs4, openpyxl
from datetime import datetime

# Creating the folder structure where log files and the excel file will be stored
if len(sys.argv) < 3:
    print('Please enter the name of the URLs text file and the path to the excel file in ' +
          'the command line.')
    sys.exit()
os.makedirs(os.path.join('.', sys.argv[2], 'logs'), exist_ok=True)

# Creating a shelf file to count the runs
shelfFile = shelve.open(os.path.join('.', sys.argv[2], 'runCounterFile'))
if 'runCounter' not in shelfFile:
    shelfFile['runCounter'] = 1
else:
    shelfFile['runCounter'] += 1
    
# Configuring logging
logging.basicConfig(filename=os.path.join
                    ('.', sys.argv[2], 'logs', 'logsTracker' + str(
                        shelfFile['runCounter']) + '.log'), level=logging.INFO,
                     format=' %(asctime)s - %(levelname)s - %(message)s')

logging.info('Start of program')
errors = []

# Reading and saving the content of the URLs text file with text file name validation
try:
    urlsFileObj = open(sys.argv[1])
except FileNotFoundError:
    logging.error('URLs text file not found!')
    errors.append('URLs text file not found')
    print(sys.argv[1] + ' doesn\'t exist! Enter a valid file name: ')
    while True:
        try:            
            urlFileName = input()
            urlsFileObj = open(urlFileName)
            break
        except FileNotFoundError:
            logging.error('URLs text file not found')
            errors.append('URLs text file not found!')
            print(urlFileName + ' doesn\'t exit! Enter a valid file name: ')
            continue
urlsList = urlsFileObj.readlines()
urlsFileObj.close()
logging.info('URLs text file read. Total number of URLs = ' + str(len(urlsList)))
for i in range(len(urlsList)):
    if urlsList[i].endswith('\n'):
        urlsList[i] = urlsList[i][:-1]
    logging.info('URL number ' + str(i + 1) + ': ' + urlsList[i])

# Scraping each URL
productNamesList = []
pricesList = []
availabilityList = []
for i in range(len(urlsList)):
    res = requests.get(urlsList[i])
    try:
        res.raise_for_status()
    except Exception as err:
        logging.error(err)
        errors.append('404 Client Error')
        productNamesList.append('URL not found')
        pricesList.append('URL not found')
        availabilityList.append('URL not found')
        continue
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    
    # Finding and extracting the product name
    productNameElem = soup.select('h1')
    if productNameElem != []:
        productNamesList.append(productNameElem[0].getText().strip())
        logging.info('Product named "' + productNamesList[i] + '" found in URL ' +
                     urlsList[i])
    else:
        try:
            raise Exception('Product name not found in URL ' + urlsList[i])
        except Exception as err:
            productNamesList.append('Unknown')
            logging.warning(err)       
    
    # Finding and extracting the price
    priceElem = soup.select('.price_color')
    if priceElem != []:
        assert priceElem[0].getText().strip()[2:-3].isdecimal() and \
               priceElem[0].getText().strip()[-2:].isdecimal(), 'Price is not a number'
        pricesList.append(priceElem[0].getText().strip()[1:])
        logging.info('Price ' + pricesList[i] + ' found in URL ' + urlsList[i])
    else:
        try:
            raise Exception('Price not found in URL ' + urlsList[i])
        except Exception as err:
            pricesList.append('Unknown')
            logging.warning(err)

    # Finding and extracting the availability
    availabilityElem = soup.select('.instock.availability')
    if availabilityElem != []:
        availabilityList.append(availabilityElem[0].getText().strip())
        logging.info('Availability "' + availabilityList[i] + '" found in URL ' +
                     urlsList[i])
    else:
        try:
            raise Exception('Availability not found in URL ' + urlsList[i])
        except Exception as err:       
            availabilityList.append('Unknown')
            logging.warning('Availability not found in URL ' + urlsList[i])

# Writing/Updating excel
if os.path.exists(os.path.join('.', sys.argv[2], 'priceTracker.xlsx')):
    wb = openpyxl.load_workbook(os.path.join('.', sys.argv[2], 'priceTracker.xlsx'))
    logging.info('Excel file priceTracker.xlsx opened')
    sheet1 = wb['Products']
    sheet2 = wb['History']
# Creating new excel file, sheets, headings and formating
else:
    wb = openpyxl.Workbook()
    logging.info('Excel file priceTracker.xlsx created')
    sheet1 = wb.active
    sheet1.title = 'Products'
    wb.create_sheet(index=1, title='History')
    sheet1['A1'] = 'URL'
    sheet1['B1'] = 'PRODUCT NAME'
    sheet1['C1'] = 'FIRST SEEN'
    sheet1['D1'] = 'LAST SEEN'
    sheet1['E1'] = 'LAST KNOWN PRICE'
    sheet1['F1'] = 'CURRENCY'
    sheet1['G1'] = 'LAST KNOWN STATUS'
    sheet1['H1'] = 'LAST KNOWN QTY IN STOCK'
    sheet1.freeze_panes = 'A2'
    sheet1.column_dimensions['A'].width = 80
    sheet1.column_dimensions['B'].width = 35
    sheet1.column_dimensions['C'].width = 20
    sheet1.column_dimensions['D'].width = 20
    sheet1.column_dimensions['E'].width = 20
    sheet1.column_dimensions['F'].width = 10
    sheet1.column_dimensions['G'].width = 20
    sheet1.column_dimensions['H'].width = 25
    sheet2 = wb['History']
    sheet2['A1'] = 'TIMESTAMP'
    sheet2['B1'] = 'URL'
    sheet2['C1'] = 'PRICE'
    sheet2['D1'] = 'CURRENCY'
    sheet2['E1'] = 'STATUS'
    sheet2['F1'] = 'QTY IN STOCK'
    sheet2['G1'] = 'RUN ID'
    sheet2.freeze_panes = 'A2'
    sheet2.column_dimensions['A'].width = 20
    sheet2.column_dimensions['B'].width = 80
    sheet2.column_dimensions['C'].width = 10
    sheet2.column_dimensions['D'].width = 10
    sheet2.column_dimensions['E'].width = 10
    sheet2.column_dimensions['F'].width = 15
    sheet2.column_dimensions['G'].width = 10

# Filling the cells with the scraped data
logging.info('Writing/updating the excel file')
excelUrlsList = []

for i in sheet1['A']:
     excelUrlsList.append(i.value)

productsCounter = 0
productsAddedList = []
productsUpdatedList = []

for i in range(len(urlsList)):
    if urlsList[i] not in excelUrlsList:
        productsCounter += 1
        sheet1.cell(row=sheet1.max_row+1,column=1).value = urlsList[i]          
        sheet1.cell(row=sheet1.max_row,column=2).value = productNamesList[i]
        sheet1.cell(row=sheet1.max_row,column=3).value = datetime.now()
        sheet1.cell(row=sheet1.max_row,column=4).value = datetime.now()
        if pricesList[i] == 'Unknown':
            sheet1.cell(row=sheet1.max_row,column=5).value = pricesList[i]
            sheet1.cell(row=sheet1.max_row,column=6).value = pricesList[i]
        else:
            sheet1.cell(row=sheet1.max_row,column=5).value = pricesList[i][1:]
            sheet1.cell(row=sheet1.max_row,column=6).value = pricesList[i][0]
        if availabilityList[i] == 'Unknown':
            sheet1.cell(row=sheet1.max_row,column=7).value = availabilityList[i]
            sheet1.cell(row=sheet1.max_row,column=8).value = availabilityList[i]
        else:
            sheet1.cell(row=sheet1.max_row,column=7).value = availabilityList[i][:8]
            sheet1.cell(row=sheet1.max_row,column=8).value = availabilityList[i][10:12]
        productsAddedList.append(productNamesList[i])       
    else:
        productsUpdatedList.append(productNamesList[i])
        for j in range(len(excelUrlsList)):
            if excelUrlsList[j] == urlsList[i]:
                sheet1.cell(row=j+1,column=4).value = datetime.now()
                if pricesList[i] == 'Unknown':
                    sheet1.cell(row=j+1,column=5).value = pricesList[i]
                    sheet1.cell(row=j+1,column=6).value = pricesList[i]
                else:
                    sheet1.cell(row=j+1,column=5).value = pricesList[i][1:]
                    sheet1.cell(row=j+1,column=6).value = pricesList[i][0]
                if availabilityList[i] == 'Unknown':
                    sheet1.cell(row=j+1,column=7).value = availabilityList[i]
                    sheet1.cell(row=j+1,column=8).value = availabilityList[i]
                else:
                    sheet1.cell(row=j+1,column=7).value = availabilityList[i][:8]
                    sheet1.cell(row=j+1,column=8).value = availabilityList[i][10:12]
    sheet2.cell(row=sheet2.max_row+1,column=1).value = datetime.now()
    sheet2.cell(row=sheet2.max_row,column=2).value = urlsList[i]
    if pricesList[i] == 'Unknown':
        sheet2.cell(row=sheet2.max_row,column=3).value = pricesList[i]
        sheet2.cell(row=sheet2.max_row,column=4).value = pricesList[i]
    else:
        sheet2.cell(row=sheet2.max_row,column=3).value = pricesList[i][1:]
        sheet2.cell(row=sheet2.max_row,column=4).value = pricesList[i][0]
    if availabilityList[i] == 'Unknown':
        sheet2.cell(row=sheet2.max_row,column=5).value = availabilityList[i]
        sheet2.cell(row=sheet2.max_row,column=6).value = availabilityList[i]
    else:
        sheet2.cell(row=sheet2.max_row,column=5).value = availabilityList[i][:8]
        sheet2.cell(row=sheet2.max_row,column=6).value = availabilityList[i][10:12]
    sheet2.cell(row=sheet2.max_row,column=7).value = shelfFile['runCounter']

# Logging excel updates and saving the workbook
logging.info(str(productsCounter) +
             ' rows added to the "Products" sheet in priceTracker.xlsx')
logging.info(str(len(urlsList) - productsCounter) +
             ' rows updated in the "Products" sheet in priceTracker.xlsx')
logging.info(str(len(urlsList)) + ' rows added to the "History" sheet in priceTracker.xlsx')
wb.save(os.path.join('.', sys.argv[2], 'priceTracker.xlsx'))

# Final summary in the console and log file
print('FINAL SUMMARY')
logging.info('FINAL SUMMARY')
print('Total URLs processed: ' + str(len(urlsList)))
logging.info('Total URLs processed: ' + str(len(urlsList)))
if productsAddedList != []:
    print('New products added:')
    logging.info('New products added:')
    for i in productsAddedList:
        print('   - ' + i)
        logging.info('   - ' + i)
if productsUpdatedList != []:        
    print('Existing products updated:')
    logging.info('Existing products updated:')
    for i in productsUpdatedList:
        print('   - ' + i)
        logging.info('   - ' + i)
if errors != []:
    print('Errors found:')
    logging.info('Errors found:')
    for i in errors:
        print('   - ' + i)
        logging.info('   - ' + i)
print('Path to the Excel file: ' + os.path.abspath
      (os.path.join('.', sys.argv[2], 'priceTracker.xlsx')))
logging.info('Path to the Excel file: ' + os.path.abspath
      (os.path.join('.', sys.argv[2], 'priceTracker.xlsx')))
print('Path to the log file: ' + os.path.abspath
      (os.path.join('.', sys.argv[2], 'logs', 'logsTracker' +
                    str(shelfFile['runCounter']) + '.log')))
logging.info('Path to the log file: ' + os.path.abspath
      (os.path.join('.', sys.argv[2], 'logs', 'logsTracker' +
                    str(shelfFile['runCounter']) + '.log')))
shelfFile.close()
logging.info('End of program')
