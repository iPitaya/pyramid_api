rm -rf build
rm -rf dist
rm -rf hichao.egg-info
/home/api2/env/bin/pip uninstall hichao  -y
/home/api2/env/bin/python setup.py clean
/home/api2/env/bin/python setup.py build
/home/api2/env/bin/python setup.py install
