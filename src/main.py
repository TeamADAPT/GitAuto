import argparse
import logging
import subprocess
import os
from typing import List, Tuple

# Custom exception class for GitAuto-specific errors
class GitAutoError(Exception):
    pass

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add file handler
file_handler = logging.FileHandler('gitauto.log')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="GitAuto - Automate Git operations")
    parser.add_argument('--version', action='version', version='%(prog)s 0.2.0')
    parser.add_argument('command', choices=['init', 'status', 'commit', 'branch', 'merge', 'pull', 'push', 'fetch', 'log', 'diff', 'stash'],
                        help='Git command to execute')
    parser.add_argument('--message', '-m', help='Commit message (required for commit command)')
    parser.add_argument('--branch', '-b', help='Branch name (required for branch and merge commands)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--num-commits', '-n', type=int, default=10, help='Number of commits to show in log')
    parser.add_argument('--compare', '-c', nargs=2, metavar=('OLD', 'NEW'), help='Compare two commits or branches')
    return parser.parse_args()

def run_git_command(command: List[str]) -> Tuple[int, str, str]:
    """Run a Git command and return the result."""
    try:
        result = subprocess.run(['git'] + command, check=True, capture_output=True, text=True)
        return 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr
    except FileNotFoundError:
        raise GitAutoError("Git command not found. Please ensure Git is installed and in your PATH.")

def is_git_repository() -> bool:
    """Check if the current directory is a Git repository."""
    return os.path.isdir('.git')

def init_repo():
    """Initialize a new Git repository."""
    if is_git_repository():
        logger.warning("Git repository already exists in this directory.")
        return

    logger.info("Initializing new Git repository...")
    exit_code, output, error = run_git_command(['init'])
    if exit_code == 0:
        logger.info("Git repository initialized successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to initialize Git repository: {error}")

def check_status():
    """Check the status of the Git repository."""
    if not is_git_repository():
        raise GitAutoError("Not a Git repository. Please run 'init' command first.")

    logger.info("Checking Git repository status...")
    exit_code, output, error = run_git_command(['status'])
    if exit_code == 0:
        logger.info("Git status:")
        logger.info(output)
    else:
        raise GitAutoError(f"Failed to check Git status: {error}")

def commit_changes(message: str):
    """Commit changes to the Git repository."""
    if not is_git_repository():
        raise GitAutoError("Not a Git repository. Please run 'init' command first.")

    if not message:
        raise GitAutoError("Commit message is required.")
    
    logger.info(f"Committing changes with message: {message}")
    
    # Check if there are any changes to commit
    status_code, status_output, _ = run_git_command(['status', '--porcelain'])
    if status_code == 0 and not status_output.strip():
        logger.warning("No changes to commit. Working tree clean.")
        return

    # Stage all changes
    stage_exit_code, stage_output, stage_error = run_git_command(['add', '.'])
    if stage_exit_code != 0:
        raise GitAutoError(f"Failed to stage changes: {stage_error}")

    # Commit changes
    commit_exit_code, commit_output, commit_error = run_git_command(['commit', '-m', message])
    if commit_exit_code == 0:
        logger.info("Changes committed successfully.")
        logger.debug(commit_output)
    else:
        raise GitAutoError(f"Failed to commit changes: {commit_error}")

def create_branch(branch_name: str):
    """Create a new branch."""
    if not is_git_repository():
        raise GitAutoError("Not a Git repository. Please run 'init' command first.")

    if not branch_name:
        raise GitAutoError("Branch name is required.")

    logger.info(f"Creating new branch: {branch_name}")
    exit_code, output, error = run_git_command(['checkout', '-b', branch_name])
    if exit_code == 0:
        logger.info(f"Branch '{branch_name}' created successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to create branch: {error}")

def merge_branch(branch_name: str):
    """Merge a branch into the current branch."""
    if not is_git_repository():
        raise GitAutoError("Not a Git repository. Please run 'init' command first.")

    if not branch_name:
        raise GitAutoError("Branch name to merge is required.")

    logger.info(f"Merging branch '{branch_name}' into current branch")
    exit_code, output, error = run_git_command(['merge', branch_name])
    if exit_code == 0:
        logger.info(f"Branch '{branch_name}' merged successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to merge branch: {error}")

def pull_changes():
    """Pull changes from the remote repository."""
    if not is_git_repository():
        raise GitAutoError("Not a Git repository. Please run 'init' command first.")

    logger.info("Pulling changes from remote repository")
    exit_code, output, error = run_git_command(['pull'])
    if exit_code == 0:
        logger.info("Changes pulled successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to pull changes: {error}")

def push_changes():
    """Push changes to the remote repository."""
    if not is_git_repository():
        raise GitAutoError("Not a Git repository. Please run 'init' command first.")

    logger.info("Pushing changes to remote repository")
    exit_code, output, error = run_git_command(['push'])
    if exit_code == 0:
        logger.info("Changes pushed successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to push changes: {error}")

def fetch_changes():
    """Fetch changes from the remote repository."""
    if not is_git_repository():
        raise GitAutoError("Not a Git repository. Please run 'init' command first.")

    logger.info("Fetching changes from remote repository")
    exit_code, output, error = run_git_command(['fetch', '--all'])
    if exit_code == 0:
        logger.info("Changes fetched successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to fetch changes: {error}")

def show_log(num_commits: int):
    """Show commit history."""
    if not is_git_repository():
        raise GitAutoError("Not a Git repository. Please run 'init' command first.")

    logger.info(f"Showing last {num_commits} commits")
    exit_code, output, error = run_git_command(['log', f'-n{num_commits}', '--oneline'])
    if exit_code == 0:
        logger.info("Commit history:")
        logger.info(output)
    else:
        raise GitAutoError(f"Failed to show commit history: {error}")

def show_diff(old: str, new: str):
    """Show differences between commits or branches."""
    if not is_git_repository():
        raise GitAutoError("Not a Git repository. Please run 'init' command first.")

    logger.info(f"Showing differences between {old} and {new}")
    exit_code, output, error = run_git_command(['diff', old, new])
    if exit_code == 0:
        logger.info("Differences:")
        logger.info(output)
    else:
        raise GitAutoError(f"Failed to show differences: {error}")

def stash_changes():
    """Stash changes in the working directory."""
    if not is_git_repository():
        raise GitAutoError("Not a Git repository. Please run 'init' command first.")

    logger.info("Stashing changes")
    exit_code, output, error = run_git_command(['stash'])
    if exit_code == 0:
        logger.info("Changes stashed successfully.")
        logger.debug(output)
    else:
        raise GitAutoError(f"Failed to stash changes: {error}")

def main():
    """Main function to run the GitAuto tool."""
    args = parse_arguments()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        if args.command == 'init':
            init_repo()
        elif args.command == 'status':
            check_status()
        elif args.command == 'commit':
            commit_changes(args.message)
        elif args.command == 'branch':
            create_branch(args.branch)
        elif args.command == 'merge':
            merge_branch(args.branch)
        elif args.command == 'pull':
            pull_changes()
        elif args.command == 'push':
            push_changes()
        elif args.command == 'fetch':
            fetch_changes()
        elif args.command == 'log':
            show_log(args.num_commits)
        elif args.command == 'diff':
            if not args.compare:
                raise GitAutoError("Please provide two commits or branches to compare using the --compare/-c option.")
            show_diff(args.compare[0], args.compare[1])
        elif args.command == 'stash':
            stash_changes()
        else:
            logger.error(f"Unknown command: {args.command}")
    except GitAutoError as e:
        logger.error(str(e))
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        logger.debug("Exception details:", exc_info=True)

if __name__ == "__main__":
    main()