from setuptools import setup, find_packages

setup(
    name='oeaindice',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click==6.6',
    ],
    entry_points='''
        [console_scripts]
        oeaindice=oeaindice.cli:cli
    ''',
)