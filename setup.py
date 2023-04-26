from setuptools import find_packages, setup

setup(
    name='src',
    packages=find_packages(),
    version='0.1.0',
    description='Models for analysing Formula 1 teams and drivers\' performances.',
    author='Felipe Oliveira',
    license='MIT',
    install_requires = [
        'numpy',
        'scipy',
        'pandas',
        'seaborn',
        'plotly',
        'SQLAlchemy',
        'pymysql',
        'sqlparse',
        'tqdm',
    ]
)
