# Integration Tests using Python and Selenium

The selenium driver performs actions in a browser just as a user would do.  
It can run in a normal browser window, or in headless mode (without a graphical interface).  
The implemented test suite can run in both ways.

# How to run the tests?

The tests can be executed automatically inside the docker container (using the browser headless mode).

However, to see the execution of the tests in a normal browser window (in your local environment), the following requirements must be satisfied.

## Requirements

### Python

Python == 2.7.6

#### Python modules
Install the requirements.txt in the repository root or only the following packages using `pip install`:

```pip
html-testRunner==1.2.1
selenium==3.141
```

### Chrome and ChromeDriver

The tests were created to run with version 84.0.4147.0 of ChromeDriver, and those are very sensitive to the Chrome version. 
The Version 84.0.4147.0 of Chrome and ChromeDriver can be downloaded [here](https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Linux_x64/768968/). 
Instructions to install these versions are below.

Notes: 
- Make sure you do not have other installations of Chrome on your machine.
- For searching other versions consult this [link](https://www.chromium.org/getting-involved/download-chromium).


#### Installing Chrome
These instructions were created for Linux Distros (we did not create documentation about the installation of this for Windows or macOS). Therefore, the procedure is the following:

 1. Install dependencies
``` sh
sudo apt-get update
sudo apt-get install libxss1 libappindicator1 libindicator7 libgbm-dev
```
 2. Download Chrome zip of the correct version
``` sh
wget 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F768968%2Fchrome-linux.zip?generation=1589492137977189&alt=media' -O chrome-linux.zip
```
 3. Extract folder to /opt/
``` sh
sudo unzip chrome-linux.zip -d /opt/
rm chrome-linux.zip
```
 4. Add ``` export PATH=$PATH:/opt/chrome-linux ``` at the end of your .bashrc file in your home directory, and then run ``` source ~/.bashrc ```

 5. The command ``` chrome ``` should work and open a Chrome window

 6. The command ``` chrome --version ``` should output ``` Chromium 84.0.4147.0 ```

 7. To develop tests it is practical to have a desktop launcher for this installation, which can be created using the instructions on this [link](https://askubuntu.com/questions/64222/how-can-i-create-launchers-on-my-desktop) or similar.

#### Installing ChromeDriver

 1. Download chromedriver zip
``` sh
wget 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F768968%2Fchromedriver_linux64.zip?generation=1589492142972831&alt=media' -O chromedriver_linux64.zip
```
 2. Extract binary to /usr/local/bin/
 ``` sh
sudo unzip -j chromedriver_linux64.zip -d /usr/local/bin/
rm chromedriver_linux64.zip
```

 3. The command ``` chromedriver --version ``` should output ``` ChromeDriver 84.0.4147.0 (...) ```

## Run Script Arguments

The entry point to run the tests is the ``` run_tests.py ``` script. Arguments:

 - **-h** to see a resume of all arguments: ``` python run_tests.py -h ```
 - **-b** to specify the base URL in which tests will run on: ``` python run_tests.py -b http://localhost:8181 ```
 - **-hl** to use the browser headless mode (mandatory inside docker container).
 - **-t** followed by the test class name to run only one test, e.g: ``` python run_tests.py -t LoginTestCase ```
 - **-tr** to use the TextTestRunner, which will only report text to the terminal. By default, the report of tests execution will be under ``` tests/units/test_results ``` in HTML format. This is useful for developers not to generate tons of HTML reports.
 
 Advanced options:
 - **-d** to dump the database state to a JSON fixture before running the tests, for example ``` python run_tests.py -t FingerprintAddTestCase -d ``` will save the database state in ``` emif/fixtures/test_fixtures/FingerprintAddTestCase.json ``` before running the test. (Only works inside docker container)
 - **-l** to load the test fixtures before running the tests, for example ``` python run_tests.py -t FingerprintAddTestCase -l ``` will load the fixtures in ``` emif/fixtures/test_fixtures/FingerprintAddTestCase.json ``` before running the test. This ensures the database is in the correct state to run the test, assuming the fixtures file is correct. (Only works inside docker container)
 
The used arguments are displayed in the HTML report title.

## Running tests

To be able to run the tests, the environment variables `LOAD_TEST_DATA` must be set to `True`.

There are two options for running the tests:

### Option 1 - Run the tests inside the docker container (without GUI)

To run the tests inside the docker container:

- set the test environment variables in .env to:
```
TEST_MODE=True
RUN_TESTS=True
```
- run the build.sh script on the docker directory, so the image used contains both the chrome and chromedriver.
  This is required because our Dockerfile uses multi-stage builds and by default we don't install test dependencies and tools,
  only when `TEST_MODE` is set to `True`.
- start the container.

The tests will run automatically after the application starts.

**Two runs** of the test suite will be executed inside the container:
1. Without loading fixtures: Runs the tests sequentially without manipulating the database in the between.  
2. Loading fixtures: Runs the tests with the -l argument which loads the corresponding test fixtures before each test.

These runs will generate two separate HTML reports (when finished) inside ``` tests/units/test_results ``` folder.

It is possible to follow the execution of the tests by accessing the container logs, through the following command:

``` sh
docker logs -f docker_catalogue_1
```

Note that this is the option that gives you more information about the test results since the -l argument can only be used inside the docker container.  
With the -l argument, at the beginning of each test, the database is loaded to a correct state, and therefore there will be no situations where a test fails because another one failed before.

#### Common fails

If you encounter some tests failing with something similar to the following error:
```
unknown error: session deleted because of page crash from unknown error: cannot determine loading status from tab crashed with ChromeDriver Selenium
```
There are different solutions as mentioned [here](https://stackoverflow.com/a/53970825/12980218), one of them being adding the volume mapping `/dev/shm:/dev/shm` to the catalogue container.

### Option 2 - Run the tests in your local browser (with GUI)

To see the tests running in a local browser window:
1. Set the test environment variables in .env to:
```
TEST_MODE=False
RUN_TESTS=False
```
and bring the containers up.
2. Have chrome/chromium + chromedriver installed. Follow the instruction in [Chrome and ChromeDriver](#chrome-and-chromedriver);
3. Create a python 2 virtual environment and install the dependencies mentioned in [Python modules](#python-modules);
4. Using the previous virtual environment run `python run_tests.py`. If you want you can import the virtual environment
into pycharm and then use its debugger by creating a Run Configuration of type Python with:
   1. Script path: path to the `run_tests.py` script;
   2. Python Interpreter: choose the created virtual environment created in 3.

Note: It is necessary to ensure that the computer screen is always active during the execution of the tests in a normal browser (with the headless mode it is not necessary).  
If you are thinking of abandoning the computer and leaving the tests to run without the headless argument, first disable the blank screen option in your operating system. On Ubuntu: Power Settings → Blank Screen → Never

# Developing tests

## Code Structure

 - Tests are organized in subfolders. Each folder contains tests for the features of one django app.
 - The "utils" folder contains several utility files to generalize the tests code.
 - The run_tests.py script is the entry point to run the tests, even if you want to run only one test.
 - The test suite runs in the order of the TEST_CLASSES list, inside run_tests.py.
 - The database maintains the state between the execution of different tests, so the order in the list is important.

## Initial database state

The database must be in a specific state for the test suite to run correctly. 
You can consult the ``` /emif/reset_test_data.sh ``` file to see all fixtures that are automatically loaded into the database before the tests start running.

### Users

Three users are automatically created:

1. user1 is a normal user who belongs to the test_community.
2. user2 is a superuser who can access the admin panel and is the owner of the test_community.
3. user3 is a normal user who does not have access to the test_community.

The password for all users is test123.

## Useful commands

### Reset database

Before running the test suite, the database must be reset. The script ``` /emif/reset_test_data.sh ``` runs the commands to reset the database to the initial tests state. Use the following command to run it:

``` sh
 docker exec -it docker_catalogue_1 /bin/bash -c "cd /deploy/catalogue/emif; ./reset_test_data.sh"
```

Note: The environment variable ``` TEST_MODE ``` must be set to ``` True``` for the ``` ./reset_test_data.sh ``` script to work.

### Run the tests manually inside the docker container

To run a test you are developing, it is useful to run the test inside the docker container to generate the fixtures with -d argument, or to test if the fixtures work with the -l argument. 

For example, to run the fingerprint filters test, without generating the HTML report, and loading the fixtures before the execution of the test, you can use the following command:

``` sh
docker exec -it docker_catalogue_1 /bin/bash -c "cd /deploy/catalogue/tests/units; python run_tests.py -hl -tr -l -t FingerprintFilterTestCase"
```


## Writing tests
If you are new to selenium with python, get started with the following tutorial: https://selenium-python.readthedocs.io/getting-started.html.  
Always consult this documentation first. For example, we are using Implicit Waits of 10 seconds in this project, to know more about that go to https://selenium-python.readthedocs.io/waits.html.

To facilitate discovering the best tag for each element, and to generate the test code, you can use the Selenium IDE extension for chrome: https://www.selenium.dev/selenium-ide/.

Then you can start to create new tests in compliance with Montra following these steps:

 1. Create a new class extending from ``` MontraTestCase ```
 2. Add test code inside a ``` test_* ``` function
 3. Use ``` utils.data.MontraTestData ``` data if needed
 4. Use ``` self.utils ``` functions to do basic tasks like login, open community, etc. For example, for handling modals use ``` utils.wait_element_clickable ``` function
 5. Add the new test to the test suite by importing the created class in the ``` run_tests.py ``` file, and adding it to the ``` TEST_CLASSES ``` list in the correct position
 6. Add a .json fixtures file to ``` emif/fixtures/test_fixtures ``` with the correct database state for the test. To do that, use the -d argument inside the docker container, and verify the test passed after dumping the fixtures file
 7. Congrats, you can push to the repository the new test class file, the corresponding JSON fixture, and the modified ``` run_tests.py ``` file.

Note: Avoid clicks with JavaScript, if you can not click with selenium, always try to scroll to the element or wait for the element.

### Fingerprint Delete Example

Check the first 4 points above in the following example:

```py
from selenium.webdriver.common.by import By

from utils.testcases import MontraTestCase
from utils.data import MontraTestData as data


class FingerprintDeleteTestCase(MontraTestCase):

    def test_fingerprint_delete(self):

        user2 = data.users["user2"]

        # Login as user2
        self.utils.login(user2["username"], user2["password"])

        self.utils.open_community()

        count = self.utils.get_number_of_fingerprints()

        current_fingerprint_acronym = data.fingerprint_acronym + str(count)

        assert current_fingerprint_acronym in self.driver.page_source

        # Open fingerprint to delete
        self.driver.find_element(By.CSS_SELECTOR, "a[data-acronym={}]".format(current_fingerprint_acronym)).click()

        # Open modal Manage/Delete
        self.driver.find_element(By.ID, "managetoolbar").click()
        self.driver.find_element(By.ID, "delete_list_toolbar").click()

        # Click Delete
        element = self.utils.wait_element_clickable((By.ID, "delete_fingerprint"))
        element.click()

        # Wait for modal to disappear
        self.utils.wait_element_invisible((By.ID, "delete_fingerprint"))

        # Home
        self.driver.find_element(By.ID, "home").click()

        # Open community
        self.utils.open_community()

        # Verify fingerprint does not exist
        assert current_fingerprint_acronym not in self.driver.page_source
```
