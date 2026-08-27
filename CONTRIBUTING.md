# 🤝 Contributing

Thank you for your interest in contributing to the **Energy Consumption Forecasting System**.

Contributions are welcome, including bug fixes, improvements, documentation updates, testing, machine-learning enhancements, and new analytics features.

---

## 📋 Before You Start

Please read:

* `README.md` — Project overview and setup
* `PRD.md` — Product requirements and project scope
* `SECURITY.md` — Security and vulnerability reporting

Before starting significant work, make sure your proposed change fits the project's goals.

---

## 🚀 Getting Started

### 1. Fork the Repository

Create your own fork of the project on GitHub.

### 2. Clone Your Fork

```bash
git clone <your-fork-url>
cd energy-consumption-forecasting
```

### 3. Create a Branch

Use a descriptive branch name:

```bash
git checkout -b feature/add-sarima-model
```

Examples:

```text
feature/add-transformer-model
feature/improve-anomaly-detection
feature/add-weather-features
fix/upload-validation
fix/forecast-api
docs/improve-readme
test/add-forecast-tests
```

---

## 🛠️ Development Setup

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables using:

```text
.env.example
```

Never commit your real `.env` file.

---

## 🧪 Run Tests

Before submitting a contribution:

```bash
pytest -v
```

All existing tests should pass.

If you introduce a new feature, add appropriate tests whenever possible.

---

## 🧹 Code Quality

Please keep contributions:

* Readable
* Modular
* Documented where necessary
* Consistent with the existing architecture
* Free from unnecessary dependencies

Avoid:

* Hardcoded secrets
* Hardcoded forecast results
* Unnecessary global state
* Debugging code
* Unused imports
* Exposing internal exceptions to users

---

## 🧠 Machine Learning Contributions

When adding a forecasting model:

1. Add the model to the appropriate ML module.
2. Ensure it follows the existing model interface.
3. Use chronological validation.
4. Do not shuffle time-series data.
5. Prevent future-data leakage.
6. Add appropriate evaluation metrics.
7. Add tests.
8. Update the model documentation.
9. Ensure model selection remains data-driven.

New models should not automatically become the default winner without evaluation.

---

## 📊 Data Contributions

When working with datasets:

* Do not commit private datasets.
* Do not commit credentials.
* Do not commit unnecessarily large raw datasets.
* Document dataset sources.
* Respect the original dataset's license and usage conditions.
* Clearly distinguish synthetic and real datasets.

---

## 🔐 Security

Never submit:

* API keys
* Passwords
* `.env` files containing secrets
* Private datasets
* Authentication tokens
* Database credentials

If you discover a security vulnerability, please follow the process described in `SECURITY.md` instead of opening a public issue.

---

## 📝 Commit Messages

Use clear and descriptive commit messages.

Examples:

```text
feat: add SARIMA forecasting model
fix: validate uploaded CSV timestamps
docs: improve forecasting documentation
test: add anomaly detection tests
refactor: simplify feature engineering pipeline
```

Keep commits focused on a single logical change when possible.

---

## 🔀 Pull Requests

Before opening a pull request:

* [ ] Tests pass locally.
* [ ] New functionality has appropriate tests.
* [ ] Documentation is updated.
* [ ] No secrets are included.
* [ ] No unnecessary files are committed.
* [ ] Code follows the existing project structure.
* [ ] The change matches the project's scope.

### Pull Request Description

Please explain:

1. What changed?
2. Why was it changed?
3. How was it tested?
4. Are there any limitations or known issues?

---

## 🐛 Bug Reports

When reporting a bug, include:

* Operating system
* Python version
* Project version/commit
* Steps to reproduce
* Expected behavior
* Actual behavior
* Relevant error message
* Minimal dataset/example if appropriate

Do not include secrets or sensitive data.

---

## 💡 Feature Requests

Feature requests are welcome.

A useful feature request should describe:

* The problem
* Proposed solution
* Expected benefit
* Potential implementation approach
* Any relevant examples

Large features should ideally be discussed before implementation.

---

## 📚 Documentation

Documentation improvements are always welcome.

You can contribute by improving:

* README
* API documentation
* Installation instructions
* ML explanations
* Code comments
* Examples
* Troubleshooting information

---

## 📜 License

By contributing to this project, you agree that your contributions will be licensed under the project's **MIT License**.
