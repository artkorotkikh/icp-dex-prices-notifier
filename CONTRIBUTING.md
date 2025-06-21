# Contributing to ICP Token Monitor Bot

🎉 Thank you for your interest in contributing to the ICP Token Monitor Bot! We welcome contributions from the community.

## 🤝 How to Contribute

### 🐛 Reporting Bugs

Before creating bug reports, please check the issue list as you might find that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what behavior you expected**
- **Include screenshots if applicable**
- **Include your environment details** (OS, Python version, etc.)

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and expected behavior**
- **Explain why this enhancement would be useful**

### 🔧 Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/ICP_tokens_bot.git
   cd ICP_tokens_bot
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration**
   ```bash
   cp config/config.env.example config/config.env
   # Edit config/config.env with test values
   ```

5. **Run tests**
   ```bash
   python3 tests/test_apis.py
   python3 tests/local_test.py
   ```

### 🔀 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes**
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   python3 tests/test_apis.py
   python3 tests/local_test.py
   python3 tests/test_main_components.py
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Create a Pull Request**
   - Use a clear and descriptive title
   - Describe what you changed and why
   - Reference any related issues

## 📝 Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these additions:

- **Line length**: 88 characters (Black formatter standard)
- **Imports**: Use absolute imports, group them logically
- **Docstrings**: Use Google-style docstrings
- **Type hints**: Use type hints for function parameters and return values

### Code Structure

```python
"""Module docstring describing the purpose."""

import standard_library
import third_party_library

from .local_module import LocalClass


class ExampleClass:
    """Class docstring describing the purpose.
    
    Attributes:
        attribute_name: Description of the attribute.
    """
    
    def __init__(self, param: str) -> None:
        """Initialize the class.
        
        Args:
            param: Description of the parameter.
        """
        self.attribute_name = param
    
    def example_method(self, param: int) -> str:
        """Example method with proper documentation.
        
        Args:
            param: Description of the parameter.
            
        Returns:
            Description of the return value.
            
        Raises:
            ValueError: When param is negative.
        """
        if param < 0:
            raise ValueError("Parameter must be non-negative")
        return str(param)
```

### Testing Guidelines

- **Write tests** for all new functionality
- **Use descriptive test names** that explain what is being tested
- **Test edge cases** and error conditions
- **Keep tests isolated** and independent
- **Use mock objects** for external dependencies

Example test structure:
```python
def test_example_function_with_valid_input():
    """Test that example_function works with valid input."""
    result = example_function("valid_input")
    assert result == "expected_output"

def test_example_function_with_invalid_input():
    """Test that example_function raises error with invalid input."""
    with pytest.raises(ValueError):
        example_function("invalid_input")
```

## 🏗️ Project Structure

When adding new features, follow the existing project structure:

```
src/
├── core/           # Core business logic
│   ├── database.py     # Database operations
│   ├── api_client.py   # API integrations
│   └── alert_system.py # Alert processing
├── bot/            # Telegram bot interface
│   └── telegram_bot.py # Bot handlers
└── utils/          # Utility functions
    └── helpers.py      # Helper functions
```

### Adding New Features

1. **Core functionality** goes in `src/core/`
2. **Bot commands** go in `src/bot/telegram_bot.py`
3. **Utility functions** go in `src/utils/`
4. **Tests** go in `tests/` with descriptive names
5. **Documentation** updates go in `docs/`

## 🧪 Testing Your Changes

Before submitting a pull request, ensure all tests pass:

```bash
# API connectivity tests
python3 tests/test_apis.py

# Full system test (no Telegram required)
python3 tests/local_test.py

# Integration tests
python3 tests/test_main_components.py

# Quick price check
python3 tests/quick_test.py
```

## 📚 Documentation

- Update relevant documentation when making changes
- Add docstrings to new functions and classes
- Update the README if you add new features
- Consider adding examples for complex features

## 🔍 Code Review Process

1. **Automated checks** run on all pull requests
2. **Manual review** by maintainers
3. **Testing** on different environments
4. **Documentation** review for completeness
5. **Merge** after approval

## 🎯 Areas for Contribution

We welcome contributions in these areas:

### 🚀 High Priority
- **New DEX integrations** (KongSwap, etc.)
- **Performance optimizations**
- **Error handling improvements**
- **Test coverage expansion**

### 🌟 Medium Priority
- **Advanced charting features**
- **Portfolio tracking**
- **Mobile notifications**
- **UI/UX improvements**

### 💡 Ideas Welcome
- **AI price predictions**
- **Social trading features**
- **Multi-chain support**
- **Advanced analytics**

## 🏷️ Issue Labels

We use these labels to organize issues:

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `priority-high` - High priority issue
- `priority-medium` - Medium priority issue
- `priority-low` - Low priority issue

## 🤔 Questions?

If you have questions about contributing:

1. **Check existing issues** and discussions
2. **Create a new issue** with the `question` label
3. **Join our community** channels for real-time help

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors are recognized in:

- **README.md** acknowledgments section
- **Release notes** for significant contributions
- **Community shoutouts** on social media

Thank you for helping make the ICP Token Monitor Bot better! 🚀 