# Requirements Files

This directory contains different requirements files for various deployment scenarios:

## Files

- **`../requirements.txt`** - Main production requirements (use this for most deployments)
- **`minimal.txt`** - Minimal dependencies for basic functionality
- **`production.txt`** - Enhanced production features with additional packages
- **`simple.txt`** - Simple deployment for lightweight environments

## Usage

### Standard Deployment
```bash
pip install -r requirements.txt
```

### Minimal Deployment (Render, Heroku Free Tier)
```bash
pip install -r requirements/minimal.txt
```

### Production with Enhanced Features
```bash
pip install -r requirements/production.txt
```

### Simple/Testing Environment
```bash
pip install -r requirements/simple.txt
```

## Notes

- All requirements files are tested and compatible
- The main `requirements.txt` is recommended for most use cases
- Choose minimal requirements if you encounter package installation issues on deployment platforms