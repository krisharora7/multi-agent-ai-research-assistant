# Multi-Agent AI Research Assistant

A Python-based research assistant that combines web search, webpage extraction, report generation, and AI-powered review into a single workflow.

## Overview

Researching a topic often involves more than finding a few relevant links. Useful research requires gathering information from multiple sources, reading the relevant material, organizing the findings, and reviewing the final write-up for clarity and completeness.

This project explores how a multi-stage AI workflow can help automate that process.

The system accepts a research topic and passes it through four stages: a search agent retrieves relevant web results, a reader agent selects pages for deeper reading, a writer chain turns the gathered material into a structured report, and a critic chain evaluates the report and provides feedback.

The project is built with LangChain, Groq, Tavily, Requests, BeautifulSoup, and Streamlit. It also includes a command-line entry point for running the research pipeline directly.

## Key Features

- **Web research:** Searches for relevant information using the Tavily Search API.
- **Tool-enabled agents:** Uses LangChain agents to decide when and how to invoke search and scraping tools.
- **Webpage extraction:** Retrieves webpage HTML and extracts readable text for further analysis.
- **Structured report generation:** Produces reports organized into an introduction, key findings, conclusion, and sources.
- **AI-powered critique:** Reviews the generated report and returns a score, strengths, areas for improvement, and an overall verdict.
- **Modular implementation:** Separates tools, agent and chain definitions, pipeline orchestration, and the user interface into different files.
- **Streamlit interface:** Provides a graphical interface for interacting with the research workflow.
- **Alternative execution:** Supports running the pipeline from the terminal without relying on the graphical interface.

## How It Works

The system follows a sequential workflow. Each stage has a specific responsibility, and the output of one stage becomes input for the next.

### 1. Search Agent

The process begins with a research topic supplied by the user.

The search agent uses the custom `web_search` tool, which calls the Tavily API to retrieve up to five search results. Each result is formatted with its title, URL, and a short excerpt from the returned content.

The search results give the next stage a starting point for identifying relevant sources.

**Implemented with:** LangChain agents and Tavily Search API.

### 2. Reader Agent

Search excerpts may not contain enough information to support a detailed report. The reader agent therefore uses the custom `scrape_url` tool to retrieve and examine selected webpages.

The scraper uses Requests to fetch HTML and BeautifulSoup to parse the page. It removes common non-content elements, including scripts, styles, navigation, and footers, before extracting readable text.

The extracted content is limited to 3,000 characters per scraping call to keep the amount of text passed through the workflow manageable.

**Implemented with:** LangChain agents, Requests, and BeautifulSoup.

### 3. Writer Chain

The search results and extracted webpage content are combined into a research context. The writer chain passes this context, along with the original topic, to the language model through a structured prompt.

The model is instructed to produce a detailed report containing:

- Introduction
- Key Findings, with at least three explained points
- Conclusion
- Sources, listing the URLs found in the research

This stage transforms collected information into a more readable and organized document.

**Implemented with:** LangChain prompt templates, the Groq-hosted language model, and `StrOutputParser`.

### 4. Critic Chain

After the report is generated, a separate critic chain reviews it.

The critic is prompted to provide a score out of 10, identify strengths, suggest areas for improvement, and give a one-line verdict. Its feedback is returned alongside the report.

This review stage adds a second evaluation pass instead of treating the writer's first output as the final word.

The current implementation generates critique and feedback; it does not automatically revise the report or guarantee that every claim has been fact-checked.

**Implemented with:** LangChain prompt templates, the language model, and `StrOutputParser`.

### Workflow at a Glance

```text
                  Research Topic
                        |
                        v
                  Search Agent
                  (Tavily API)
                        |
                        v
                  Reader Agent
              (Requests + BeautifulSoup)
                        |
                        v
                 Research Context
                        |
                        v
                  Writer Chain
                (Report Generation)
                        |
                        v
                  Critic Chain
                 (Report Review)
                        |
                        v
             Report + Critic Feedback
                        |
                        v
                 Streamlit UI
```

The terminal pipeline can also display the stages and results directly in the console.

## Technology Stack

| Technology           | Role in the project                                       |
| -------------------- | --------------------------------------------------------- |
| Python               | Core programming language                                 |
| LangChain            | Agent creation, tool integration, prompts, and chains     |
| Groq                 | Hosts the language model used for generation and critique |
| `openai/gpt-oss-20b` | Language model configured in the current implementation   |
| Tavily Search API    | Retrieves web search results                              |
| Requests             | Fetches webpage HTML                                      |
| BeautifulSoup        | Parses HTML and extracts readable text                    |
| `python-dotenv`      | Loads API credentials from environment variables          |
| Rich                 | Improves console output                                   |
| Streamlit            | Provides the user interface                               |

