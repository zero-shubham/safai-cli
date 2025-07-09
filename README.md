# Safai CLI

Safai is a command-line tool that intelligently organizes your folders using AI. It supports multiple AI platforms and can be customized to your needs.

## Features
- Organize your folders and files using AI suggestions
- Supports OpenAI, Google Gemini, and Anthropic Claude platforms
- One-shot (no feedback) or interactive feedback mode
- Recursively organize subdirectories
- Ignore specific directories
- Configurable via CLI options or a config file

## Installation

Safai is distributed as a Python package. You can install it using pip:

```bash
pip install safai
```

If you are developing locally, you can install it in editable mode from the repo root:

```bash
pip install -e .
```

> **Tip:** It's recommended to use a virtual environment for isolation.

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

> **Note:** Except for `PATH`, all options can be set in `$HOME/.safai` and will be loaded automatically if not provided on the command line.

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

## Configuration File: `$HOME/.safai`

You can store your default options in a config file in your home directory. This file uses INI format and can have a `[config]` section for global defaults and sections for each platform.

> **Note:** Only `platform` and `ignore` can be set in the `[config]` section. `api_key` and `model` must be set in the platform-specific sections (`[openai]`, `[gemini]`, `[claude]`). `one_shot` and `recursive` must be provided via CLI options if needed.

### Example `$HOME/.safai`:

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

## License
MIT
