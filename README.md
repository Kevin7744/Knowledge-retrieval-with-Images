## Knowledge Retrieval with Images

This app retrieves images of a website by scraping the raw html then turn relative url to absolute url in html and convert the html to markdown, after that create a vector index from markdown and do RAG search depending on the query similarity and generate an answer with OpenAI

* packages needed<br>
	**pip install dotenv langchain llama openai html2text requests beatifulsoup html2text**

