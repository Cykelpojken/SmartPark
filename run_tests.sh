#!/bin/bash

python -m pytest --junitxml=xml/python_tests.xml -q --cmdopt=type2 tests/space_detection_tests.py
pycodestyle --exclude PyRoboViz,car_controller,lidarServer . > xml/pep8.log
# printf '%d\n' $?
