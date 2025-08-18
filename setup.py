from setuptools import setup

setup(
    name="ProlabsRobotics",
    version="0.1.0",
    py_modules=["ProlabsRobotics"],  # this is your single .py file
    install_requires=[
        "pyperclip",
        "pynput",
        "pygetwindow; platform_system=='Windows'"
    ],
    python_requires=">=3.8",
    author="Aarav Jaisingh",
    author_email="aaravjaisingh@gmail.com",
    description="Automation + ChatGPT integration with history, by Prolabs Robotics",
    url="https://github.com/Aarav-111/ProlabsRobotics",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
