# Multi-Agent Framework R&D

This repository is dedicated to research and development of multi-agent frameworks, exploring various use cases and implementations.

## Overview

This project serves as a testing ground for different multi-agent scenarios, architectures, and interactions. The research focuses on developing and evaluating various approaches to multi-agent systems.

## Getting Started

### Prerequisites

- Python 3.x
- Git
- VS Build Tools
- Docker

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AngeloAyranji/multiagent-framework.git
cd multiagent-framework
```

2. Set up a virtual environment:
```bash
# Create a new virtual environment
python -m venv env

# Activate the virtual environment
# On Windows (PowerShell):
.venv/Scripts/Activate.ps1

# On Windows (Command Prompt):
.venv\Scripts\activate.bat

# On Unix or MacOS:
source env/bin/activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Set Environment Variables:
```bash
cp .env.example .env
```

### Verifying Installation

After installation, you can verify your setup by:

1. Ensuring your virtual environment is activated (you should see `(env)` in your terminal prompt)
2. Checking Python version:
```bash
python --version
```
3. Verifying installed packages:
```bash
pip list
```

## Project Structure

```
project/
├── README.md          # Project documentation
├── requirements.txt   # Python dependencies
└── env/              # Virtual environment (not tracked in git)
```