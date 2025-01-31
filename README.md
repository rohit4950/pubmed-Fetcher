This projects helps to fetch reasearch publications from the PubMed API bases on user query. 

This is done by using python modules like requests , XML parser. The obtained output is saved in a CSV containing all the data.This projects accepts queries as a command line Argument. This is done by using argparse module. 
The project has two python files: 
get_papers_list.py: This file contain all the necessary functions and code used to extract and fetch data from the PubMed API and save it into the CSV File.
get_pubmed_papers: This file contains the main function which runs the python scripts and provides options displayed in the command line arguement for further query search. 

This Project is done by using poetry environment . Hence make sure you have installed poetry and necessary packages. 
Pyproject.toml : This files contains all the necessary dependancies , packages and function calls in the poetry enviornment. It gives a description of how the code should be executed in the poetry environment. 

Rest all files are automated scripts done by the python server. 

How to execute this program : 

1) Clone the repository to your terminal or VS codeStudio :
   Open terminal and type : git clone https://github.com/rohit4950/test-get-papers.git
   then later enter into the directory by using the command : cd test-get-paper
   
2) Now once you entered the directory install poetry and set up the poetry environment:
   run the following commands: pipx install poetry
   Now once we have installed poetry, go to the test-papers-git directory and run the command: poetry install . This will create and virtual enviornment for project .

   Check if requests module is present by running the command : poetry show requests . if it is not installed , install the requests by running: poetry add lxml requests

3) Now once the all the dependencies are installer are set .Our projects is good to go.
4) For an example enter the command:  poetry run get_pubmed_papers "Cancer research" --f output.csv ; This will return all the publications based on the query "Cancer research" and show the results in output.csv


References and LLM tools used for this Project : 
1) Poetry and requests documentation
2) Chatgpt(for code optimisation and imporvements)

