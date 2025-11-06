# 🚀 Contributing to Vizora

Thank you for your interest in contributing to Vizora! We're excited to work with you to make data visualization more accessible and beautiful for everyone.

## 🌟 Ways to Contribute

- **🐛 Bug Reports**: Found something that doesn't work? Let us know!
- **💡 Feature Requests**: Have an idea for making Vizora better? We'd love to hear it!
- **📝 Documentation**: Help improve our docs, examples, and tutorials
- **🔧 Code Contributions**: Fix bugs, add features, or improve performance
- **🧩 Plugin Development**: Create plugins for new data sources or visualizations
- **🎨 UI/UX Improvements**: Make Vizora more beautiful and user-friendly

## 🏗️ Development Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- Git

### Getting Started

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/vizora.git
cd vizora

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all extras
pip install -e ".[dev,all]"

# Install pre-commit hooks
pre-commit install

# Run tests to make sure everything works
pytest

# Start the development server
vizora run
```

## 🧪 Testing

We use pytest for testing. Please write tests for any new features or bug fixes.

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vizora --cov-report=html

# Run specific test file
pytest tests/test_dashboard.py

# Run tests matching a pattern
pytest -k "test_data_loading"
```

## 📋 Code Style

We use several tools to maintain code quality:

```bash
# Format code with black
black vizora/

# Sort imports with isort
isort vizora/

# Lint with flake8
flake8 vizora/

# Type check with mypy
mypy vizora/

# Run all checks (this happens automatically in pre-commit)
pre-commit run --all-files
```

## 🎯 Commit Guidelines

We follow conventional commits for clear, meaningful commit messages:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code formatting (no logic changes)
- `refactor:` Code restructuring (no behavior changes)
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add PostgreSQL data source plugin
fix: resolve port conflict in startup script
docs: update installation instructions
```

## 🔌 Plugin Development

Creating plugins is one of the best ways to extend Vizora! Here's a quick example:

```python
from vizora.plugins import VisualizationPlugin, PluginMetadata

class MyCustomPlugin(VisualizationPlugin):
    def get_metadata(self):
        return PluginMetadata(
            name="my-custom-viz",
            version="1.0.0",
            author="Your Name",
            description="My awesome custom visualization"
        )
    
    def create_visualization(self, data, config):
        # Your visualization logic here
        return {
            "type": "custom_chart",
            "data": data,
            "config": config
        }
```

## 📖 Documentation

We use MkDocs for documentation. To work on docs:

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Serve docs locally
mkdocs serve

# Build docs
mkdocs build
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear description** of what you expected vs. what happened
2. **Steps to reproduce** the issue
3. **Environment details** (Python version, OS, etc.)
4. **Error messages** or screenshots if applicable
5. **Sample data** if the issue is data-related (anonymized if needed)

## 💡 Feature Requests

For feature requests, please provide:

1. **Use case**: What problem does this solve?
2. **Detailed description**: How should it work?
3. **Examples**: Show us what you envision
4. **Alternatives**: Have you considered other approaches?

## 🏷️ Pull Request Process

1. **Fork** the repository and create a feature branch
2. **Write tests** for your changes
3. **Update documentation** if needed
4. **Run all checks** (`pre-commit run --all-files`)
5. **Submit PR** with clear description of changes

### PR Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (please describe)

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord**: Join our community chat (link in README)
- **Email**: pedahd@gmail.com for direct contact

## 🤝 Code of Conduct

We're committed to fostering a welcoming, inclusive community. Please:

- **Be respectful** and considerate in all interactions
- **Welcome newcomers** and help them get started
- **Focus on constructive feedback** and collaborative problem-solving
- **Respect different perspectives** and experiences
- **Report inappropriate behavior** to the maintainers

## 📄 License

By contributing to Vizora, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

**Thank you for helping make Vizora better! 🙏**

Your contributions make a real difference in helping people create beautiful, meaningful data visualizations. We appreciate your time and effort!