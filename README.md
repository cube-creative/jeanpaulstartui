# jeanpaulstartui

PySide client for Jean-Paul Start

![](jeanpaulstartui.jpg)

## Setup

* Create a new virtual environment with: `virtualenv -p path\to\python27.exe <venv-name>`.
  
* Active the virtual environnement with: `<venv-name>\Scripts\activate` on Windows, or `<venv-name>/bin/activate` on Unix or Mac.
  
* Upgrade pip installation: `python -m pip install --upgrade pip`

* Install dependencies: `pip install -r requirements.txt`

* Rename *.env.sample* file as *.env*, and fill variables on it.

* Load all environment variable in the *.env* file.

* Set autoarbo folder into the PYTHONPATH variable. (I'll move `__main__.py` in the future to avoid this step).

* Finally execute the application: `python ./jeanpaulstratui/__main__.py`

### Launching

Run the module `jeanpaulstartui` giving a path where to find batches, and the user tags description file

Batch pathes can be separated with ';'

````bash
python -m jeanpaulstartui --batches /path/to/a/batch/folder;/path/to/another/folder --tags /path/to/user-tags.yml
````
