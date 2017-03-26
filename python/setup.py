from setuptools import setup

# This is the cabb_scheduler Python library.
# Jamie Stevens 2017
# ATCA Senior Systems Scientist
# Jamie.Stevens@csiro.au

setup(name='cabb_scheduler',
      version='1.3',
      description='CABB Scheduling Python Library',
      url='https://github.com/ste616/cabb-schedule-api',
      author='Jamie Stevens',
      author_email='Jamie.Stevens@csiro.au',
      license='MIT',
      packages=[ 'cabb_scheduler' ],
      install_requires=[
          'numpy',
          'requests'
      ],
      zip_safe=False)

# Changelog:
# 2017-03-14, v1.1: Added the parse routine to the schedule library, to read/write in
#    strings instead of just files, and return number of scans read in.
# 2017-03-15, v1.2: Add the ability to query MoniCA for the array name and the
#    frequencies currently in use.
# 2017-03-26, v1.3: Fix a bug in interpreting the Environment code, reading as an
#    integer. Also move the calibrator check into the toString routine.

