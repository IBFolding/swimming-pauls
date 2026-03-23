# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.1.x   | :white_check_mark: |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

**Please do not open public issues for security vulnerabilities.**

Instead, please report security vulnerabilities via:

1. **Email:** security@swimmingpauls.com (preferred)
2. **Discord DM:** Message an admin in our [Discord server](https://discord.gg/clawd)

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will:
1. Acknowledge receipt within 48 hours
2. Investigate and confirm within 1 week
3. Release a patch as soon as possible
4. Credit you in the release notes (if desired)

## Security Considerations

### 100% Local Architecture
Swimming Pauls is designed to be completely local:
- No data is sent to external servers
- No API keys required for core functionality
- All processing happens on your machine

This means **you control your data**.

### Optional External Services
Some optional features may connect to external services:

| Feature | External Connection | Data Sent |
|---------|---------------------|-----------|
| Crypto prices | CoinGecko/Hyperliquid | Token symbols only |
| News search | Various APIs | Search queries only |
| Telegram bot | Telegram servers | Messages you send |

**These are opt-in** and core functionality works without them.

### Data Storage
All data is stored locally:
- `data/` directory: Predictions, prices, history
- `logs/` directory: Application logs
- `config.yaml`: Your configuration

**No cloud storage. No telemetry. No analytics.**

### Code Execution
Pauls run code within the Swimming Pauls environment:
- Sandboxed to the project directory
- No network access by default
- Custom skills can be reviewed before use

### Best Practices

#### For Users
1. **Keep dependencies updated:**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Review custom skills:**
   Before installing third-party skills, review the code.

3. **Backup your data:**
   ```bash
   python export_data.py
   ```

4. **Use a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

#### For Contributors
1. **No hardcoded secrets:**
   Use environment variables or config files.

2. **Input validation:**
   Validate all user inputs.

3. **Secure defaults:**
   Default to safe configurations.

4. **No external calls without consent:**
   Make network activity opt-in and transparent.

## Known Limitations

### Current
1. **No authentication:** Anyone with access to localhost:3005 can use the UI
2. **No encryption:** Data stored in plaintext JSON/SQLite
3. **No audit log:** No record of who made what prediction

These are acceptable for single-user local deployments but would need addressing for multi-user or cloud deployments.

### Future (v2.2+)
- Optional authentication
- Encrypted data storage
- Audit logging
- Sandboxed skill execution

## Third-Party Dependencies

We regularly audit dependencies:
```bash
pip install safety
safety check
```

Known vulnerable dependencies will be patched promptly.

## Contact

- **Security Email:** security@swimmingpauls.com
- **Discord:** [Private message an admin](https://discord.gg/clawd)
- **PGP Key:** Available upon request

---

**Last Updated:** 2026-03-23

We take security seriously. Thank you for helping keep Swimming Pauls safe.
