# Git hooks for Godot Engine

This folder contains Git hooks meant to be installed locally by Godot Engine
contributors to make sure they comply with our requirements.

## List of hooks

- Pre-commit hook for `black`: Applies `black` to the staged Python files
  before accepting a commit.

## Installation

Copy all the files from this folder into your `.git/hooks` folder, and make
sure the hooks and helper scripts are executable.

#### Linux/MacOS

The hooks rely on bash scripts and tools which should be in the system `PATH`,
so they should work out of the box on Linux/macOS.

##### black
- Python installation: make sure Python is added to the `PATH`
- Install `black` - in any console: `pip3 install black`
