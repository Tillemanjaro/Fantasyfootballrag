from setuptools import setup, find_packages

setup(
    name="ragfant",
    version="0.1",
    packages=find_packages(),
    python_requires='>=3.13',
    install_requires=[
        'streamlit==1.32.0',
        'openai==1.12.0',
        'python-dotenv==1.0.1',
        'requests==2.31.0',
        'numpy==1.26.4',  # Pre-built wheel available for Python 3.13
        'pandas==2.1.4',  # Compatible with numpy 1.26.4
        'scipy==1.11.4',  # Last stable version for this combination
        'rich==13.7.0'
    ]
)