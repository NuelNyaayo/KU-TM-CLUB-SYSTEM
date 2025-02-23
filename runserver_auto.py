import subprocess
import webbrowser
import time

# Run Django server in the same VS Code terminal
subprocess.Popen("python manage.py runserver", shell=True)

# Wait a few seconds to let the server start
time.sleep(2)

# Open the browser with the default system browser
webbrowser.open("http://127.0.0.1:8000/")
