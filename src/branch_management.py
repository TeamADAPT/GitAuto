import subprocess
from typing import List, Tuple


class BranchManager:
    @staticmethod
    def run_git_command(command: List[str]) -> Tuple[int, str, str]:
        """Run a Git command and return the result."""
        try:
            result = subprocess.run(
                ["git"] + command, check=True, capture_output=True, text=True
            )
            return 0, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr

    @staticmethod
    def list_branches() -> List[str]:
        """List all branches in the repository."""
        exit_code, output, _ = BranchManager.run_git_command(["branch", "--list"])
        if exit_code == 0:
            return [branch.strip() for branch in output.split("\n") if branch]
        return []

    @staticmethod
    def create_branch(name: str) -> bool:
        """Create a new branch."""
        exit_code, _, _ = BranchManager.run_git_command(["branch", name])
        return exit_code == 0

    @staticmethod
    def delete_branch(name: str, force: bool = False) -> bool:
        """Delete a branch."""
        command = ["branch", "-D" if force else "-d", name]
        exit_code, _, _ = BranchManager.run_git_command(command)
        return exit_code == 0

    @staticmethod
    def rename_branch(old_name: str, new_name: str) -> bool:
        """Rename a branch."""
        exit_code, _, _ = BranchManager.run_git_command(
            ["branch", "-m", old_name, new_name]
        )
        return exit_code == 0

    @staticmethod
    def get_current_branch() -> str:
        """Get the name of the current branch."""
        exit_code, output, _ = BranchManager.run_git_command(
            ["rev-parse", "--abbrev-ref", "HEAD"]
        )
        if exit_code == 0:
            return output.strip()
        return ""

    @staticmethod
    def switch_branch(name: str) -> bool:
        """Switch to a different branch."""
        exit_code, _, _ = BranchManager.run_git_command(["checkout", name])
        return exit_code == 0

    @staticmethod
    def merge_branch(source: str, target: str = None) -> bool:
        """Merge a source branch into the target branch (or current branch if not specified)."""
        if target:
            BranchManager.switch_branch(target)
        exit_code, _, _ = BranchManager.run_git_command(["merge", source])
        return exit_code == 0
