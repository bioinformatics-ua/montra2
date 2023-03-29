How to deploy Catalogue with Docker?
==============

## First steps

1.	Please enter in the ''docker'' directory and create your `.env` file here, using `.env.example` as reference.
For local installation, you can just copy the `.env.example` content to a new file. <br>
**Note**: In case of port errors in the next steps, the problem could be related to a port already in use by
your system that you defined here and it is busy, choose other.

2.
    1. If you wish to run tests in a specific domain, you must specify the `PUBLIC_IP` variable. In example, if the application is 
    installed in the domain www.example.com you should set the `PUBLIC_IP` variable to that. Moreover, if the application 
    is running in a domain containing a suffix (i.e. www.example.com/suffix) then please specify the suffix in the 
    `BASE_DIR` variable. <br>
    Hence, for the previous example the variables should look as follows:
        ```
           
            PUBLIC_IP=www.example.com
            BASE_DIR=suffix
        
        ```
        You will be able to access the application using the url www.example.com/suffix
    2. If you want to run the application using the localhost instead, you can use the `.env.example` default settings.
    The variable `PUBLIC_IP` must be empty and the variable `BASE_DIR` can be set to anything since it will be running
    in the localhost. To change the default port, you can set the `PRODUCTION_MODE_PORT` variable to any port that is
    available and you wish to use. <br>
    **Note**: The `PRODUCTION_MODE_PORT` is the **host** port that will be used to communicate with the application.
    Hence, for the previous example the variables should look as follows:
          ```
           
             PUBLIC_IP=                  # Empty, since it will be running in the localhost
             BASE_DIR=suffix             # Or any suffix that you want
             PRODUCTION_MODE_PORT=8080   # Or other port that you want AND is available.
        
         ```
         You will be able to access the application using the url http://localhost:8080/suffix

    3. If you are making a new installation you should set the `NEW_INSTALLATION` variable to True, so an admin user (user: admin, password: emif) is created.
 
3. Run the following command to build the image.
  
        $ sh build.sh
   When prompted for the desired version you can use the default one (press Enter). In that case, the system will
   determine the version based on the git version. <br>
   Otherwise, specify a version that you wish to associate to the image.
  
4. Wait a couple of minutes until the image is built. It might take some time if it is the first time you are building
 the images. If it is not, it will use as much cached information as possible and the building process will be 
 faster. When it is finished building, you will be notified in the terminal with a "Build Complete" message.
 
5. The image is built and now it is time to run the application. For that, simply execute the `run.sh` script. It will
stop any running instances associated with the application before running them again. 

        $ sh run.sh
   This process will take some time until the application is up and running. You can check the state of the application
   by reading the container logs:
   
        $ docker logs  docker_catalogue_1
   If the container's name is not docker_catalogue_1, please check its name using the following command:
   
        $ docker container ls
   When the application is running, you can access it with your browser using the URL mentioned earlier.
  
*Note*: if you are running the application with the default ports, you should be able to access it:
- `production mode`: http://localhost:8080
- `debug mode`: http://localhost:8181

6. If you started a fresh installation with `NEW_INSTALLATION=True` you can set it back to `False` to speed up future startups.

## Environment variables
As mentioned in the previous section, the application can be parametrized using a set of variables defined in the .env
file. This section will guide you to these variables and their role within the application. <br>

