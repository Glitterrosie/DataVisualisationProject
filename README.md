# DataVisualisationProject - CO2 Emissions
## Project Description
This is a project developed together in the course "Data Visualisation" at Aarhus University. The goal is to implement an interactive visualisation to show a dataset of our choosing.

## Deployment
You can access the hosted app here: https://glitterrosie-datavisualisationproject-srcmain-qbhprc.streamlit.app/

The app gets automatically re-deployed if changes are pushed to main.

## Setup
### Clone and Setup the Repository locally
1. You can find the Repository holding the code [here](https://github.com/Glitterrosie/DataVisualisationProject).
2. In order for the next steps to work you need to have git installed. You can find a tutorial [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
3. Verifiy that git is running on your machine by running `git --version` in the terminal.
4. Now you can clone the repository. On GitHub go to Code and copy the http address.
5. Now go to your terminal and navigate to the location where you can to put the code.
6. Enter `git clone copied-http-here`, to clone the repo in this location.
7. Now you can open this folder in e.g. Visual Studio Code.


### Create and activate your virtual environment
We need a bunch of libraries to implement the visualisation. In order to have them locally running and also synchronized across our different computers, you need to setup a **virtual environment**. In this environment all dependencies are installed.
1. The virtual environment (venv) is already initialized. You only need to activate it
- Linux/Mac OS: `source venv/bin/activate`
- Windows: `venv\scripts\activate`
2. Once activated the virtual environment hold every dependency defined in the `requirements.txt`.
3. To add a library (dependency): 
    1. `pip install package_name`
    2. `pip freeze > requirements.txt`
4. To remove a library (dependency):
    1. `pip uninstall package_name`
    2. `pip freeze > requirements.txt`

For further details visit this [page](https://www.reddit.com/r/learnpython/comments/m3exau/setting_up_first_python_project_environment/)

### Run Streamlit app
To run the streamlit app you must follow these steps:
1. Make sure your venv is activated.
2. Run `streamlit run src/main.py`
3. This should have opened a new page in you browser with the running application.

Further documentation on streamlit can be found [here](https://docs.streamlit.io/).

### How to use Git for this project
Git is a version control tool that enables us to work on our features seperatly and then merge them together. If you want to work on a feature you need to follow these steps:
1. Create a **branch**. A branch is a copy of the current project that you have locally on your PC. Changing stuff on this branch is not going to change anything on the production version of the code. Be carefull not to work on the branch `main`, as this is the production version.
2. Name this branch in a way, that we can easily see which feature is implemented on this branch.
3. This branch is now you playground. You can change and adapt anything you want.
4. To save you progress you need to **commit** and **push**. In committing you transfer all changes you have on your local branch to the online version of the branch. This again does not change the production code, it just makes your changes available for everyone. When committing, add a message to indicate what has happened.
5. If you want to update any branch with the pushed changes, you need to **pull**.
6. If you are finished with your code, you can create a **pullrequest** on github, to **merge** your changes into the production version.

A detailed tutorial on using git with Visual Sudio Code can be found [here](https://www.youtube.com/watch?v=i_23KUAEtUM).

