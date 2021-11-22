NeuroflowCodingProject
=======================

A simple REST API written in Python using Flask and SQLAlchemy.

Installation
------------

After cloning the repo, create a virtual environment and install the requirements. Refer to the commands below:

    $ python -m venv env
    $ source env/bin/activate
    (env) $ pip install -r requirements.txt

Running
-------

To run the server use the following command:

    (env) $ python api.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader

Then from a different terminal window you can send requests.

API Documentation
-----------------

- POST **/api/users**

    Use this request to register a new user.<br>
    The request must contain a `-d` flag that defines `username` and `password` fields.<br>
    If the request succeeds, the status code 201 is returned. The body of the response contains the JSON with the newly added user's username.<br>
    If the request fails, the status code 400 is returned.<br>

- GET **/api/users/&lt;int:id&gt;**

    Use this request to return a user and its relevant information.<br>
    If the request succeeds, a status code 200 is returned. The body of the response contains a JSON object with the requested user's username, streak,and the timestamp of this user's last POST request to /api/mood.<br>
    If the request fails, the status code 400 is returned.
    
- DELETE **/api/users/&lt;int:id&gt;**

    Use this request to delete a specified user.<br>
    If the request succeeds, the status code 200 is returned. The body of the response contains a success message that says true to indicate the action succeeded.<br>
    If the request fails, the status code is returned.

- GET **/api/mood**

    Use this request to return all moods for a given user.<br>
    This request must be authenticated using a HTTP Basic Authentication header. The client must provide the login details of a valid user using the `-u` flag in the request.<br>
    If the request succeeds, the status code 200 is returned. The body of the response contains a JSON object with a list of the user's moods.<br>
    If the request fails, the status code 401 is returned, indicating the client is unauthorized to access that endpoint.
    
- POST **/api/mood**

    Use this request to add a new mood for the given user.<br>
    This request must be authenticated using a HTTP Basic Authentication header. The client must provide the login details of a valid user using the `-u` flag in the request.<br>
    If the request succeeds, the status code 201 is returned. The body of the response contains a JSON object with the mood that was just entered.<br>
    If the request fails due to bad arguments, the status code 400 is returned.<br>
    If the request fails due to invalid user or no user login entered, the status code 401 is returned.

Usage
-------
When you load up the REST api, you will find that a guest user already exists at http://127.0.0.1:5000/api/users/1

The following `curl` command returns that user's information in a JSON object:

```
    $ curl -i http://127.0.0.1:5000/api/users/1
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 122
    Server Werkzeug/2.0.2 Python/3.9.2
    Date: Mon, 22 Nov 2021 19:00:47 GMT
    
    {"streak": 1,"timestamp": "Mon, 22 Nov 2021 14:00:22 GMT","username": "guest"}
```

These credentials can now be used to access that user's moods:

    $ curl -u guest:password -i -X GET http://127.0.0.1:5000/api/mood
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 20
    Server: Werkzeug/2.0.2, Python/3.9.2
    Date: Mon, 22 Nov 2021 19:02:36 GMT
    
    {"moods":["happy"]}
    
Using the wrong credentials the request is refused:

    $ curl -u guest:pass -i -X GET http://127.0.0.1:5000/api/mood
    HTTP/1.0 401 UNAUTHORIZED
    Content-Type: text/html; charset=utf-8
    Content-Length: 19
    WWW-Authenticate: Basic realm="Authentication Required"
    Server: Werkzeug/2.0.2 Python/3.9.2
    Date: Mon, 22 Nov 2021 19:03:50 GMT
    
    Unauthorized Access
    
The following `curl` command registers a new user with username `guest2` and password `password`:

    $ curl -i -X POST -H "Content-Type: application/json" -d '{"username":"guest2","password":"password"}' http://127.0.0.1:5000/api/users
    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 26
    Location: http://127.0.0.1:5000/api/users/2
    Server: Werkzeug/2.0.2 Python/3.9.2
    Date: Mon, 22 Nov 2021 17:35:48 GMT
    
    {"username": "guest2"}
    
 
The following `curl` command adds a new mood to a specified user, in this case `guest2`:

```
   $ curl -u guest2:password -i -X POST -H "Content-Type: application/json" -d '{"mood":"sad"}' 
http://127.0.0.1:5000/api/mood
    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 20
    Server: Werkzeug/2.0.2 Python/3.9.2
    Date: Mon, 22 Nov 2021 17:50:35 GMT
    
    {"mood": "sad"}
```

You can delete a user from the database using the following `curl` command, which deletes user `guest2`:

```
    $ curl -i -X DELETE http://127.0.0.1:5000/api/users/2
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 22
    Server: Werkzeug/2.0.2 Python/3.9.2
    Date: Mon, 22 Nov 2021 17:53:58 GMT
    
    {"success": true}
```

Writeup/Disclaimer
-------

This REST API was built entirely for the purposes of a coding assessment from Neuroflow. It is in no way intended to be used for production services. 

I would like to share that I had no prior experience with web services and REST APIs before this project. This was my first time using frameworks like Flask and SQLAlchemy. After recieving the assignment from Neuroflow on 11/19, I spent the first day educating myself on what REST APIs are and how to go about building one in Python. After going through a few tutorials and a lot of documentation, I began working on this project on 11/20 and as I got more comfortable with REST concepts and Flask, I was able to build the specified API a lot faster than I had anticipated, given that I had no clue what a REST API was three days ago. I haven't done extensive testing on the system, but I've ensured that all of the core funtionality required of the system does and will continue to work. Feel free to run and modify the accompanying `test.py` file in order to test the API using the requests library. 

There were definitely shortcuts taken in order to complete the assignment, and those shortcuts would be disastrous if implemented on a real, production web service. 

   For instance, the way the system maintains the data for each user's moods is not ideal. The program stores each users' list of moods in a csv file, line by line for each user. So, the user with an id of 2 has its moods stored in line 2 of the csv file, with each mood separated by a comma. This tends to bug out when it comes to deleting users and updating the csv file afterwards. 

   This could be circumvented if I fully implented a database to hold both the Users and the Moods. In that case, a primary key for the users can be used to reference moods stored in another table. The mood id would be linked the user id, and it would be simple to query and/or delete all moods for a given user. Depending on how the tables are linked, the moods could automatically be removed when a user is deleted and the tables casacade. 

The streak functionality is also a bit finicky but it will work as expected for the most part. When a user is created, their streak is initially zero and timestamp of last POST request is null. When the user POSTs a mood, that timestamp is saved to the user and its streak is set to 1. From then on, whenever the user POSTs a mood, that request's timestamp is compared with the most recent timestamp stored in the User model. If the difference between the new request and the most recent request are longer than 24 hours, the user's streak was broken and it gets reset to 1. If the new request was within 24 hours of the most recent request, the program checks to see if the new request is the next day after the most recent request. If this is true, then the streak is incremented. Otherwise, streak is left alone, and the user's timestamp is set to the timestamp of the new request.

In order to accomodate more users and data, an overhaul of the database and data-storage methods used in project is definitely needed. A CSV file is not equipped to handle large amounts of data, as well as maintaining that data with precision and accuracy. I'm sure there are better ways of implementing a database to not only hold the Users for the system, but also holds the Mood data as well. 

