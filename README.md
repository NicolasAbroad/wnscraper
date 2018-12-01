# WNScraper

This is the source code for the WNScraper website. It is mainly composed of two parts: the website and the website scraper/epub generator.
So far, the website has been designed to turn the content of any web novel from the website https://ncode.syosetu.com/ into epub files, provided that the url for the novel is submitted to the website.
The epub files are generated per volume, with the options to download epub files individually, or everything contained in one big zip folder.


### Prerequisites
-	Python 3.7
- Ubuntu 16.04


### How to run in a local environment:
##### Set up a virtual environment
```
$ cd [ setup folder directory ]
$ python3 -m venv venv
```

##### Activate virtual environment
```
$ source venv/bin/activate 
```

##### Install the required modules
```
$ (venv) pip install -r requirements.txt
```

##### Deploy website to localhost:5000 (127.0.0.1:5000):
-	Set environment variables
```
$ (venv) export FLASK_APP=webapp.py
```
- Run the following for debug mode:
```
$ (venv) export FLASK_DEBUG=1
```
- Run
```
$ (venv) flask run
```


### How to change (adding / removing / modifying) the database models:
-	Change the database models (located in ./app/models.py)
-	Generate a script to modify the database while keeping the data contained in it:
```
$ (venv) flask db migrate
```
-	Apply the script to the database:
```
$ (venv) flask db upgrade
```


### How to modify languages and translations on website:
-	Adding a new language:
```
$ (venv) flask translate init [ language ]
```
-	Modifying the translations:
-	Wrap text to translate with _(‘ ’)
-	Update the translation file:
```
$ (venv) flask translate upgrade
```
-	Translate the strings contained in ./app/translations/[ language ]/LC_MESSAGES/messages.po
```
Enter the translation for msgid in msgstr
#: app/forms.py:10 app/forms.py:18
msgid "Password"
msgstr "パスワード"
```
-	Compile the strings (which will be automatically used for translations):
```
$ (venv) flask translate compile
```
