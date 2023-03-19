# Standup Generator

This generator will help you create a standup report for your team based on your commit history.

## Usage

Set up `OPENAI_API_KEY` environment variable with your OpenAI API key and then run this script in the directory you want to prepare standup update for.

- `-d` or `--days` - number of days to look back for commits. If this option is not specified, than the last workday will be looked up, with special handling for weekends.

## Project Structure

```
standup_generator/
│
├── .gitignore
├── pyproject.toml
├── README.md
├── setup.py
└── src/
    └── standup_generator/
        ├── init.py
        └── main.py
```

- `.gitignore`: A standard Python `.gitignore` file to avoid committing unwanted files.
- `pyproject.toml`: This file is used to manage dependencies and specify the required Python version. We use Poetry for dependency management.
- `README.md`: A description of your project, installation instructions, usage, and any other relevant information.
- `setup.py`: This file is used to make your project installable via `pip` and to register the script as a global command.
- `src/standup_generator/`: This is where your actual project code should be placed.
- `src/standup_generator/__init__.py`: Empty file that is used to mark a directory as a Python package. It allows the Python interpreter to treat the directory as a package, which means you can import modules and functions from this directory in other Python scripts.

## Development

To work with the project, you will need to have Poetry installed (https://python-poetry.org/docs/#installation).

To install the project dependencies:

```bash
poetry install
```

To run the project:

```bash
poetry run standup_generator
```

To build and package the project:

```bash
poetry build
```

To install the project locally as a global command:

```bash
pip install --editable .
```

Now, you can run the command from anywhere in your system:

```bash
standup_generator
```

Don't forget to replace `standup_generator` with the desired command name specified in `setup.py`.

## Dependencies and poetry.lock

This project uses [Poetry](https://python-poetry.org/) for dependency management. The `poetry.lock` file contains information about the exact versions of the dependencies used in the project. It is recommended to commit this file to the repository to ensure consistent behavior across different environments.

When you install the project dependencies using `poetry install`, Poetry will use the versions specified in the `poetry.lock` file. If you want to update the dependencies to their latest versions, you can run `poetry update`.
