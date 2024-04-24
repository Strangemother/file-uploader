# website

Description for project "website"

## Basic Install

Ensure the environment is created and started.

Create an environment (only if it doesn't exist) we'll call the directory `./env/`:
```bash
$> python -m venv env
```

Activate the environment (for every fresh terminal):
```bash
$> env/scripts/activate.bat
(env) $>
```

Install any requirements (if required):
```bash
$> pip install -r requirements.txt
```

## Run


Run in basic development mode

```py
(env) $> python manage.py runserver
# ...
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

