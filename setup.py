from setuptools import setup

setup(name='kivu',
      version='0.1',
      description='Asset management utilities for python',
      url='https://github.com/altfund/kivu',
      author='Altfund Capital',
      author_email='altfund@altfund.org',
      license='MIT',
      packages=['kivu'],
      install_requires=['pyxi==0.4'],
      zip_safe=False)