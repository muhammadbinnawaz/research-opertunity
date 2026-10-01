#Research Opportunity Portal
it is a  simple web app where faculty members can post view update and delete research opportunities in one place.

Name:Muhammad Bin Nawaz
Roll No:24P-0733
Class:BSCS 5A
GitHub Repository:https://github.com/muhammadbinnawaz/research-opertunity
Demo Video: Coming soon

##Features
- Add a new research opportunity through a form
- See all opportunities in a table
- View full details of any opportunity
- Edit an existing opportunity
- Close an opportunity with one click(Open->Closed)
- Delete an opportunity
- Success and error messages on the page
- Basic form validation on the frontend and the backend
- All data is stored in MySQL (nothing is hard-coded)

##Stuff Used
- Python(for backend)
- MySQL(database)
- HTML CSSand JavaScript
- Postman (for API testing)
##Requirements  of the portal

Before running the project, make sure you have:
- Python 3 installed
- MySQL Server installed and running
- The `mysql-connector-python` package (the only extra library used)


pip install mysql-connector-python




## How to Run
i have provided thecommands for ease while setting things up
1. Open the project folder in a terminal.
2. Create the database and table by running the SQL file:

mysql -u root -p < schema.sql



3. Set your MySQL password (so it is not written inside the code).
Windows (cmd):
Mac / Linux:
export DB_PASSWORD=your_password
If your MySQL user is not  root, also set DB_USER the same way. If your root user has no password you can skip this step.

4. Start the server:
python server.py

5. Open the browser and go to the local host `http://localhost:3000`
The frontend is served by the same server, so nothing else needs to be started.






##The Status Codes
200 Request worked (get,update,delete) 
201 | New opportunity created 
400 | Missing or invalid data 
404 | Opportunity not found 
500 | Something went wrong on the server 



#Implementation

The backend uses the `http.server` module that comes with Python hence no web framework was needed.Each of the request is checked by the method and the data is validated before it is saved. If something is wrong the server sends back a 400 with a message that the frontend shows to the user.
For updating, the server loads the old record first and only changes the fields that were sent. That is why the Close button only needs to send `{"status": "Closed"}`.

The frontend uses `fetch` to talk to the API and builds the table from whatever the server sends back.

