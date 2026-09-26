# Source Code

> All project code goes here. Structure this folder as your solution grows.

---

## 📁 Suggested Structure

Adapt this to your project type:

```
src/
├── README.md           ← This file — describe what the code does
├── .bobignore          ← Prevents Bob from reading sensitive files
├── .gitignore          ← Prevents secrets from being committed
│
├── (your project files)
│
└── tests/
    └── (your test files)
```

---

## 🚀 Getting Started

> Fill this in as you build your project.

### Prerequisites

```bash
# List dependencies here
# e.g.:
# node >= 18
# python >= 3.11
# docker
```

### Installation

```bash
# Steps to install and run your project
# e.g.:
# npm install
# npm run dev
```

### Running Tests

```bash
# How to run the test suite
# e.g.:
# npm test
# pytest tests/
```

---

## 🤖 IBM Bob 2.0 Usage in This Code

> Document how Bob contributed to building this code.
> This feeds into your IBM Bob Usage Statement for submission.

| File/Module | How Bob Helped | Bob Feature Used |
|------------|---------------|-----------------|
| | | |
| | | |

---

## ⚠️ Credential Safety

- **Never hardcode API keys, passwords, or secrets** in any file in this directory
- Use environment variables: `process.env.API_KEY` or `os.environ['API_KEY']`
- All secrets belong in `.env` (which is in `.gitignore` and `.bobignore`)
- IBM Cloud credential exposure = account suspension

### Required `.gitignore` entries:
```
.env
.env.*
credentials.json
ibm-credentials.env
*.key
*.pem
```

### Required `.bobignore` entries:
```
.env
.env.*
credentials.json
ibm-credentials.env
```
