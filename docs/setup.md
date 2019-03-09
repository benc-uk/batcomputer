# Batcomputer - End to End Setup
!TODO! Words here

## Prereqs
- Python 3.6 
  - Earlier versions of Python can **NOT** be used
  - Python for Windows or the Python that comes with WSL can be used
- Azure CLI (Only for creating Azure ML Workspace)

# Python Environment
It's strongly advised to use a Python [virtual environment](https://docs.python.org/3.6/tutorial/venv.html), but it is not mandatory. If you are comfortable with using Python or have an existing virtual environment setup that you use, then that can used instead.

To create a virtual environment and install Python packages/modules  

From root of batcomputer project directory
- `python -m venv pyenv`  
  (**WARNING!** If using WSL, run `python3 -m venv pyenv`)
- `source pyenv/bin/activate` (Linux/WSL)  
  OR
- `.\pyenv\Scripts\activate` (Windows)
- `pip install -r aml/requirements.txt`
- `pip install -r model-api/requirements.txt`

