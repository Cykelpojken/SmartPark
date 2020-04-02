#!/bin/bash
pytest --junitxml=javaxml.xml
python -m pytest -q --cmdopt=type2 tests/space_detection_tests.py
