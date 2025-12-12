@echo on
call venv\Scripts\activate.bat
allure serve .\allure-results\
pause