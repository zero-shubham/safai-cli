# Safai CLI

[![PyPI version](https://badge.fury.io/py/safai.svg)](https://badge.fury.io/py/safai)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Safai is a command-line tool that intelligently organizes your folders using AI. It supports multiple AI platforms and can be customized to your needs.

## Features
- Organize your folders and files using AI suggestions
- Supports OpenAI, Google Gemini, and Anthropic Claude platforms
- One-shot (no feedback) or interactive feedback mode
- Recursively organize subdirectories
- Ignore specific directories
- Configurable via CLI options or a config file

## Installation

### 🚀 Quick Install (Recommended)

Install using **uv** (recommended for speed and reliability):

```bash
uv add safai
```

Or using **pip**:

```bash
pip install safai
```

### 🔧 Development Install

If you're developing locally or want to contribute:

```bash
# Clone the repository
git clone https://github.com/shubham-biswas/safai-cli.git
cd safai-cli

# Install in editable mode with uv
uv pip install -e .

# Or with pip
pip install -e .
```

### 📦 Alternative Installation Methods

#### Using pipx (isolated environment):
```bash
pipx install safai
```

#### Using conda/mamba:
```bash
conda install -c conda-forge safai
```

> **💡 Tip**: It's recommended to use a virtual environment or uv for better dependency management and isolation.

### 🐍 Python Version Requirements

- **Minimum**: Python 3.10
- **Recommended**: Python 3.11+
- **Tested**: Up to Python 3.13

### 📋 Dependencies

Safai automatically installs its core dependencies:
- `anthropic` - For Claude AI platform
- `google-genai` - For Gemini AI platform  
- `openai` - For OpenAI platform
- `platformdirs` - Cross-platform config directories
- `pydantic` - Data validation
- `pyyaml` - YAML parsing
- `rich` - Beautiful terminal output
- `typer` - CLI framework

## Usage

Run the CLI with:

```bash
python main.py [OPTIONS] PATH
```

Or using the Makefile:

```bash
make run ARGS="[OPTIONS] PATH"
```

### Required Argument
- `PATH`: Path to the directory you want to organize

### Options
| Option         | Short | Description                                              | Default           |
| --------------|-------|----------------------------------------------------------|-------------------|
| --platform    | -pl   | AI platform to use (`openai`, `gemini`, `claude`)        | (from config)     |
| --api_key     | -a    | API Key for the selected AI platform                     | (from config)     |
| --model       | -m    | Model to use as per platform                             | (from config)     |
| --one_shot    | -o    | Organize without any feedback from user                  | False             |
| --recursive   | -r    | Recursively organize sub-directories                     | False             |
| --ignore      | -i    | Directories to ignore (can be used multiple times)       | []                |

> **Note:** Except for `PATH`, all options can be set in a config file and will be loaded automatically if not provided on the command line.

> **Recursive mode (-r/--recursive):**
> When this flag is set, Safai will traverse all subdirectories of the specified path and organize files in every folder, not just the root. This is useful for deeply nested or complex folder structures.

## Supported Platforms
- `openai`   (e.g., GPT models)
- `gemini`   (Google Gemini)
- `claude`   (Anthropic Claude)

### Default Models
| Platform | Default Model              |
|----------|---------------------------|
| openai   | o4-mini                   |
| gemini   | gemini-1.5-flash          |
| claude   | claude-3-7-sonnet-latest  |

If you do not specify a model for a platform, Safai will use the default model listed above.

## Example: Organizing a Folder

```bash
python main.py --platform openai --api_key YOUR_OPENAI_KEY --model gpt-3.5-turbo /path/to/your/folder
```

Or, with a config file (recommended):

## Configuration File

Safai stores configuration in platform-specific locations:

**Linux**: `~/.safai`  
**macOS**: `~/Library/Application Support/safai/config`  
**Windows**: `%APPDATA%\safai\config`

> **Note**: Safai also checks `~/.safai` as a fallback on macOS/Windows for backward compatibility.

The config file uses INI format with a `[config]` section for global defaults and sections for each platform.

> **Note:** Only `platform` and `ignore` can be set in the `[config]` section. `api_key` and `model` must be set in the platform-specific sections (`[openai]`, `[gemini]`, `[claude]`). `one_shot` and `recursive` must be provided via CLI options if needed.

### Example Config File:

```ini
[config]
platform = openai
ignore = .git,node_modules

[openai]
api_key = sk-xxxxxxx
model = gpt-3.5-turbo

[gemini]
api_key = your-gemini-key
model = gemini-1.5-flash

[claude]
api_key = your-claude-key
model = claude-3-7-sonnet-latest
```

- Values in `[config]` are used as defaults for platform and ignore.
- Platform-specific sections must provide `api_key` and `model` for that platform.
- `ignore` can be a comma-separated list of directory names to skip.
- `one_shot` and `recursive` must be set via CLI flags (`--one_shot`, `--recursive`).

## Feedback & Interactive Mode
- By default, Safai will ask for feedback after suggesting an organization plan. Enter `n` to accept, `s` to skip, or provide feedback to refine the suggestion.
- Use `--one_shot` to skip feedback and auto-apply suggestions.

## Troubleshooting
- If required options are missing, Safai will prompt you to provide them or add them to your config file.
- Make sure your API keys are valid and have access to the selected model/platform.

## Sample Usage

```shell
zero@pop-os ~/Desktop » ls -al             
total 3464
drwxr-xr-x  8 zero zero   4096 Jul 12 09:51  .
drwxr-x--- 45 zero zero   4096 Jul 12 09:51  ..
drwxrwxr-x  3 zero zero   4096 Jul 10 17:06  Archives
-rwxrwxr-x  1 zero zero 344077 May  6 19:55  cartoonified_image.jpg
drwxrwxr-x  2 zero zero   4096 Jul 10 15:28  Configurations
-rwxrwxr-x  1 zero zero  92200 May  6 19:55  distributed_sys.png
-rwxrwxr-x  1 zero zero  65154 May  6 19:55  distributed_sys.svg
drwxrwxr-x  2 zero zero   4096 Jul 10 17:06  Documents
drwxrwxr-x  5 zero zero   4096 Jul 10 17:08  Domine
-rwxrwxr-x  1 zero zero    903 May  6 19:55  favicon.png
-rwxrwxr-x  1 zero zero   2468 May  6 19:55  favicon.svg
-rwxrwxr-x  1 zero zero    637 May  6 19:55  logo-dark.svg
-rwxrwxr-x  1 zero zero    637 May  6 19:55  logo-light.svg
-rwxrwxr-x  1 zero zero 915451 May  6 19:55  me2.jpeg
-rwxrwxr-x  1 zero zero 836589 May  6 19:55  me3.jpeg
-rwxrwxr-x  1 zero zero 653372 May  6 19:55  me4.jpeg
drwxrwxr-x  4 zero zero   4096 Jul 10 17:07  Nunito_Sans
-rwxrwxr-x  1 zero zero 150540 May  6 19:55  panasonic_ac_invoice.jpeg
-rwxrwxr-x  1 zero zero     83 May  6 19:55  rounded_favicon.png
-rwxrwxr-x  1 zero zero 348393 May  6 19:55  vector_cartoon_image.jpg
-rwxrwxr-x  1 zero zero  67330 May  6 19:55  WhatsApp_Image_2025-01-14_at_11.48.39_AM.jpeg

zero@pop-os ~/Desktop » safai ~/Desktop -pl=openai      
Model value not provided defaulting to o4-mini
Currently processing /home/zero/Desktop/ 

⠏ In process...
Suggested reorganize as follows: 
 Media:
  Images:
    Logos:
      - 'logo-dark.svg'
      - 'logo-light.svg'
    Favicons:
      - 'favicon.svg'
      - 'favicon.png'
      - 'rounded_favicon.png'
    Illustrations:
      - 'distributed_sys.svg'
      - 'distributed_sys.png'
      - 'cartoonified_image.jpg'
      - 'vector_cartoon_image.jpg'
    Photos:
      Selfies:
        - 'me2.jpeg'
        - 'me3.jpeg'
        - 'me4.jpeg'
      WhatsApp:
        - 'WhatsApp_Image_2025-01-14_at_11.48.39_AM.jpeg'
      Invoices:
Please provide any feedback if required (n to accept / s to skip - current plan): n
Happy decluttering! ✨

zero@pop-os ~/Desktop » ls -al                    
total 36
drwxr-xr-x  9 zero zero 4096 Jul 12 09:52  .
drwxr-x--- 45 zero zero 4096 Jul 12 09:53  ..
drwxrwxr-x  3 zero zero 4096 Jul 10 17:06  Archives
drwxrwxr-x  2 zero zero 4096 Jul 10 15:28  Configurations
drwxrwxr-x  2 zero zero 4096 Jul 10 17:06  Documents
drwxrwxr-x  5 zero zero 4096 Jul 10 17:08  Domine
drwxrwxr-x  3 zero zero 4096 Jul 12 09:52  Media
drwxrwxr-x  4 zero zero 4096 Jul 10 17:07  Nunito_Sans

zero@pop-os ~/Desktop » ls -al Media/Images 
total 24
drwxrwxr-x 6 zero zero 4096 Jul 12 09:52 .
drwxrwxr-x 3 zero zero 4096 Jul 12 09:52 ..
drwxrwxr-x 2 zero zero 4096 Jul 12 09:52 Favicons
drwxrwxr-x 2 zero zero 4096 Jul 12 09:52 Illustrations
drwxrwxr-x 2 zero zero 4096 Jul 12 09:52 Logos
drwxrwxr-x 5 zero zero 4096 Jul 12 09:52 Photos
```

## License
GNU General Public License v3.0
