
##### When you create a new Python project or pull down a project - you need to install a fresh Python environment:

```
python -m venv local_python_environment
```

------------------------------------------------------------------------------------------------------------------------------

##### Activate that environment using the following command in the folder directory

```
.\local_python_environment\Scripts\activate
```

------------------------------------------------------------------------------------------------------------------------------

##### Install all packages from your requirements.txt using the command within your local environment

```
(local_python_environment) pip install -r requirements.txt
```

------------------------------------------------------------------------------------------------------------------------------

##### Before pushing to GitHub create a requirements.txt file using 

```
pip freeze > requirements.txt
```

------------------------------------------------------------------------------------------------------------------------------

##### Also you can keep on updating it along with package installation such as

```
pip install requests && pip freeze > requirements.txt
```
