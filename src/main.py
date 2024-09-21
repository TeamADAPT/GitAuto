import argparse
import logging
import subprocess
import os
from typing import List, Tuple


# Custom exception class for GitAuto-specific errors
class GitAutoError(Exception):
    pass


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add file handler
file_handler = logging.FileHandler("gitauto.log")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="GitAuto - Automate Git operations\n\n"
        "GitAuto is a powerful command-line tool for automating Git operations and streamlining "
        "your development workflow. It provides a set of easy-to-use commands that wrap around Git, "
        "making version control tasks more efficient and less error-prone.\n\n"
        "Available commands:\n"
        "  init      Initialize a new Git repository\n"
        "  status    Show the working tree status\n"
        "  commit    Record changes to the repository\n"
        "  branch    Create a new branch\n"
        "  merge     Join two or more development histories together\n"
        "  pull      Fetch from and integrate with another repository or a local branch\n"
        "  push      Update remote refs along with associated objects\n"
        "  fetch     Download objects and refs from another repository\n"
        "  log       Show commit logs\n"
        "  diff      Show changes between commits, commit and working tree, etc\n"
        "  stash     Stash the changes in a dirty working directory away\n"
        "  list      List all available GitAuto commands",
        epilog="For more information on each command, use: gitauto <command> --help",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.2.0")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Git command to execute"
    )

    # Init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new Git repository",
        description="Initialize a new Git repository in the current directory.",
    )
    init_parser.set_defaults(func=init_repo)
    init_parser.epilog = "Example: gitauto init"

    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show the working tree status",
        description="Display the status of the working tree, showing modified files, "
        "staged changes, and untracked files.",
    )
    status_parser.set_defaults(func=check_status)
    status_parser.epilog = "Example: gitauto status"

    # Commit command
    commit_parser = subparsers.add_parser(
        "commit",
        help="Record changes to the repository",
        description="Commit staged changes to the repository with a message. "
        "You can provide a commit message directly or use a template.",
    )
    commit_parser.add_argument("--message", "-m", help="Commit message")
    commit_parser.add_argument(
        "--template", "-t", action="store_true", help="Use commit message template"
    )
    commit_parser.set_defaults(func=commit_changes)
    commit_parser.epilog = (
        "Examples:\n" "  gitauto commit -m 'Add new feature'\n" "  gitauto commit -t"
    )

    # Branch command
    branch_parser = subparsers.add_parser(
        "branch",
        help="Create a new branch",
        description="Create a new branch with the specified name and switch to it.",
    )
    branch_parser.add_argument(
        "--name", "-n", required=True, help="Name of the new branch"
    )
    branch_parser.set_defaults(func=create_branch)
    branch_parser.epilog = "Example: gitauto branch -n feature-branch"

    # Merge command
    merge_parser = subparsers.add_parser(
        "merge",
        help="Join two or more development histories together",
        description="Merge the specified branch into the current branch. "
        "This combines the changes from the specified branch into your current branch.",
    )
    merge_parser.add_argument(
        "--branch", "-b", required=True, help="Name of the branch to merge"
    )
    merge_parser.set_defaults(func=merge_branch)
    merge_parser.epilog = "Example: gitauto merge -b feature-branch"

    # Pull command
    pull_parser = subparsers.add_parser(
        "pull",
        help="Fetch from and integrate with another repository or a local branch",
        description="Fetch changes from the remote repository and merge them into the current branch. "
        "This is equivalent to running 'git fetch' followed by 'git merge'.",
    )
    pull_parser.set_defaults(func=pull_changes)
    pull_parser.epilog = "Example: gitauto pull"

    # Push command
    push_parser = subparsers.add_parser(
        "push",
        help="Update remote refs along with associated objects",
        description="Push local changes to the remote repository. "
        "This uploads your local commits to the remote repository.",
    )
    push_parser.set_defaults(func=push_changes)
    push_parser.epilog = "Example: gitauto push"

    # Fetch command
    fetch_parser = subparsers.add_parser(
        "fetch",
        help="Download objects and refs from another repository",
        description="Fetch changes from the remote repository without merging them. "
        "This updates your remote-tracking branches.",
    )
    fetch_parser.set_defaults(func=fetch_changes)
    fetch_parser.epilog = "Example: gitauto fetch"

    # Log command
    log_parser = subparsers.add_parser(
        "log",
        help="Show commit logs",
        description="Display the commit history of the repository. "
        "You can specify the number of commits to show.",
    )
    log_parser.add_argument(
        "--num-commits", "-n", type=int, default=10, help="Number of commits to show"
    )
    log_parser.set_defaults(func=show_log)
    log_parser.epilog = "Example: gitauto log -n 5"

    # Diff command
    diff_parser = subparsers.add_parser(
        "diff",
        help="Show changes between commits, commit and working tree, etc",
        description="Display the differences between two commits, branches, or between "
        "the working directory and the last commit.",
    )
    diff_parser.add_argument(
        "--compare",
        "-c",
        nargs=2,
        metavar=("OLD", "NEW"),
        required=True,
        help="Compare two commits or branches",
    )
    diff_parser.set_defaults(func=show_diff)
    diff_parser.epilog = "Example: gitauto diff -c HEAD~1 HEAD"

    # Stash command
    stash_parser = subparsers.add_parser(
        "stash",
        help="Stash the changes in a dirty working directory away",
        description="Temporarily store modified, tracked files in order to change branches. "
        "This allows you to switch branches without committing incomplete work.",
    )
    stash_parser.set_defaults(func=stash_changes)
    stash_parser.epilog = "Example: gitauto stash"

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List all available GitAuto commands",
        description="Display a list of all available GitAuto commands with brief descriptions.",
    )
    list_parser.set_defaults(func=list_commands)

    return parser.parse_args()


