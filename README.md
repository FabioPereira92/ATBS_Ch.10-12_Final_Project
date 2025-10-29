# Price Tracker
A program that accepts a file path, from the command line, for a .txt file containing URLs, extracts product name, current price and availability from each URL and writes/updates an Excel workbook, in a path obtained from the command line, with the results. It also generates a log file with info, warnings and errors for each run and prints a final summary to the console.

## Features
- Scanning product name, current price and availability in URLs from a .txt file selected in the command line by the user.
- Writing/updating an excel workbook with the results in a path chosen in the command line by the user.
- Generating a log file with info, warnings and errors for each run.
- Printing a final summary to the console.
  
## How to run
1. Clone this repository or download the file `priceTracker.py`.
2. Run in terminal.

## Example Usage
### Example text file
![example text file](https://github.com/user-attachments/assets/f3da1ce2-baff-4509-b215-aa665d01a0c3)
### Content of one of the scanned URLs 
![content of one of the scanned URLs](https://github.com/user-attachments/assets/893c6af2-e7f1-4063-8c25-00467a5c924b)
### Content of the generated priceTrackerFolder
![content of the generated priceTrackerFolder](https://github.com/user-attachments/assets/a2fff273-ecb5-4022-9781-851f8373eb47)
### Content of one of the sheets of the generated excel file
![content of one of the sheets of the generated excel file](https://github.com/user-attachments/assets/41f180ef-add3-4eef-a398-5e2e0a893da4)
### Content of the generated logsTracker1 file
![content of the generated logsTracker1 file](https://github.com/user-attachments/assets/641cae06-de29-475c-9cdd-0d2a0ae4db3b)
### Final summary in the console
![final summary in the console](https://github.com/user-attachments/assets/6de2bcfb-6015-4377-bf07-02e2145a4ebe)

## Tech Stack
- Python 3.13
- Standard library only (logging, shelve, os, sys, requests, bs4, openpyxl, datetime)

## License
MIT
