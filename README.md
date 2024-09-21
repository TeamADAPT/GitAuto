# GitAuto

GitAuto is a powerful command-line tool for automating Git operations and streamlining your development workflow. It provides a set of easy-to-use commands that wrap around Git, making version control tasks more efficient and less error-prone.

## Features

- Initialize Git repositories
- Check repository status
- Commit changes with automatic staging
- Create and manage branches
- Merge branches
- Pull and push changes
- Fetch updates from remote repositories
- View commit history
- Show differences between commits or branches
- Stash changes
- Use commit message templates

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/gitauto.git
   cd gitauto
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

GitAuto provides a simple command-line interface with subcommands for different Git operations. Here's how to use it:

```
python src/main.py <command> [options]
```

To see the full list of available commands and global options, use:

```
python src/main.py --help
```

For detailed information on a specific command, use:

```
python src/main.py <command> --help
```

### Available Commands

- `init`: Initialize a new Git repository in the current directory.
- `status`: Display the status of the working tree, showing modified files, staged changes, and untracked files.
- `commit`: Record changes to the repository with a message.
- `branch`: Create a new branch with the specified name.
- `merge`: Merge the specified branch into the current branch.
- `pull`: Fetch changes from the remote repository and merge them into the current branch.
- `push`: Push local changes to the remote repository.
- `fetch`: Fetch changes from the remote repository without merging them.
- `log`: Display the commit history of the repository.
- `diff`: Display the differences between two commits or branches.
- `stash`: Temporarily store modified, tracked files in order to change branches.

### Examples

1. Initialize a new Git repository:
   ```
   python src/main.py init
   ```

2. Check the status of your repository:
   ```
   python src/main.py status
   ```

3. Commit changes with a message:
   ```
   python src/main.py commit --message "feat: add new feature"
   ```

4. Commit changes using a template:
   ```
   python src/main.py commit --template
   ```

5. Create a new branch:
   ```
   python src/main.py branch --name new-feature
   ```

6. Merge a branch into the current branch:
   ```
   python src/main.py merge --branch feature-branch
   ```

7. Pull changes from remote:
   ```
   python src/main.py pull
   ```

8. Push changes to remote:
   ```
   python src/main.py push
   ```

9. View commit history (last 5 commits):
   ```
   python src/main.py log --num-commits 5
   ```

10. Show differences between two commits:
    ```
    python src/main.py diff --compare HEAD~1 HEAD
    ```

11. Stash changes:
    ```
    python src/main.py stash
    ```

## Commit Message Templates

GitAuto supports the use of commit message templates to encourage consistent and informative commit messages. To use a template:

1. Create a file named `commit_template.txt` in the project root directory.
2. Add your desired template to this file. For example:
   ```
   # <type>: <subject>

   # <body>

   # <footer>

   # Type can be:
   #   feat     (new feature)
   #   fix      (bug fix)
   #   docs     (changes to documentation)
   #   style    (formatting, missing semi colons, etc; no code change)
   #   refactor (refactoring production code)
   #   test     (adding missing tests, refactoring tests; no production code change)
   #   chore    (updating grunt tasks etc; no production code change)
   ```
3. When committing, use the `--template` flag:
   ```
   python src/main.py commit --template
   ```

This will prompt you to enter your commit message following the template structure.

## Development

To set up the development environment:

1. Follow the installation steps above.
2. Install development dependencies:
   ```
   pip install -r requirements-dev.txt
   ```
3. Run tests:
   ```
   pytest
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape GitAuto.
- Inspired by the need for simpler Git workflows in development teams.

For more detailed information about the project, its current status, and future plans, please refer to the [GitAuto_Details.md](GitAuto_Details.md) file.
