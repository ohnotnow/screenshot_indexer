# MacOS Screenshot Describer and Indexer

This Python application leverages the Ollama and ChromaDB technologies to generate descriptions of MacOS screenshots and create a searchable index for them. This allows for efficient retrieval of screenshots based on their content.

## Features

- **Automatic Description Generation**: Utilizes Ollama's vision and text models to generate concise descriptions of screenshots.
- **Searchable Index Creation**: Integrates ChromaDB to store and query screenshot descriptions, facilitating easy search and retrieval.
- **Flexible File Handling**: Supports customizable file patterns and limits on the number of files processed.

## Prerequisites

Before running this script, ensure you have Python installed on your system (Python 3.8+ recommended). You will also need to have `pip` available to install dependencies.

## Installation

Clone the repository to your local machine using:

```bash
git clone [URL to your GitHub repository]
cd [repository name]
```

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

## Usage

To run the script, use the following command from the root of your repository:

```bash
cd ~/Pictures  # or where-ever your screenshots are
python /path/to/repo/main.py --update
python /path/to/repo/main.py --query "vegetable stew"
```

If you find yourself using this a lot - it's probably worth adding a shell alias, eg

```sh
alias sss="python /path/to/repo/main.py --query"
alias ssu="python /path/to/repo/main.py --update"
```

### Options

- `--pattern`: Specify the pattern to match files against (default: `Screenshot *.png`).
- `--max-files`: Define the maximum number of files to process (default: processes all matched files).
- `--update`: Enable updating the screenshot description database.
- `--query`: Query the database for specific terms.

### ChromaDB

The script should start it's own copy of ChromaDB if it's not already running - but this adds about five
seconds to the startup time.  If you want to have chroma running already then something like this would
match the paths this script uses.

```sh
chroma run --path /Users/you/ --log-path=/Users/you
```

## Contributing

Contributions to this project are welcome! Please feel free to fork the repository and submit pull requests.

## License

This project is licensed under the MIT license, see the LICENSE file for details.
