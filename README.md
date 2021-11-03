# Unit-Estimator-ThousandEyes
Tool to estimate unit consumption for ThousandEyes

Creates Excel sheet containing separate tabs for each account group and estimates cost per test following ThousandEyes billing algorithm per test-type.

Requirements:
xlsxwriter (https://xlsxwriter.readthedocs.io/)

Usage:
1. Add auhentication (email/token) to script
2. python3 unit_estimator.py
3. Excel file will be placed in same directory when complete (may take up to an hour depending on size)
