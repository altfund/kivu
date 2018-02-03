from setuptools import setup, find_packages

setup(name='kivu',
      version='0.1',
      description='Asset management utilities for python',
      url='https://github.com/altfund/kivu',
      author='Altfund Capital',
      author_email='altfund@altfund.org',
      license='MIT',
      packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
      install_requires=[numpy,
      coinmarketcap
      ],#'pyxi==0.4'],
#      test_suite='pytest',
#      tests_require=['pytest'],
      zip_safe=False)