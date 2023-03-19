import os
import logging
import datetime
import subprocess
import git
import sys
import openai

# Read logging level from environment variable
log_level = os.environ.get("LOG_LEVEL", "ERROR")
numeric_level = getattr(logging, log_level.upper(), logging.INFO)

logging.basicConfig(level=numeric_level)

# Get command line parameters
days_period = None
if "-d" in sys.argv:
    index = sys.argv.index("-d")
    if len(sys.argv) > index + 1:
        days_period = sys.argv[index + 1]

# Set up OpenAI API key
api_key = os.environ.get("OPENAI_API_KEY")
if api_key is None:
    print("ERROR: OPENAI_API_KEY environment variable is not defined.")
    print("Please obtain an API key from OpenAI and set the environment variable in your shell's configuration file (e.g., .bashrc, .zshrc).")
    print("The environment variable should be set securely and not hard-coded in scripts.")
    print("You can set the environment variable like this (replace <your-api-key> with your actual key):")
    print("export OPENAI_API_KEY=<your-api-key>")
    raise SystemExit(1)

openai.api_key = api_key

# Configuration
try:
    git_repo_path = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip()
    logging.debug(f"Git repository path: {git_repo_path}")
except subprocess.CalledProcessError:
    print("ERROR: You are not in a git repository. Please go to a git repository and run the script again.")
    raise SystemExit(1)

try:
    git_username = subprocess.check_output(["git", "config", "--global", "user.name"]).decode().strip()
except subprocess.CalledProcessError:
    print("ERROR: Could not detect your git username.")
    raise SystemExit(1)

# Function to get start date based on whether it's Monday or not
def get_start_date():
    today = datetime.datetime.today()
    weekday = today.weekday()
    if days_period is not None:
        return today - datetime.timedelta(days=int(days_period))
    # Monday
    if weekday == 0:
        return today - datetime.timedelta(days=4)
    # Sunday
    elif weekday == 6:
        return today - datetime.timedelta(days=3)
    # Saturday
    elif weekday == 5:
        return today - datetime.timedelta(days=2)
    else:
        return today - datetime.timedelta(days=1)

# Function to get your recent Git commits
def get_recent_commits(repo: git.Repo, start_date, username) -> list[git.Commit]:
    print("Retrieving recent commits...")
    commits = list(repo.iter_commits(since=start_date, author=username, all=True))
    print(f"Found {len(commits)} commits.")
    return commits

"""
Group commits by branch name
"""
def group_commits(repo: git.Repo, commits: list[git.Commit]) -> dict:
    print("Grouping commits...")
    result = {}
    for commit in commits:
        branch_split = repo.git.branch('-a', '--contains', commit.hexsha).split()
        if len(branch_split) == 0:
            continue
        branch_name = branch_split[-1]
        # Remove remotes/origin/ or similar prefix but retain all other slashes
        branch_name = branch_name.split("/", 2)[-1]
        if branch_name not in result:
            result[branch_name] = []
        # Only use first line of commit message
        commit_message = commit.message.splitlines()[0]
        result[branch_name].append(commit_message)
    print(f"Found {len(result)} branches.")
    return result

# Function to generate stand-up message using OpenAI API
def generate_standup_message(repo: git.Repo, commits: list[git.Commit]):
    grouped_commits = group_commits(repo, commits)
    updates = []

    for branch_name, commits in grouped_commits.items():
        prompt="""Generate a stand-up update for commits from the past day based on one branch.
Update should contain the task name, and summary of all commits on that branch, separated by a dash.
Task name should be extracted from the branch name.
Update should be a single line no longer than one line.

Examples:

Branch
feature/implement-standup-generator
Commits
feat: standup generator core functionality
fix: fixed compilation
fix: fixed running ide
Update
feat: implement stand-up generator — core functionality, fixes

Branch
ST-1234-fix-registration-buttons
Commits
fix: fixed login button
fix: fixed logout button
Update
ST-1234 — fix registration buttons — fixed some of the buttons

Branch
perf/autosave-optimization
Commits
perf: optimized autosave pre-delay
perf: optimized autosave post-delay
fix: fixed autosave
Update
perf: autosave optimization — optimized delays

Branch
chore/update-dependencies
Commits
chore: updated React
chore: updated TypeScript
chore: updated OpenAI API
Update
chore: update dependencies — updated some of the dependencies

Branch
feat/add-web-application
Commits:
ci: renamed project
ci: fixed circleci config
ci: changed docker image
ci: fixed flag for build
ci: changed docker image back
Revert "ci: changed docker image"
fix: parallel tests
Revert "fix: parallel tests"
feat: added tsconfig
feat: added prettier config
chore: test config
ci: jest config
Update
feat: add web application — CI updates and configuration

Branch
ST-54321-repaint-splash-screen
Commits
style: changed splash screen background color
style: changed splash screen text color
style: changed splash screen logo
Update
ST-54321 — repaint splash screen — changed visual style

Using template from the example above, generate update from following history:

Branch"""

        print(f"Got {branch_name} with following commits:")
        for commit in commits:
            print(f"  {commit}")
        print("Generating update...")
        prompt += branch_name + "\n"
        prompt += "Commits\n"
        for commit in commits:
            prompt += f"{commit}\n"
        prompt += "\nUpdate\n"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n"]
        )
        logging.info(f"Response: {response}")
        updates.append(response.choices[0].text.strip())

    # Concatenate all updates with newlines
    return "\n".join(updates)

def main():
    start_date = get_start_date()
    repo = git.Repo(git_repo_path)
    commits = get_recent_commits(repo, start_date, git_username)
    
    if len(commits) > 0:
        standup_message = generate_standup_message(repo, commits)
        print("Stand-up update:")
        print(standup_message)
    else:
        print("No commits found.")

if __name__ == "__main__":
    main()