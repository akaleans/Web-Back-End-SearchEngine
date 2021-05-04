Name:	Khalen Stensby
Class:	CPSC-449 Friday
Assn:	Project 6 - Search Engine

Twitter Search Engine

This project is intended to be a search engine created to work specifically with the mock
Twitter services we have created in the past. All methods are working properly and the entire
service can be tested easily with a post.sh file included. Execution of the program is
documented below:

	**NOTE**
	A.	This project makes use of the gensim library, if you do not already have it, 
		open a terminal and type "pip3 install --upgrade gensim"

	1.	Extract contents into a folder on your Desktop
	2.	Open a terminal at the folder location
	3.	Inside of the created folder directory, type "./bin/init.sh"
		a.	This step creates the database files from the .sql files inside of /share
	4.	Inside of the created folder directory, type "foreman start"
	5.	Open a new terminal at the folder location
	6.	Inside of the created folder directory, type "./bin/post.sh"
		a.	This step will run a sequence of http POST and GET commands
		b.	Simply scroll through the terminal to see the output of each statement
	7.	When done, inside of the terminal where foreman is running, press "Ctrl-C"
	8.	Exit the terminals
