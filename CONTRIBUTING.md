# Contributing to Swimming Pauls

First off, thank you for considering contributing to Swimming Pauls! It's people like you that make this project better for everyone.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/swimming-pauls.git`
3. **Create a branch**: `git checkout -b feature/amazing-feature`
4. **Make changes** and test them
5. **Commit**: `git commit -m 'Add amazing feature'`
6. **Push**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

## 📋 Ways to Contribute

### 🐛 Report Bugs

Before creating a bug report, please:
- Check if the issue already exists
- Use the latest version
- Run `python health_check.py` to verify your setup

**Good bug reports include:**
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- System info (OS, Python version, RAM)
- Error messages or logs

**Template:**
```
**Bug:** Brief description

**To Reproduce:**
1. Run `python start.py`
2. Click 'Connect Local'
3. ...

**Expected:** What should happen
**Actual:** What actually happens

**System:**
- OS: macOS 14.2
- Python: 3.11.4
- RAM: 16GB
```

### 💡 Suggest Features

Feature requests are welcome! Please:
- Check if it's already been suggested
- Explain the use case
- Describe how it would work
- Consider if it fits the "100% local" philosophy

### 📝 Improve Documentation

Docs are never done! Help with:
- README clarity
- Code comments
- Example usage
- Tutorial guides
- Fixing typos

### 🔧 Code Contributions

Areas we need help:
- **New Paul Personas** - Add to `PAULS_EXTENDED.md`
- **New Skills** - Add data sources in `skills.py`
- **Visualizations** - Improve the web UI
- **Performance** - Optimize for more Pauls
- **Tests** - We need more test coverage

## 🛠️ Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/swimming-pauls.git
cd swimming-pauls

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8

# Run smoke test
python smoke_test.py

# Run full test suite
pytest
```

## 📝 Code Style

### Python
- Follow [PEP 8](https://pep8.org/)
- Use `black` for formatting: `black .`
- Use `flake8` for linting: `flake8 .`
- Max line length: 100 characters
- Use type hints where helpful

### Example:
```python
def resolve_prediction(
    prediction_id: str, 
    outcome: str, 
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark the outcome of a prediction.
    
    Args:
        prediction_id: ID of prediction
        outcome: 'CORRECT', 'INCORRECT', or 'PENDING'
        notes: Optional notes about the outcome
        
    Returns:
        Dict with resolution details
    """
    # Implementation here
    pass
```

### Documentation
- Use clear, concise language
- Include code examples
- Update README if adding features
- Add docstrings to functions

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest test_simulation.py

# Run with coverage
pytest --cov=swimming_pauls

# Run smoke test only
python smoke_test.py
```

### Writing Tests
```python
# test_example.py
import pytest
from swimming_pauls import SwimmingPauls

@pytest.fixture
def pauls():
    return SwimmingPauls()

def test_consensus_formation(pauls):
    """Test that consensus forms with multiple rounds."""
    result = pauls.run_simulation(rounds=5)
    assert result.consensus is not None
    assert result.consensus.confidence > 0
```

### What to Test
- Core simulation logic
- Data persistence
- WebSocket communication
- Skill integrations
- Edge cases (empty inputs, errors)

## 🔄 Pull Request Process

### Before Submitting
1. **Run tests**: `pytest` should pass
2. **Check style**: `black . && flake8 .`
3. **Update docs**: README, docstrings, comments
4. **Test manually**: Actually run the code

### PR Description Should Include
- **What**: What changed
- **Why**: Why it was needed
- **How**: How it works
- **Testing**: How you tested it
- **Screenshots**: If UI changes

### Example PR Template
```markdown
## What
Added price target resolution for crypto predictions

## Why
Users want to track if "BTC will hit $100k" predictions come true

## How
- Parses price targets from questions
- Fetches current prices via crypto-price skill
- Compares target vs current price
- Marks outcome CORRECT/INCORRECT

## Testing
- Tested with 5 sample predictions
- Verified BTC, ETH, SOL resolution
- Added unit tests in test_resolver.py

## Screenshots
[If applicable]
```

### Review Process
1. Maintainers will review within 48 hours
2. Address feedback promptly
3. Force push to update your branch: `git push --force-with-lease`
4. Once approved, maintainers will merge

## 🏷️ Commit Message Guidelines

Use conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build process, dependencies

### Examples
```
feat(resolver): Add auto-resolution for price targets

Automatically check if price target predictions came true
by comparing current price to target at resolution time.

Fixes #123
```

```
docs(readme): Add setup instructions for Windows

Updated README with Windows-specific steps and
troubleshooting for common issues.
```

## 🎯 Specific Contribution Areas

### Adding New Pauls
1. Edit `PAULS_EXTENDED.md`
2. Follow existing format
3. Include: name, specialty, style, risk profile, bio
4. Ensure diversity (different backgrounds, styles)

### Adding New Skills
1. Create skill in `skills/` directory
2. Inherit from `Skill` base class
3. Add to `skill_bridge.py` discovery
4. Document in SKILL.md
5. Add tests

### Improving Visualizations
1. Edit files in `ui/` directory
2. Test in multiple browsers
3. Ensure mobile responsiveness
4. Include screenshots in PR

### Performance Optimization
1. Profile first: `python -m cProfile simulation.py`
2. Target bottlenecks
3. Test with 1000+ Pauls
4. Document speed improvements

## 🌟 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md (coming soon)
- Mentioned in release notes
- Invited to contributor Discord channel

## 📞 Getting Help

- **Discord**: [Join our server](https://discord.gg/clawd)
- **GitHub Issues**: For bugs and features
- **Discussions**: For questions and ideas

## 📜 Code of Conduct

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards
**Positive behavior:**
- Being respectful of differing viewpoints
- Accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy towards others

**Unacceptable behavior:**
- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

### Enforcement
Instances of abusive behavior may be reported to the maintainers. All complaints will be reviewed and investigated promptly.

## 🙏 Thank You!

Every contribution, no matter how small, makes Swimming Pauls better. Whether you're:
- Reporting a typo
- Fixing a bug
- Adding a feature
- Improving docs

You're helping build something special. **Let the Pauls cook.** 🦷

---

**Questions?** Open an issue or reach out on Discord.
