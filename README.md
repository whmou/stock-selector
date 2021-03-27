# stock-selector

## prerequisites
1. ```$ pip install pandas pandas_datareader numpy```
2. change the WORKING_FOLDER_PATH in low_price_scanner.py to the folder you clone this project.
3. change the DATA_FOLDER in statement_dog_parser.py to the folder you clone this project.
4. make sure TICKER_LIST_FILE is in the WORKING_FOLDER_PATH.
5. for 財報狗 parser, please ensure that you are a member and you've unlocked the functions "你可以使用的健診幫手 (4/4)"

## Run
### 1. For the Low Price Scanner:
```
$ python3 low_price_scanner.py
```

output file will be in the `WORKING_FOLDER_PATH/dog_health_chk.txt`


### 2. For the StatementDog Parser:
after finish running low_price_scanner.py,
make sure `dog_health_chk.txt` is in the DATA_FOLDER.
```
$ python3 statemen_dogparser.py
```
- headless chrome window open up, login manually, then press enter in the command line.
- result file will be `dog_filter.txt` in the DATA_FOLDER.

