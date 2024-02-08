from setuptools import setup, find_packages

setup(
    name='auto_prompt',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
)