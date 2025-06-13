from setuptools import setup, find_packages

setup(
    name="ragfant",
    version="0.1",
    packages=find_packages(),
    python_requires='>=3.9,<3.11',
    install_requires=[
        'streamlit==1.31.0',
        'openai==1.12.0',
        'python-dotenv==1.0.0',
        'requests==2.31.0',
        'numpy==1.24.3',
        'pandas==1.5.3',
        'scipy==1.10.1',
        'rich==13.7.0'
    ]
)