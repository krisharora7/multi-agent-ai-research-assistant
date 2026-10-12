from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from rich import print
from dotenv import load_dotenv
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str)-> str:
    ''' this tool searchs the web for recent and reliable information about the given topic. Return Titles, URLs and snippet'''
    results = tavily.search(query=query, max_results=5)
    out=[]

    for r in results['results']:
        # take snippet upto 300 chararcters
        out.append(f"Title: {r['title']} \n URL: {r['url']} \n Snippet: {r['content'][:300]} \n")

    # convert out list back to a string with this .join
    return '\n-----\n'.join(out)

@tool
def scrape_url(url: str) -> str:
    '''Scrape and return clean text content from a given url for deeper reading.'''
    try:
        # timeout says to wait 8 seconds idle if we got no response may be due to any error like network error. header makes it more human so that website shouldn't ban us as a bot
        resp = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        # resp.text: The HTML received from the website. "html.parser": Python's built-in HTML parser, which BeautifulSoup uses to interpret the HTML structure.
        soup = BeautifulSoup(resp.text, "html.parser")
        # decompose() removes the selected element and its contents from the parsed tree. tags like script, style, nav, footer doesn't have any valuable information
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        # separator=' ' inserts a space between text fragments so adjacent elements don't get accidentally joined together.
        # strip=True removes leading and trailing whitespace from extracted fragments. and we will return first 3000 cahracters
        return soup.get_text(separator=' ',strip=True)[:3000]
    except Exception as e:
        return f"could not scrape url: {str(e)}"