def run_git_command(command: List[str]) -> Tuple[int, str, str]:
    """Run a Git command and return the result."""
    try:
        result = subprocess.run(
            ["git"] + command, check=True, capture_output=True, text=True
        )
        return 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr
    except FileNotFoundError:
        raise GitAutoError(
            "Git command not found. Please ensure Git is installed and in your PATH."
        )


def is_git_repository() -> bool:
    """Check if the current directory is a Git repository."""
    return os.path.isdir(".git")


def load_commit_template() -> str:
    """Load the commit message template from file."""
    template_path = os.path.join(os.path.dirname(__file__), "..", "commit_template.txt")
    try:
        with open(template_path, "r") as template_file:
            return template_file.read()
    except FileNotFoundError:
        logger.warning("Commit message template not found. Using default template.")
        return "# <type>: <subject>\n\n# <body>\n\n# <footer>"


def format_commit_message(template: str, message: str) -> str:
    """Format the commit message using the template."""
    formatted_message = template.replace("# <type>: <subject>", message)
    return formatted_message


def validate_commit_message(message: str) -> bool:
    """Validate the commit message format."""
    lines = message.split("\n")
    if not lines:
        return False

    first_line = lines[0]
    if not first_line or len(first_line) > 50 or ":" not in first_line:
        return False

    type_, subject = first_line.split(":", 1)
    if not type_ or not subject.strip():
        return False

    return True


def init_repo(args):
    """Initialize a new Git repository."""
    if is_git_repository():
        logger.warning("Git repository already exists in this directory.")
        return

    logger.info("Initializing new Git repository...")
    exit_code, output, error = run_git_command(["init"])
    if exit_code == 0:
        logger.info("Git repository initialized successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to initialize Git repository: {error}")


def check_status(args):
    """Check the status of the Git repository."""
    if not is_git_repository():
        raise GitAutoError(
            "Not a Git repository. Please run 'gitauto init' to create a new repository."
        )

    logger.info("Checking Git repository status...")
    exit_code, output, error = run_git_command(["status"])
    if exit_code == 0:
        logger.info("Git status:")
        logger.info(output)
    else:
        raise GitAutoError(f"Failed to check Git status: {error}")


def commit_changes(args):
    """Commit changes to the Git repository."""
    if not is_git_repository():
        raise GitAutoError(
            "Not a Git repository. Please run 'gitauto init' to create a new repository."
        )

    if args.template:
        template = load_commit_template()
        if not args.message:
            logger.info("Please enter your commit message:")
            message = input().strip()
        else:
            message = args.message
        commit_message = format_commit_message(template, message)
    elif not args.message:
        raise GitAutoError(
            "Commit message is required. Use -m 'Your message' or -t for template."
        )
    else:
        commit_message = args.message

    if not validate_commit_message(commit_message):
        raise GitAutoError(
            "Invalid commit message format. Please use the format: <type>: <subject>"
        )

    logger.info(f"Committing changes with message: {commit_message}")

    # Check if there are any changes to commit
    status_code, status_output, _ = run_git_command(["status", "--porcelain"])
    if status_code == 0 and not status_output.strip():
        logger.warning("No changes to commit. Working tree clean.")
        return

    # Stage all changes
    stage_exit_code, stage_output, stage_error = run_git_command(["add", "."])
    if stage_exit_code != 0:
        raise GitAutoError(f"Failed to stage changes: {stage_error}")

    # Commit changes
    commit_exit_code, commit_output, commit_error = run_git_command(
        ["commit", "-m", commit_message]
    )
    if commit_exit_code == 0:
        logger.info("Changes committed successfully.")
        logger.debug(commit_output)
    else:
        raise GitAutoError(f"Failed to commit changes: {commit_error}")


