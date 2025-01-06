# NounLogic Summariser Lib

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)

## 🚀 Introduction

Welcome to **NounLogic Summariser Lib** – your ultimate tool for intelligent and efficient text summarization! Whether you're dealing with lengthy articles, extensive reports, or any substantial text content, our library simplifies the process by breaking down text into manageable chunks and leveraging the power of the Ollama model to generate concise summaries. Perfect for developers, researchers, and anyone looking to streamline their text processing workflows.

## ✨ Features

- **Multi-Format Support**: Seamlessly handle `.txt`, `.md`, `.pdf`, `.xlsx`, and `.docx` files.
- **Smart Sanitization**: Automatically cleans and prepares text by removing non-understandable characters.
- **Dynamic Chunking**: Breaks down large texts into customizable token-sized chunks for efficient processing.
- **Configurable Summarization**: Fully adjustable settings via `config.json` or CLI commands to tailor the summarization process.
- **Ollama Integration**: Utilizes the Ollama library to interact with locally running models for high-quality summaries.
- **Extensible Output**: Save summaries in your preferred format, including `.txt` and `.pdf`.
- **Robust Logging & Error Handling**: Comprehensive logging to monitor processes and handle errors gracefully.
- **User-Friendly CLI**: Easy-to-use command-line interface for quick operations and configurations.

## 📦 Installation

### Prerequisites

- **Python 3.8+**
- **Pip** package manager
- **Ollama** installed and running locally

### Steps

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/nounlogic-summariser-lib.git
    cd nounlogic-summariser-lib
    ```

2. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up Console Scripts**

    Uncomment the `console_scripts` section in `setup.cfg` if not already enabled:

    ```ini
    [options.entry_points]
    console_scripts =
        summariser = nounlogic_summariser_lib.skeleton:run
    ```

4. **Install the Package**

    ```bash
    pip install .
    # or for editable mode
    pip install -e .
    ```

5. **Verify Installation**

    ```bash
    summariser --help
    ```

## 🛠 Usage

NounLogic Summariser Lib can be used both as a Python library and a CLI tool.

### 👩‍💻 As a Python Library

```python
from nounlogic_summariser_lib import summariser

# Load configuration
config = summariser.load_config('config.json')

# Process and summarize a file
summariser.process_file('path/to/your/file.txt', config)
```

### 🖥️ Via CLI

```bash
summariser summarize path/to/your/file.md
```

#### 📄 Additional CLI Options

- **Specify Configuration File**

    ```bash
    summariser summarize path/to/file.pdf --config custom_config.json
    ```

- **Enable Verbose Logging**

    ```bash
    summariser summarize path/to/file.txt -v
    ```

### 🌟 Example Workflow

1. **Summarize a PDF File**

    ```bash
    summariser summarize documents/report.pdf
    ```

    This command converts `report.pdf` to Markdown, sanitizes the text, breaks it into chunks, summarizes each chunk using the Ollama model, and saves the summary as `report_summarised.txt` in the `summarized_outputs` directory.

2. **Customize Summarization Parameters**

    Modify `config.json` to adjust token limits, prompts, and output settings to fit your specific needs.

    ```json
    {
        "token_limit": 1500,
        "prompt_template": "Please provide a concise summary of the following text:",
        ...
    }
    ```

3. **Handle Errors Gracefully**

    If an error occurs during processing, it will be logged to `errors.log`, and the tool will continue processing remaining chunks if `continue_on_error` is set to `true`.

## 🛠 Configuration

All settings are managed via the `config.json` file. Ensure that no settings are hardcoded to allow maximum flexibility.

```json
{
    "token_limit": 1000,
    "prompt_template": "Generate a summary of the following text:",
    "ollama": {
        "model": "tinyllama",
        "host": "localhost",
        "port": 11434,
        "timeout": 30,
        "retry_attempts": 3
    },
    "output": {
        "suffix": "_summarised.txt",
        "directory": "summarized_outputs"
    },
    ...
}
```

## 📚 Supported Formats

- **Input**: `.txt`, `.md`, `.pdf`, `.xlsx`, `.docx`
- **Output**: `.txt`, `.pdf`

## 🐞 Logging & Error Handling

- **Logging**: Detailed logs are saved to `summarizer.log` with configurable log levels.
- **Error Handling**: Errors are recorded in `errors.log`, and the tool can be set to continue processing despite errors.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

For any inquiries or support, please contact [nathfavour](mailto:nathfavour@example.com).

---

Happy summarizing! 🚀