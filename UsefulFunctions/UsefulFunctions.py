import os
import pathlib
import yaml
from yaml.loader import SafeLoader

def GetProjectDirectory():
    parent_directory = str(pathlib.Path(__file__).parent.absolute()).split('/')[-1]
    project_directory = str(pathlib.Path(__file__).parent.absolute()).split(parent_directory)[0]
    return parent_directory, project_directory

def ChangeDirectory():
    ProjectDirectory, ParentDirectory = GetProjectDirectory()
    WorkingDirectory = os.path.join(ProjectDirectory, ParentDirectory)
    try:
        os.chdir("%s/"%(WorkingDirectory))
    except FileNotFoundError:
        os.system("pwd")

def LoadYaml2Dictionary(YAML_FILE_LOCATION):
    with open(YAML_FILE_LOCATION) as f:
        data = yaml.load(f, Loader=SafeLoader)
    print(data['Problem']['Type'])
    return data

def DomainSetup(DICTIONARY):
    
    pass