def create_branch(args):
    """Create a new branch."""
    if not is_git_repository():
        raise GitAutoError(
            "Not a Git repository. Please run 'gitauto init' to create a new repository."
        )

    if not args.name:
        raise GitAutoError(
            "Branch name is required. Use -n or --name to specify the branch name."
        )

    logger.info(f"Creating new branch: {args.name}")
    exit_code, output, error = run_git_command(["checkout", "-b", args.name])
    if exit_code == 0:
        logger.info(f"Branch '{args.name}' created successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to create branch: {error}")


def merge_branch(args):
    """Merge a branch into the current branch."""
    if not is_git_repository():
        raise GitAutoError(
            "Not a Git repository. Please run 'gitauto init' to create a new repository."
        )

    if not args.branch:
        raise GitAutoError(
            "Branch name to merge is required. Use -b or --branch to specify the branch name."
        )

    logger.info(f"Merging branch '{args.branch}' into current branch")
    exit_code, output, error = run_git_command(["merge", args.branch])
    if exit_code == 0:
        logger.info(f"Branch '{args.branch}' merged successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to merge branch: {error}")


def pull_changes(args):
    """Pull changes from the remote repository."""
    if not is_git_repository():
        raise GitAutoError(
            "Not a Git repository. Please run 'gitauto init' to create a new repository."
        )

    logger.info("Pulling changes from remote repository")
    exit_code, output, error = run_git_command(["pull"])
    if exit_code == 0:
        logger.info("Changes pulled successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to pull changes: {error}")


def push_changes(args):
    """Push changes to the remote repository."""
    if not is_git_repository():
        raise GitAutoError(
            "Not a Git repository. Please run 'gitauto init' to create a new repository."
        )

    logger.info("Pushing changes to remote repository")
    exit_code, output, error = run_git_command(["push"])
    if exit_code == 0:
        logger.info("Changes pushed successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to push changes: {error}")


def fetch_changes(args):
    """Fetch changes from the remote repository."""
    if not is_git_repository():
        raise GitAutoError(
            "Not a Git repository. Please run 'gitauto init' to create a new repository."
        )

    logger.info("Fetching changes from remote repository")
    exit_code, output, error = run_git_command(["fetch", "--all"])
    if exit_code == 0:
        logger.info("Changes fetched successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to fetch changes: {error}")


def show_log(args):
    """Show commit history."""
    if not is_git_repository():
        raise GitAutoError(
            "Not a Git repository. Please run 'gitauto init' to create a new repository."
        )

    logger.info(f"Showing last {args.num_commits} commits")
    exit_code, output, error = run_git_command(
        ["log", f"-n{args.num_commits}", "--oneline"]
    )
    if exit_code == 0:
        logger.info("Commit history:")
        logger.info(output)
    else:
        raise GitAutoError(f"Failed to show commit history: {error}")


def show_diff(args):
    """Show differences between commits or branches."""
    if not is_git_repository():
        raise GitAutoError(
            "Not a Git repository. Please run 'gitauto init' to create a new repository."
        )

    logger.info(f"Showing differences between {args.compare[0]} and {args.compare[1]}")
    exit_code, output, error = run_git_command(
        ["diff", args.compare[0], args.compare[1]]
    )
    if exit_code == 0:
        logger.info("Differences:")
        logger.info(output)
    else:
        raise GitAutoError(f"Failed to show differences: {error}")


def stash_changes(args):
    """Stash changes in the working directory."""
    if not is_git_repository():
        raise GitAutoError(
            "Not a Git repository. Please run 'gitauto init' to create a new repository."
        )

    logger.info("Stashing changes")
    exit_code, output, error = run_git_command(["stash"])
    if exit_code == 0:
        logger.info("Changes stashed successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to stash changes: {error}")


def list_commands(args):
    """List all available GitAuto commands."""
    commands = [
        ("init", "Initialize a new Git repository"),
        ("status", "Show the working tree status"),
        ("commit", "Record changes to the repository"),
        ("branch", "Create a new branch"),
        ("merge", "Join two or more development histories together"),
        ("pull", "Fetch from and integrate with another repository or a local branch"),
        ("push", "Update remote refs along with associated objects"),
        ("fetch", "Download objects and refs from another repository"),
        ("log", "Show commit logs"),
        ("diff", "Show changes between commits, commit and working tree, etc"),
        ("stash", "Stash the changes in a dirty working directory away"),
        ("list", "List all available GitAuto commands"),
    ]

    logger.info("Available GitAuto commands:")
    for cmd, desc in commands:
        logger.info(f"  {cmd:<10} {desc}")


def main():
    """Main function to run the GitAuto tool."""
    args = parse_arguments()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        args.func(args)
    except GitAutoError as e:
        logger.error(str(e))
        if "Not a Git repository" in str(e):
            logger.info(
                "Tip: Use 'gitauto init' to create a new Git repository in the current directory."
            )
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        logger.debug("Exception details:", exc_info=True)
        logger.info(
            "If this error persists, please report it to the GitAuto development team."
        )


if __name__ == "__main__":
    main()
