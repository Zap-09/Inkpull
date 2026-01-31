# Building
Note: This is mainly for Windows. I can't make one for Mac/Linux cause I don't have those systems. So if someone gets this running in those system, make a pull request. I will add them to the docs.


1. Make sure to have Python installed, I made this with Python `3.13.2`.
2. Clone this repo and `cd` into it.
3. Make a virtual environment. (Optional)
4. Run `pip install -r requirements.txt` <br> and  `pip install pyinstaller`
5. Then run <br>`mkdir PYINSTALLER && pyinstaller -y --workpath PYINSTALLER\build --distpath PYINSTALLER\dist .github\workflows\Inkpull.spec`
6. Now after the building is done you should have a folder called `PYINSTALLER/dist/Inkpull` and your exe and `libs` folder should be there.


[Back to main page](../README.md)