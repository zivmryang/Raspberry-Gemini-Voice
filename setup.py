from setuptools import setup, find_packages

setup(
    name="raspberry_gemini_voice",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'vosk',
        'espeak',
        'pyaudio',
        'flask',
        'requests',
        'sqlite3',
        'python-dotenv'
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'raspberry-gemini-voice=raspberry_gemini_voice.src.main:main',
        ],
    },
)