## Project Structure

```text
multi-agent-ai-research-assistant/
│
├── app.py             # Streamlit user interface
├── tools.py           # Web search and webpage scraping tools
├── agents.py          # Search/reader agents and writer/critic chains
├── pipeline.py        # Sequential research workflow
├── requirements.txt   # Python dependencies
├── .env.example       # Template for required API keys
├── .gitignore         # Files excluded from version control
└── README.md          # Project documentation
```

### File Responsibilities

- **`tools.py`** defines the two custom tools: `web_search` and `scrape_url`.
- **`agents.py`** configures the Groq language model, creates the search and reader agents, and defines the writer and critic chains.
- **`pipeline.py`** coordinates the stages, maintains the results in a state dictionary, and provides a command-line entry point.
- **`app.py`** contains the Streamlit interface.
- **`requirements.txt`** lists the Python packages needed to run the project.

## Getting Started

### Prerequisites

Before running the project, make sure you have:

- Python 3.10 or later
- A Groq API key
- A Tavily API key
- Git, if you intend to clone the repository

API access and usage limits depend on the providers' current plans.

### 1. Clone the repository

Replace the placeholder URL with the URL of your GitHub repository.

```bash
git clone https://github.com/YOUR_USERNAME/multi-agent-ai-research-assistant.git
cd multi-agent-ai-research-assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project's root directory and add your API keys:

```dotenv
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Use your own keys in your local environment. Never commit `.env` or publish API credentials in source code, screenshots, or logs.

### 5. Run the application

To launch the Streamlit interface:

```bash
streamlit run app.py
```

To run the command-line research pipeline:

```bash
python pipeline.py
```

When running the pipeline directly, enter a research topic when prompted. The workflow then executes the search, reading, writing, and critique stages in sequence.

## Example Use Case

Suppose the research topic is:

```text
Recent developments in solid-state batteries
```

The system searches for relevant web sources, selects pages for deeper reading, combines the available material, and generates a report covering the topic's background and key findings. It then produces a separate critique containing a score, strengths, suggested improvements, and a verdict.

The quality of the output depends on the sources retrieved, the content that can be extracted from those sources, and the language model's response. The results should therefore be reviewed before being used in academic or professional work.

## Design Decisions

### Why use separate agents and chains?

Search and webpage reading require the model to choose whether to use a tool and which input to pass to it. The writer and critic, in contrast, perform more defined transformations on content already gathered by the pipeline.

Separating these responsibilities keeps the implementation modular and makes it easier to inspect and modify individual stages.

### Why combine search results with scraped content?

Search excerpts provide a quick overview of relevant pages, while extracted webpage text can provide additional context. Combining both gives the writer more material than relying on search excerpts alone.

### Why include a critic stage?

A generated report can be well written while still having gaps, unclear reasoning, or unsupported statements. The critic provides a separate review pass to highlight possible weaknesses. Its score is an LLM-generated assessment, not an objective benchmark or a guarantee of factual accuracy.

## Current Limitations

- The search stage is limited to the results returned by Tavily.
- Webpage extraction depends on the page's HTML structure, network access, and the site's restrictions.
- The scraper removes common page elements but is not a full browser renderer and may not extract content from JavaScript-heavy websites.
- Each scraping call returns at most 3,000 characters, so longer pages may be only partially represented.
- The pipeline runs its stages sequentially rather than coordinating them through a dynamic planning graph.
- The critic provides feedback, but the current pipeline does not automatically revise the report based on that feedback.
- Search results, extracted text, and model-generated summaries can contain inaccuracies. Source links and factual claims should be checked independently.
- API availability, latency, and usage limits depend on the external services.

## Possible Future Improvements

- Add retries, clearer error handling, and more robust handling of inaccessible webpages.
- Improve source selection and preserve source attribution for individual findings.
- Support configurable research depth and source limits.
- Add an optional revision pass in which the writer responds to the critic's feedback.
- Add tests for the tools and pipeline stages.
- Improve observability so failures and intermediate results are easier to diagnose.

These are potential extensions, not features claimed to be implemented in the current version.

## Learning Outcomes

This project provided practical experience with:

- Building tool-enabled agents using LangChain
- Integrating an external search API into an LLM workflow
- Fetching and parsing webpage content
- Creating prompt-driven generation and review chains
- Passing information between sequential pipeline stages
- Managing API credentials through environment variables
- Connecting a research backend to a Streamlit interface

##
