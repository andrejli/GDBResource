==================================
G D B R  - GRAPH DATABASE RESOURCE
==================================


A B O U T
----------

Custom made Graph Document based Database only for other project purposes.
Stores and loads data in .json format and in encrypted or plaintext .data files.


Dependencies
------------
Python3.6
git

Install
-------
use https://github.com/andrejli/GDBResource.git

Run database
------------
Go to program directory and write:

In Linux Terminal:

python3 Database_CMD.py

In Win10 Powershell:

python.exe ./Database_CMD.py

Documentation
--------------------
Every object has unique 9digit code. Objects, links are stored in .json
Every object has own data file with hashmd5.data
Data are entered via custom SimpleEditor and could be encrypted with simple encryption
So .json file doesn't contain any useful readable data without data stored in text.
Decoded objects could be searched via fulltext search.
Database also contains FulltextDigger which reveals all TAGS <> from decoded files and automatically finds
aliases between objects within .data files.

Predefined
----------
* root record = id 111111111 is object where all ids are stored. Contains also base key for database Encryption.
* object or record = object
* id = 9digit identification number of every object and link stored in database
* otype = object type like person, vehicle, report or computer program
* confirmation status = if existence of object is confirmed and verified


Admin Commands
~~~~~~~~~~~~~~
* reveal all commands in database  >>>help
* init new database  >>>init
* drop database >>>drop
* switch to another database  >>>switch
* exit program >>>exit

List commands
=============
* list all objects and links in database  >>>lsdb
* list all object types >>>lsot

Search Commands
===============
* find id  >>> fid
* find text in data  >>> ft
* find object type >>> fot
* near objects ids >>> near
* reveal boolean if two objects are linked together >>> ql

Edit Commands
=============
* new object record  >>>nr
* new link between objects  >>>nl
* edit id  >>> eid
* remove id  >>> rid

Selection Commands
==================
Not added to CMD yet!

Encryption Commands
===================
Not added to CMD yet!

Export Commands
===============
Not added to CMD yet!

How to use SimpleEditor
=======================
Simple editor is only used to edit NEW record. If you are editi
* To exit without write to .data file  >>>:q
* To exit with write to .data file  >>>:wq

When entering text to SimpleEditor you can provide text with database tags
<PERSON Name Surname DoB>

<PLACE Earth>

Always press ENTER after write tags because they are fastest way to index your dtaabase
Database is always indexed only in computer memory so any decoded records are not saved to disk
Database Engine automatically index all records and if they are not linked engine provide link called Alias

Alias is a link between database object and all relevant records in database where it was mentioned.
So you enter taged text and aliases with existing objects are provided by DB engine for you

Vizualize Data
==============
In near future we provide database with link to visualization library