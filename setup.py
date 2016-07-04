from setuptools import setup
from setuptools import find_packages


setup(name='optomatic',
      version='0.1',
      description='Scalable distributed hyperparameter optimization in Python',
      author='Erlend Davidson',
      author_email='erlend.davidson@gmail.com',
      url='https://github.com/erlendd/optomatic',
      license='MIT',
      install_requires=['numpy', 'scipy', 'pandas', 'scikit-learn', 'pymongo'],
      packages=find_packages())
