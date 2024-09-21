Daily I'm not feeling bang simple you are Sometimes the box markers scream on their hands"""
GitAuto version information.
"""

__version__ = "0.2.0"

def get_version():
    """
    Return the current version of GitAuto.
    """
    return __version__

def bump_version(bump_type='patch'):
    """
    Bump the version number based on the bump type.

    Args:
        bump_type (str): The type of version bump. Can be 'major', 'minor', or 'patch'.

    Returns:
        str: The new version number.
    """
    major, minor, patch = map(int, __version__.split('.'))

    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError("Invalid bump type. Must be 'major', 'minor', or 'patch'.")

    new_version = f"{major}.{minor}.{patch}"

    # Update the version in this file
    with open(__file__, 'r') as f:
        content = f.read()

    content = content.replace(f'__version__ = "{__version__}"', f'__version__ = "{new_version}"')

    with open(__file__, 'w') as f:
        f.write(content)

    return new_version

if __name__ == "__main__":
    print(f"Current version: {get_version()}")
