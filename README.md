# Project Argos

Project Argos is a web application that requires any machine environment running a browser software, preferably Google Chrome.    
To launch the application, please go to https://projectargos.ga.

## Setup

There are several dependencies that are required. These can be installed by running
the following commands:

```
sudo pip install Flask Flask-Session apscheduler sklearn numpy scipy
sudo npm install chartist-plugin-axistitle
```

The code has primarily been tested in python3.6 but any python3.x should also
work fine.

Once you have everything installed, simply run `python app.py`.
Go to http://localhost:5000/ in your favourite browser and you are good to go!

## Deployment

For proper usage of the system, running it off a server is necessary. This
ensures that the data is constantly updated and that it is available online
from everywhere.

To do this, you will need to obtain a server. We used an Amazon Web Sever EC2 instance,
though any server should work, provided it has a static IP address. This
is achieved via AWS's elastic IP service. Additionally, you will
need to obtain a domain name. We got a free one from Freenom, though there are many
other services that will allow you to buy one. Point this domain name towards
your server's static IP, either by adding an A record or otherwise.

The next step is to clone the current repository into this
server.

You will now need to obtain an SSL certificate to support HTTPS. We
used ZeroSSL to do this, though again there are other alternatives
available. You will most likely need to add a record to the domain name
to prove ownership so do this. The end result of this will be a
certificate and an encryption key. Put these in 2 separate files
called host.crt and host.key respectively, located
within the root directory of this project (the same folder
as app.py).

We are now ready to rumble. You can run the system as a background process,
keeping it constantly up but allowing us to continue to use the server
including exiting it. Flask will dynamically assign it threads as required so this
is sufficient. The following command will do this: `python app.py server &`.
You will need to record the PID of this so that you can stop it in the future if
required. There are some bash scripts to do this which can be
found in the server/ folder: `run.sh` will start the service while
`stop.sh` shuts it down again. Place these scripts in the directory above this
repository to properly use them.

The final step of the process is to redirect from the HTTP version of the
domain name to the HTTPS instance. Your server might support this more directly,
however I wrote another, very simple, application to perform this redirection: `redirect.py`.
It can also be found in the server/ folder, with accompanying scripts to start and
stop it. Place these in the directory above this repository as well.

To fully run the server at this point, run the following commands:

```
./run.sh
./redirect.sh
```

To shut it down, run the following commands:
```
./stop.sh
./stop_redirect.sh
```

## Accounts

We have setup several accounts for interacting with the system, though an admin
can easily create more! Below are the login details for these:

### Admin
Username: DeploymentAdmin   
Password: Testing1EY23A

For help as an admin watch this video: https://youtu.be/kqDc-9gHSvs  

### Consultants
Username: DeploymentConsultant
Password: AcceptanceEY23    

For help as a consultant watch this video: https://youtu.be/wbseA_kYe-M

## Testing

Several dependencies are required to start testing. Simply run following command to install them:  
```
sudo pip install unittest2 selenium
```
To test the whole suite of backend functions, run :
```
python -m tests.testAllDemoVer test
```
To test single testcase, run:
```
python -m unittest2 tests.testAllDemoVer.testingClassName
```
To test frontend functions, run :
```
python testFrontend.py
```