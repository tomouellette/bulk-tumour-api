from setuptools import setup, find_packages

# with open('requirements.txt') as f:
#     requirements = f.read().splitlines()

version = '0.1'

setup(name='bulk-tumour-api',
      version=version,
      python_requires='>3.6',
      description='A python API for accessing and downloading bulk tumour sequencing data stored in a Zenodo repository',
      author='Tom W. Ouellette',
      author_email='t.ouellette@mail.utoronto.ca',
      license='MIT',
      packages=find_packages(),
      #install_requires=requirements,
      include_package_data=True,
)	