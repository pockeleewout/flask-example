# Flask Example Project

This project demonstrates how to use Flask to create a database, use this 
database and create a REST API to access objects stored in it.

This is not intended to be a complete project, it is merely to show the basics.

## Installation

### Python and Virtualenv

Make sure you have [Python](https://python.org) and 
[Virtualenv](https://virtualenv.pypa.io/en/latest/).

On [Arch Linux](https://archlinux.org), simply run the following to install them:
```
sudo pacman -S python python-virtualenv
```

On [Debian](https://debian.org)/[Ubuntu](https://ubuntu.com) and derivatives run:
```
sudo apt install python virtualenv
```


### Setting up the virtual environment

To set up the virtual environment, open a terminal window in the root directory 
of the project and run the following commands:
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Initializing the database

To initialize the database after installation, in the terminal window where the 
virtual environment is active, run
```sh
flask create-db
```

### Running the example

To run the example, simply invoke
```sh
flask run
```

To view the example, open a web browser and go to http://localhost:5000

## Extra knowledge

### Virtual environment

A virtual environment can be created in any directory, simply specify the 
directory you want to use when creating it
```sh
virtualenv <dir>
```

To activate the virtual environment, run
```sh
source <dir>/bin/activate
```

### Extra commands

Some extra operations are provided through the ```flask``` command

#### Creating the database

To create a database, simply run
```
flask create-db
```

#### Deleting the database

There are 2 ways to delete the database: clearing the data from the database and
deleting the database file.

To delete the data, run
```
flask drop-db
flask create-db
```

To delete the database file, delete the file `database.sqlite3`
```
rm database.sqlite3
```

