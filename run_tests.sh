#!/bin/bash 
python -m pytest --junitxml=python_tests.xml -q --cmdopt=type2 tests/space_detection_tests.py
