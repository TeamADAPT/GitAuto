import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from src.main import (
    run_git_command,
    is_git_repository,
    init_repo,
    check_status,
    commit_changes,
    create_branch,
    merge_branch,
    pull_changes,
    push_changes,
    fetch_changes,
    show_log,
    show_diff,
    stash_changes,
    GitAutoError,
    parse_arguments,
)


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    old_dir = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old_dir)


def test_is_git_repository(temp_dir):
    assert not is_git_repository()
    os.mkdir(".git")
    assert is_git_repository()


def test_init_repo(temp_dir, capsys):
    init_repo()
    captured = capsys.readouterr()
    assert "Git repository initialized successfully" in captured.out
    assert is_git_repository()


def test_check_status(temp_dir, capsys):
    init_repo()
    check_status()
    captured = capsys.readouterr()
    assert "Git status:" in captured.out


def test_commit_changes(temp_dir, capsys):
    init_repo()
    with open("test_file.txt", "w") as f:
        f.write("Test content")
    commit_changes("Initial commit")
    captured = capsys.readouterr()
    assert "Changes committed successfully" in captured.out


def test_create_branch(temp_dir, capsys):
    init_repo()
    create_branch("test-branch")
    captured = capsys.readouterr()
    assert "Branch 'test-branch' created successfully" in captured.out


def test_merge_branch(temp_dir, capsys):
    init_repo()
    create_branch("test-branch")
    with open("test_file.txt", "w") as f:
        f.write("Test content")
    commit_changes("Test commit")
    run_git_command(["checkout", "main"])
    merge_branch("test-branch")
    captured = capsys.readouterr()
    assert "Branch 'test-branch' merged successfully" in captured.out


@patch("subprocess.run")
def test_pull_changes(mock_run, temp_dir, capsys):
    mock_run.return_value = MagicMock(
        returncode=0, stdout="Changes pulled successfully"
    )
    init_repo()
    pull_changes()
    captured = capsys.readouterr()
    assert "Changes pulled successfully" in captured.out


@patch("subprocess.run")
def test_push_changes(mock_run, temp_dir, capsys):
    mock_run.return_value = MagicMock(
        returncode=0, stdout="Changes pushed successfully"
    )
    init_repo()
    push_changes()
    captured = capsys.readouterr()
    assert "Changes pushed successfully" in captured.out


@patch("subprocess.run")
def test_fetch_changes(mock_run, temp_dir, capsys):
    mock_run.return_value = MagicMock(
        returncode=0, stdout="Changes fetched successfully"
    )
    init_repo()
    fetch_changes()
    captured = capsys.readouterr()
    assert "Changes fetched successfully" in captured.out


@patch("subprocess.run")
def test_show_log(mock_run, temp_dir, capsys):
    mock_run.return_value = MagicMock(
        returncode=0, stdout="Commit 1\nCommit 2\nCommit 3"
    )
    init_repo()
    show_log(3)
    captured = capsys.readouterr()
    assert "Commit history:" in captured.out
    assert "Commit 1" in captured.out
    assert "Commit 2" in captured.out
    assert "Commit 3" in captured.out


@patch("subprocess.run")
def test_show_diff(mock_run, temp_dir, capsys):
    mock_run.return_value = MagicMock(returncode=0, stdout="Diff between commits")
    init_repo()
    show_diff("commit1", "commit2")
    captured = capsys.readouterr()
    assert "Differences:" in captured.out
    assert "Diff between commits" in captured.out


@patch("subprocess.run")
def test_stash_changes(mock_run, temp_dir, capsys):
    mock_run.return_value = MagicMock(returncode=0, stdout="Changes stashed")
    init_repo()
    stash_changes()
    captured = capsys.readouterr()
    assert "Changes stashed successfully" in captured.out


def test_gitauto_error():
    with pytest.raises(GitAutoError):
        raise GitAutoError("Test error")


def test_parse_arguments():
    args = parse_arguments(["commit", "-m", "Test commit"])
    assert args.command == "commit"
    assert args.message == "Test commit"

    args = parse_arguments(["branch", "-b", "test-branch"])
    assert args.command == "branch"
    assert args.branch == "test-branch"

    args = parse_arguments(["log", "-n", "5"])
    assert args.command == "log"
    assert args.num_commits == 5

    args = parse_arguments(["diff", "-c", "commit1", "commit2"])
    assert args.command == "diff"
    assert args.compare == ["commit1", "commit2"]

    with pytest.raises(SystemExit):
        parse_arguments(["invalid-command"])


if __name__ == "__main__":
    pytest.main()
