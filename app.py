from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
import requests
import json
import os
import html2text
from langchain.chat_models import ChatOpenAI
from llama_index import Document
from llama_index.node_parser import SimpleNodeParser
from llama_index.text_splitter import TokenTextSplitter
from langchain.prompts import ChatPromptTemplate
from llama_index import VectorStoreIndex
import openai

load_dotenv()
browserless_api_key = os.getenv("BROWSERLESS_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")


# 1. Scrape raw HTML
def scrape_website(url: str):
    print("Scraping websites...")
    # define the headers for the request
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    # define the data to be sent in the request
    data = {
        "url": url,
        "elements":[{
            "selector":"body"
        }]
    }

    # Convert Python objects to Json String
    data_json = json.dumps(data)

    # Send the post request
    response = requests.post(
        f"https://chrome.browserless.io/scrape?token={browserless_api_key}",
        headers=headers,
        data=data_json
    )

    # Check the response status code
    if response.status_code == 200:
        # Decode & load the string as a JSON object
        result = response.content
        data_str = result.decode('utf-8')
        data_dict = json.loads(data_str)

        # Extract the HTML content from the dictionary
        html_string = data_dict['data'][0]['results'][0]['html']

        return html_string
    else:
        print(f"HTTP request failed with status code {response.status_code}")


# 2. Convert html to marksdown
def convert_html_to_markdown(html):
    # Create an html converter
    converter = html2text.HTML2TEXT() 

    # configure the converter
    converter.ignore_links = False

    # convert the HTML to markdown
    markdown = converter.handle(html)

    return markdown

# Turn https://developers.webflow.com/docs/getting-started-with-apps to https://developers.webflow.com
def get_base_url(url):
    parsed_url = urlparse(url)

    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url


# Turn relative url to absolute url in html
def convert_to_absolute_url(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    for img_tag in soup.find_all('img'):
        if img_tag.get('src'):
            src = img_tag.get('src')
            if src.startswith(('http://', 'https://')):
                continue
            absolute_url = urljoin(base_url, src)
            img_tag['src'] = absolute_url
        elif img_tag.get('data-src'):
            src = img_tag.get('data-src')
            if src.startswith(('https://', 'https://')):
                continue
            absolute_url = urljoin(base_url, src)
            img_tag['data-src'] = absolute_url
        
        for link_tag in soup.find_all('a'):
            href = link_tag.get('href')
            if href.startswith(('http://', 'https://')):
                continue
            absolute_url = urljoin(base_url, href)
            link_tag['href'] = absolute_url

        updated_html = str(soup)
        return updated_html

def get_markdown_from_url(url):
    base_url = get_base_url(url)
    html = scrape_website(url)
    updated_html = convert_to_absolute_url(html, base_url)
    markdown = convert_html_to_markdown(updated_html)

    return markdown

# 3. Create a vector index from markdown
def create_index_from_text(markdown):
    text_splitter = TokenTextSplitter(
        separator = "\n",
        chunk_size = 1024,
        chunk_overlap = 20,
        back_separators = ["\n\n", ".", ","]
    )
    node_parser = SimpleNodeParser(text_splitter=text_splitter)
    nodes = node_parser.get_nodes_from_documents(
        [Document(text=markdown)], show_progress = True)
    
    # Build index
    index = VectorStoreIndex(nodes)

    print("Index created!")
    return index

# 4. Retrieval Augmented generation (RAG)
def generate_answer(query, index):

    # Get relevant data with query similarity search
    retriever = index.as_retriever()
    nodes = retriever.retrieve(query)
    texts = [node.node.text for  node in nodes]

    print("Retrieved texts!", texts)

    # Generate answer with OpenAI
    model = ChatOpenAI(model_name="gpt-3.5-turbo-16k-0613")
    template = """
    CONTEXT: {docs}
    You are a helpful assistant, above is  some context,,
    Please answer the question, and make sure you follow ALL of the rules below:
    1. Answer the questions only based on the context provided, do not make things up
    2. Answer the questions in a helpful manner that is straight to the point, with clear structure & all relevant information that might help users answer the question
    3. Answer should be formatted in markdown
    4. If there are relevant images, video, links, they are important reference data, please include them as part of the answer

    QUESTION: {query}
    ANSWER (formatted in markdown):
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    
    response = chain.invoke({"docs":texts, "query":query})
    return response.content

url = "https://developers.webflow.com/docs/getting-started-with-apps"
query = "How to create a webflow?"
markdown = get_markdown_from_url(url)
index = create_index_from_text(markdown)
answer = generate_answer(query, index)
print(answer)\
