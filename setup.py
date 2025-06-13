from setuptools import setup, find_packages

setup(
    name="ragfant",
    version="0.1",
    packages=find_packages(),
    python_requires='>=3.10,<3.11',
    install_requires=[
        'streamlit==1.32.0',
        'openai==1.12.0',
        'python-dotenv==1.0.1',
        'requests==2.31.0',
        'numpy==1.24.4',  # Last version with good py3.10 wheels
        'pandas==2.0.3',  # Good py3.10 support
        'scipy==1.10.1',  # Last version with good py3.10 wheels
        'rich==13.7.0'
    ]
)