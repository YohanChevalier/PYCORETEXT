import os
from pathlib import Path
from datetime import datetime
from tkinter import filedialog

today = datetime.today().strftime("%Y-%m-%d")
path = filedialog.askdirectory()
print(path + "test")