from setuptools import setup

setup(
    name="ProlabsRobotics",
    version="0.1.0",
    py_modules=["ProlabsRobotics"],
    description="ProlabsRobotics AI library using PySide6 and QtWebEngine to interact with ChatGPT via a browser backend.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Aarav Jaisingh",
    url="https://github.com/Aarav-111/ProlabsRobotics",
    python_requires=">=3.9",
    install_requires=[
        "PySide6>=6.6",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
