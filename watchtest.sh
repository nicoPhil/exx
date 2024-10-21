#!/bin/bash

# Watch for changes in .py files and rerun checks
find . -name '*.py' | entr -rc bash -c '

    echo "Running checks..."
    ruff check 
    if [ $? -ne 0 ]; then
        echo "Ruff checks failed!"
        exit 1
    fi

    #ruff format 
    if [ $? -ne 0 ]; then
        echo "Ruff format failed!"
        exit 1
    fi

    mypy main.py 
    if [ $? -ne 0 ]; then
        echo "Mypy checks failed!"
        exit 1
    fi

    pytest --asyncio-mode=auto
    if [ $? -ne 0 ]; then
        echo "Pytest checks failed!"
        exit 1
    fi

    echo "All checks passed!"
'
