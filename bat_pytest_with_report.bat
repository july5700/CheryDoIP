@echo off
echo Running pytest and generating Allure results...
python -m pytest --alluredir=allure-results

echo Restoring history...
if exist allure-report\history (
    xcopy /E /I /Y allure-report\history allure-results\history
)

echo Generating Allure report...
allure generate allure-results -o allure-report --clean

echo Report generation completed!
pause