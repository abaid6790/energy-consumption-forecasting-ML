# 🔐 Security Policy

## Energy Consumption Forecasting System

Security is an important part of the Energy Consumption Forecasting System.

This project includes basic protections for file uploads, application errors, secrets, and database operations. However, it is primarily a portfolio and development project and should not be assumed to be production-secure without additional hardening and review.

---

## 🛡️ Supported Versions

Security fixes are generally focused on the latest version of the project.

| Version               | Security Support |
| --------------------- | ---------------- |
| Latest                | ✅ Supported      |
| Older versions        | ⚠️ Best effort   |
| Unmaintained versions | ❌ Not supported  |

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability, please **do not disclose it publicly through a GitHub issue**.

Instead, report it privately to the project maintainer.

Include:

* A clear description of the vulnerability
* Steps to reproduce the issue
* Potential impact
* Affected component
* Suggested mitigation, if known
* Relevant logs or screenshots where safe

Do not include:

* Passwords
* API keys
* Authentication tokens
* Private user information
* Private datasets
* Other sensitive credentials

---

## 🔎 Security Areas

### 1. File Upload Security

Uploaded CSV files are validated server-side.

Validation includes:

* File extension
* File size
* Required columns
* Timestamp parsing
* Data types
* Minimum row count
* Dataset structure

Uploaded filenames are sanitized using secure filename handling.

The application also checks that resolved file paths remain inside the intended upload directory.

---

## 2. Uploaded Content

Uploaded datasets are treated as data.

The application does not intentionally execute uploaded files or treat their contents as Python, shell commands, or executable code.

Only expected data-processing operations should be performed on uploaded datasets.

---

## 3. Directory Traversal Protection

User-controlled filenames must not be trusted.

The application uses:

* Filename sanitization
* Upload-directory restrictions
* Path-containment validation

These controls help prevent attempts to write files outside the intended upload directory.

---

## 4. Upload Size Limits

Uploaded files are subject to a configurable maximum size.

Example configuration:

```env
MAX_UPLOAD_MB=50
```

This helps reduce resource-exhaustion risks caused by unexpectedly large uploads.

---

## 5. CSRF Protection

Form-based requests use CSRF protection.

JSON API endpoints may be explicitly exempt from form-based CSRF protection because they are designed as API requests rather than browser form submissions.

Authentication and API-specific authorization should be added before exposing protected functionality publicly.

---

## 6. Secrets Management

Secrets must be stored in environment variables.

Example:

```env
SECRET_KEY=your-secret-key
```

The real `.env` file must never be committed to Git.

Use:

```text
.env.example
```

to document required configuration without exposing real credentials.

---

## 7. Error Handling

Production-facing responses should not expose:

* Python stack traces
* Internal filesystem paths
* Database credentials
* Environment variables
* Internal implementation details

The application provides controlled error handlers for common server errors.

---

## 8. Database Security

SQLite operations should use parameterized queries or safe ORM mechanisms.

Avoid constructing SQL queries using direct string concatenation with user-controlled input.

Bad:

```python
query = "SELECT * FROM history WHERE id = " + user_input
```

Preferred:

```python
query = "SELECT * FROM history WHERE id = ?"
```

with parameters supplied separately.

---

## 9. Dependency Security

Dependencies should be installed from the project's dependency file:

```bash
pip install -r requirements.txt
```

Contributors should avoid introducing unnecessary dependencies.

Dependencies should be reviewed and updated periodically to address known vulnerabilities.

---

## 10. Machine Learning Security

Machine-learning artifacts such as `.pkl` files should only be loaded from trusted sources.

Python pickle files can execute arbitrary code when deserialized from an untrusted source.

Therefore:

> Never load an unknown or untrusted model artifact.

Generated model files should be treated as trusted application artifacts.

---

## 11. Dataset Privacy

Energy-consumption data can potentially reveal information about household behavior.

Users should avoid uploading datasets containing:

* Personally identifiable information
* Addresses
* Names
* Account numbers
* Private credentials
* Other sensitive information

The project does not guarantee privacy or regulatory compliance for arbitrary datasets.

---

## 12. Production Deployment

Before deploying the application publicly, additional security controls are recommended:

* HTTPS
* Production WSGI server
* Secure cookie configuration
* Authentication
* Authorization
* Rate limiting
* Reverse proxy
* Security headers
* Centralized logging
* Monitoring
* Database backups
* Dependency scanning
* Container isolation
* Restricted file-system permissions

The Flask development server should not be used as the production server.

---

## 13. Security Best Practices for Contributors

Contributors should:

* Never commit secrets.
* Validate user-controlled input.
* Avoid unsafe deserialization.
* Avoid shell execution with user input.
* Use parameterized database queries.
* Validate uploaded files.
* Avoid exposing internal errors.
* Add tests for security-sensitive changes.
* Review dependencies before adding them.

---

## 14. Responsible Disclosure

Security vulnerabilities should be reported privately so that they can be investigated and addressed before public disclosure.

The maintainer may request additional information to reproduce and verify the issue.

After a fix is available, the project may publish an appropriate security advisory describing:

* Affected versions
* Vulnerability type
* Impact
* Fixed version
* Recommended upgrade path

---

## 15. Security Disclaimer

This project is primarily intended for:

* Education
* Demonstration
* Portfolio development
* Local experimentation
* Machine-learning research

It has not undergone a formal third-party security audit.

Deployers are responsible for implementing appropriate security controls for their environment and use case.
