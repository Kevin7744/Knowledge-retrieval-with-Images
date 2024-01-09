# Web Content to Markdown

This Python script demonstrates a process for converting raw HTML content from a website into Markdown format using various libraries. It also showcases the creation of a vector index from the resulting Markdown and utilizes a Retrieval Augmented Generation (RAG) approach to generate answers based on user queries.

## Dependencies

- `bs4` (BeautifulSoup): A Python library for pulling data out of HTML and XML files.
- `urllib`: A module for working with URLs, used for joining and parsing.
- `dotenv`: A module for loading environment variables from a file.
- `requests`: A Python library for making HTTP requests.
- `json`: A module for encoding and decoding JSON data.
- `os`: A module for interacting with the operating system.
- `html2text`: A Python script that converts HTML to Markdown.

## Configuration

The script uses environment variables to configure the API keys for browserless and OpenAI. Ensure you have a `.env` file with the following variables:

```plaintext
BROWSERLESS_API_KEY=your_browserless_api_key
OPENAI_API_KEY=your_openai_api_key