### Test variables
`LOAD_TEST_DATA` : flag indicating that the test data will be loaded into the database. It must be either `True` or `False`.
`TEST_MODE` : flag indicating that the deployed environment will be setup for running tests inside the container.
It must be either `True` or `False`.
If set to `False`, the application will not contain chrome, chromedriver and necessary python test dependencies.
If set to `True` and `DEBUG_RUN=False` the `PUBLIC_IP` will be set to `http://nginx:$PRODUCTION_MODE_PORT` so tests can
access the application.
`RUN_TESTS` : flag indicating that the application will run the tests suit automatically after the container starts.It must be either `True` or `False`.
### Installation variables
`NEW_INSTALLATION` : tells if the current installation is fresh. If true some basic users and questionnaires will be inserted into the database.
`PUBLIC_IP` : defines the application's url. Set to empty if you wish to run the application in the localhost. Otherwise,
the public ip must be specified to prevent fake HTTP Host headers.<br>
`BASE_DIR`  : defines the application's url suffix, if any. <br> 
`PRODUCTION_MODE_PORT`  : this will be the host's port to communicate with the application running in the container. It 
is only used when `DEBUG_RUN` is set to `False`.<br>
### Postgres variables
`DOCKER_POSTGRES_DB`        : defines the database's name to be used. <br>
`DOCKER_POSTGRES_USER`      : defines the postgres username. <br>
`DOCKER_POSTGRES_PASSWORD`  : defines the postgres password. <br>
### E-mail variables
The following variables are user specific and are used for the platform's e-mail notification system. <br>
`EMAIL_USE_TLS`         : whether to use the Transport Layer Security protocol when using the platform's e-mail system. It must be either 'True' or 'False'.<br>
`EMAIL_PORT`            : the e-mail service port. <br>
`EMAIL_HOST`            : the user's email host (i.e. mail.ua.pt) <br>
`EMAIL_HOST_USER`       : the user's e-mail (i.e. example@ua.pt) <br>
`EMAIL_HOST_PASSWORD`   : the user's email password.<br>
`DEFAULT_FROM_EMAIL`    : <br>
**Note** Never commit any of these variables to the remote repository.
### Git variables
The following variables are developer specific and are used for the platform's git features such as automatic issue creation. <br>
`GIT_USER`  : defines the username matching the developer's git account. <br>
`GIT_PASS`  : defines the password for the developer's git account. <br>
**Note** Never commit any of these variables to the remote repository.

