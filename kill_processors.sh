kill -9 `ps -Af | grep processor.py | grep -v grep | awk '{print $2}'`
