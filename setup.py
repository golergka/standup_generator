from setuptools import setup, find_packages

setup(
    name="standup_generator",
    version="0.1.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[],
    entry_points={
        "console_scripts": [
            "standup_generator = standup_generator.main:main",
        ],
    },
)