### Debug mode
**DEVELOPERS ONLY** <br>
**Note**: if you wish to run tests in debug mode, read this section.<br>
The application can run in debug mode. The main difference is that it uses the django's development Web server instead 
of [UWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) and [NGINX](https://www.nginx.com/).
Check [django's official documentation](https://docs.djangoproject.com/en/3.0/ref/django-admin/#runserver) for more
information about this. <br>
`DEBUG_RUN` : flag indicating that the application must be run in debug mode. It must be either `True` or `False`. 
This is meant for developers only. 
`DEBUG_MODE_PORT`       : this will be the host's port to communicate with the application running in the container. It 
is only used when `DEBUG_RUN` is set to `True`.<br> 
If you also want to run tests in this mode, note that the `PUBLIC_IP` and `BASE_DIR` variables **must** be empty.
 Otherwise,  tests will not work. 

## Development mode

The setup for new developers can be made using the docker or installing everything locally. **Note**: We strongly advise you to adopt the use of docker for development. 

### Using Docker
The current section will guide you through the process of configuring the IDE (Integrated development environment) to aid you in your work within the platform.
The instructions provided are meant to be used with the PyCharm (Professional Edition) but, nonetheles, most of these tools are also available in other IDEs and editors such as Visual Studio Code.

#### Database connection
You can setup a connection to the database through the "Data Source Connection" functionality of the IDE.
Ideally, you might want this to have an easier access to the database and view its tables and their fields.
By default, the Postgres/db container doesn't have its port exposed, for that you have to add
```yaml
ports:
  - 5432:5432
```
to the configuration of the such container.
To do so:

1. Open the "Database" window. If it is not visible, toggle it in the "View/Tool Windows/Database".
2. Click the "Add" button with a **+** symbol.
3. From the dropdown, select "PostgreSQL".
4. In the new window, fill the "Host" field with "localhost" (or the url of the database) and the "Port" field with the **host** port (left-most) assigned to the PostgreSQL db container. 
5. Fill the "User" and "Password" fields with the ones found in the `.env` or `.env.example`. 
6. Click on "Test Connection" to verify that the IDE has successfully connected to the database.
7. If the connection's test worked properly, click OK.
8. You are now able to navigate the database via the "Database" window.

Check the [official documentation](https://www.jetbrains.com/help/pycharm/connecting-to-a-database.html#connect-to-postgresql-database) for more information.

#### Docker integration
You can integrate the docker environment with the IDE. You are able to manage your images and containers within your working environment. Moreover, you can also navigate the container's file systems, check the container's logs and access the container's environment variables. To do so:

*You must have Docker and docker-compose installed*

1. Go to "Settings/Preferences". Select "Build, Execution, Deployment | Docker". 
2. Click **+** to add a new docker configuration.
3. In the new window, you must specify how to connect to your Docker daemon. It can be done with the TCP socket, docker machine or Unix socket (easier method for Unix systems).
4. If the message "Connection successful" is displayed, you are good to go. Otherwise, go to step 3 and try again with other method or parameters.
5. Access your docker daemon in the "Services" tab. If it is not visible, toggle it in the "View/Tool Windows/Services". It might appear under "Docker" instead of "Services".
6. Connect to your daemon by clicking the Play button.
7. Navigate through your images, its running containers, etc. Select a container to see its logs (same as docker logs command)

Check the [official documentation](https://www.jetbrains.com/help/pycharm/docker.html) for more information. <br>
See also  [connection settings](https://www.jetbrains.com/help/pycharm/docker-connection-settings.html) if you are having trouble connecting to your docker's daemon.

**Note**: you can manage your container inside the IDE (same as docker-compose up/down). Nonetheless, it is advised to use the script `run.sh` provided in order run/stop the containers. 


#### Remote virtual environment
Note: There is a `.idea` directory on the root of the repository which contains the necessary configuration files so Pycharm setups this automatically.
All you need to do is open the root of the repository as a project in Pycharm.

In order to configure your IDE with the exact same interpreter that the application is running, you must configure a "Remote virtual environment". This is useful since you will have auto-complete, syntax highlighting and other features that will match the interpreter being used inside your container. To do so:

1. Go to "Settings/Preferences". Select "Project | Project Interpreter".
2. Click the "Settings" button next to the down-facing arrow on the right side of the window.
3. Select "Add".
4. Select the "Docker" option.
5. In the "Image Name" field, select the one that contains the python's interpreter that you desire to use.
6. Select "OK". 
7. If it worked properly, you should see now the proper linting and syntax highlighting. You might need to associate the virtual environment with your project in the "Project Interpreter" window.

Check the [official documentation](https://www.jetbrains.com/help/pycharm/using-docker-as-a-remote-interpreter.html#config-docker) for more information.


#### Django environment 
Note: There is a `.idea` directory on the root of the repository which contains the necessary configuration files so Pycharm setups this automatically.
All you need to do is open the root of the repository as a project in Pycharm.

You can use the IPython (Interactive Python) functionality of your IDE using the configurations of the Django application. This is very useful if you wish to, in example, quickly test some code related to the django application before writing it down in your main code. This can speed up the debugging process while developing on the platform. To do so, you must configure the project's interpreter to be the one that you use within the container. To do so:

Now, to enable Django support:
1. Go to "Settings/Preferences". Select "Languages & Frameworks/Django".
2. Check the "Enable Django Support" checkbox.
3. In the "Django Project Root", select the `montra-pvt/emif` (the root of the application).
4. In the "Settings", select the `settings.py` file (`emif/settings.py`).
5. In the "Manage script", if it says `manage.py` leave it as is, otherwise select the `emif/emif/manage.py` file.
6. Click "OK".
7. If everything went accordingly, you are now able to open the "Python Console" tab and work in the IPython console while interacting with the application.

Check the [official documentation](https://www.jetbrains.com/help/pycharm/django-support7.html#enable-support) for more information.

#### Debugger
Note: There is a `.idea` directory on the root of the repository which contains the necessary configuration files so Pycharm setups this automatically.
All you need to do is open the root of the repository as a project in Pycharm.
However, you should perform the step 3 anyhow.

Using a debugger is much more powerful than using simple prints to check what is happening on the code.
To get the debugger working follow the next steps:

1. You must open repository's root on Pycharm.
You can then mark the `emif` directory as the source root by clicking with the right button of the mouse on top of the `emif` directory, then at the bottom "Mark Directory as" -> "Sources Root".
This way you can edit all the files of the repository in Pycharm and have correct code auto-completion/analysis for django code.

2. On section [Remote virtual environment](#remote-virtual-environment) describes how to create an environment using a docker image.
To setup the debugger you should either edit the existing one or create a new one that uses the docker-compose file.
You can still use the docker image, but later on you will have to make sure that the other services (solr, rabbitmq, ...) are
 accessible to the catalogue container.
For this you can either use the host network or use the docker network of the other services.
We will explain, however, with the docker-compose option.

   1. On step 4 of [Remote virtual environment](#remote-virtual-environment) choose docker-compose;
   2. On "Configuration files" choose the docker/docker-compose.yml file;
   3. On "Service" choose catalogue.
   4. Click Ok

3. Looking at our docker-compose file we can see that we expect the user to define a couple of environment variables.
Such are defined in a .env file, however Pycharm, by default, does not support reading such for a .env files.
To overcome this you should install the [.env files support](https://plugins.jetbrains.com/plugin/9525) Pycharm plugin.
It will read the .env file and automatically load the environment variables and use them on docker-compose.

4. Make sure you have Django Support enabled on Pycharm by following the instructions of section [Django environment](#django-environment)

5. Now create two configurations. One will be used to debug Django code and the other to debug celery tasks.

   5.1 
   1. For Django create a configuration of type "Django Server";
   2. On host put `0.0.0.0`;
   3. On port put the value of the DEBUG_MODE_PORT environment variable;
   4. On environment variables add `DEBUG_DJANGO=1`.
   
   5.2
   1. For celery create a configuration of type "Python";
   2. On script path put `/usr/local/bin/celery`;
   3. On arguments put `-A emif.celery worker -l debug -B -f celery.log`;
   4. To the environment variables add `C_FORCE_ROOT=True;DEBUG_CELERY=1`

You are all setup now.
When executing the debugger on one of these configurations, it will launch the catalogue container and associated services.
When debugging Django code there is no need to restart the debugger after making changes on the code, as it will automatically detect and reload.
Celery, on the other hand, does not have a reload mechanism, for that, every time you make change you have to rerun the debugger, which will rerun the entire catalogue container.
In the future we could put celery on a separate container, making the reload process of such much faster and the django app container would not be restarted.

To use another IDE is important to note that the entrypoint of the catalogue container is the docker/start_catalogue.sh script.
This script then checks if a custom run command was specified (ex: docker-compose run catalogue ...).
If so, and one of the variables `DEBUG_DJANGO` or `DEBUG_CELERY` is set to 1, the specific command will be executed instead of the default one.
For example, if you execute `docker-compose run -e DEBUG_DJANGO=1 catalogue debbuger-command`, `debugger-command` will execute instead of the default `python manage.py runserver`.

### Without Docker
#### Note
This guide is provided for Ubuntu 18.04, for other systems or releases instructions may be subject to changes.

All terminal commands can be executed, but whenever we use something between '<', '>' it means that it must be changed for the user. Eg. `<your_path>` --> `/opt/`

#### Install Dependecies in Ubuntu


1.  Install packages

        $   sudo apt-get install git python-pip curl mongodb postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3 postgresql-server-dev-9.3 rabbitmq-server libxml2-dev libxslt1-dev python-dev libpython-dev build-essential libyaml-dev python-psycopg2 libpq-dev libffi-dev cryptography

2. Checkout of the source code

        $   mkdir <your_path>/MONTRA-ROOT
        $   cd <your_path>/MONTRA-ROOT
        $   git clone -b master https://github.com/bioinformatics-ua/montra-pvt.git

    If you're a developer, you can change branch to dev ( see  [DevelopmentCycle](https://github.com/bioinformatics-ua/emif-fb/wiki/DevelopmentCycle "DevelopmentCycle") )

3.  Install virtualenv

        $   sudo pip install virtualenv

4. Activate Virtual Environment

        $   virtualenv <your_path>/MONTRA-ROOT/emif_env
        $   source <your_path>/MONTRA-ROOT/emif_env/bin/activate

5.  Install pip requirements

    1.  Install requirements

            $   pip install -r requirements.txt

6.  Install and Start MongoDB

        $ sudo mkdir <your_mongodb_path>
        $ sudo mkdir <your_mongodb_path>/db

    Now you have 2 hypotheses:

    1. Change the permissions of data and db folders and run "mongod":

            $   sudo chmod a+x <your_mongodb_path>
            $   sudo chmod a+x <your_mongodb_path>/db
            $   mongod --dbpath <your_mongodb_path>

    2. Run mongod as root:

            $   sudo mongod --dbpath <your_mongodb_path>

7. Create '~/.pgpass' file and insert:

        localhost:5432:*:<your_postgres_user>:<your_postgres_pass>

8. Change permission mode of pgpass file

        chmod 600 ~/.pgpass

9.  Install and Configure Apache-solr

    1. Install JDK and JRE:

            $   sudo apt-get update
            $   sudo apt-get install default-jre default-jdk

    2. Download and install SOLR

            $   cd /opt
            $   sudo wget http://archive.apache.org/dist/lucene/solr/4.7.2/solr-4.7.2.tgz
            $   sudo tar -xvf solr-4.7.2.tgz
            $   sudo cp -R solr-4.7.2/example /opt/solr
            $   cd /opt/solr

    3. Go to folder emif-fb-root/conf/solr/ and copy all the files to the solr default core configuration
        
            $ cp -R <your_path>/montra-pvt/confs/solr/suggestions /opt/solr/solr/
            $ cp -R <your_path>/montra-pvt/confs/solr/collection1/* /opt/solr/solr/collection1/conf/

10. Create a script file:

    1. copy code from:

            https://gist.github.com/bastiao/c8d3be799dc7c257f01a

    2. Paste in a new file in confs/ folder. Eg:

            <your_path>/MONTRA-ROOT/montra-pvt/confs/script.sh

    3. Open file and change (to the same of the *~/.pgpass* file)

            APP_DB_USER=<your_postgres_user>
            APP_DB_PASS=<your_postgres_pass>

    4. Run the script

            $ sudo sh <your_path>/MONTRA-ROOT/montra-pvt/confs/<script_name>.sh


11. Run Apache-solr as service

    Go to solr folder and Run:

        $   sudo java -jar /opt/solr/start.jar

12. Open a new terminal window/tab and run celery. Load virtualenv and go to MONTRA-ROOT/montra-pvt/emif and run: 

        $   celery -A emif.celery worker -l debug -B

13. (OPTIONAL - only for IdP )Create sp.key and sp.crt files on confs/certificates being them respectively the private key and the public certificate for all comunication originating from third-party IDP's to our SP endpoint

14. (OPTIONAL - only for IdP )The SP endpoint for IDPS uses xmlsec (which is installed through this readme). By default the path to this binary is '/usr/bin/xmlsec1'. If the path on the system is different it should be defined through the variable 'XMLSEC_BIN' on emif/emif/settings.py, otherwise it's okay to leave the default value.

15. Sync Database

        $   python manage.py syncdb
        $   python manage.py migrate
        $   cat <your_path>/MONTRA-ROOT/montra-pvt/confs/newsletter/newsletter_templates.sql | python manage.py dbshell
        $   python manage.py import_questionnaire <path_to_fingerprint_schema>  


16. (Optional/Temporary) Support Developer Group

        $   python manage.py shell
        >>> import utils.developer_group
        >>> quit()

17. Run Server

        $   python manage.py runserver 0.0.0.0:8000

17. Create a folder to documents population characteristic

        mkdir -p <your_path>/MONTRA-ROOT/emif/static/files/

18. Open browser and write

        localhost:8000

### Optional Steps:
1. Create Local Settings File:

        <your_path>/MONTRA-ROOT/emif/emif/local_settings.py

2. Add lines for email integration - **Fill accordingly** (optional):

        EMAIL_HOST = 'address.mail.com'
        EMAIL_HOST_PASSWORD = 'passwd'
        EMAIL_HOST_USER = 'login'
        EMAIL_PORT = 25
        EMAIL_USE_TLS = True


3. Add lines for integration with github issues and releases **Fill accordingly** (optional)

        GITHUB_USERNAME='githubusername'
        GITHUB_PASSWD='pass'
        GITHUB_ACCOUNT='bioinformatics-ua'
        GITHUB_REPO='montra-pvt'


4. To add a new IDP service to the our SP endpoint just add the service metadata xml file path to IDP_SERVICES array **Fill accordingly** (optional).

        IDP_SERVICES += [path.join(BASEDIR, 'idp_metadata.xml')]


### Start the virtual environment and development (always)
1. Go to solr folder and Run:

        $   sudo java -jar /opt/solr/start.jar


2. Start MongoDB

    If you change the permissions of the /data and /data/db folders

        $   mongod --dbpath <your_mongodb_path>

    else

        $   sudo mongod --dbpath <your_mongodb_path>

3. Activate the virtual environments

        $   source <your_path>/MONTRA-ROOT/emif/bin/activate

4. Start Django

        $   python manage.py runserver 0.0.0.0:8000

5. Open browser at:

        localhost:8000
