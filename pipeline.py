from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
from rich import print

def run_research_pipeline(topic: str) -> dict:
    # we will maintain a state dictionary for chat history
    state={}

    # step 1 -> search agent
    print('\n'+'= '*50)
    print("step 1 -> search agent is working...")
    print('= '*50)

    search_agent = build_search_agent()
    search_results = search_agent.invoke({
        'messages':[
            ('user',f'find recent, reliable and detailed information about: {topic}, use available tool if required and list the URLs/sources at end')
        ]
    })
    state['search_results'] = search_results['messages'][-1].content
    print('\n search results -> \n', state['search_results'])

    # step 2 -> reader agent
    print('\n'+'= '*50)
    print("step 2 -> reader agent is scraping top results...")
    print('= '*50)

    reader_agent = build_reader_agent()
    reader_results = reader_agent.invoke({
        'messages':[
            (
                'user', f'based on the following search results about {topic}\n\n'
                f'pick the most relevant urls and scrape it for deeper content using the available scrape_url tool. \n\n'
                f'search results : \n {state["search_results"][-800:]}'
            )
        ]
    })
    state['scraped_content'] = reader_results['messages'][-1].content
    print('\n scraped results -> \n', state['scraped_content'])

    # step 3 -> writer chain
    print('\n'+'= '*50)
    print("step 3 -> writer is drafting the report...")
    print('= '*50)

    research_combined = (
        f"SEARCH RESULTS: \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED RESULTS: \n {state['scraped_content']}"
    )

    state['report'] = writer_chain.invoke({
        'topic':topic,
        'research':research_combined
    })
    print('\n Final Report -> \n', state['report'])
   
    # step 4 -> critic chain
    print('\n'+'= '*50)
    print("step 4 -> Critic is reviewing the report...")
    print('= '*50)

    state['feedback'] = critic_chain.invoke({
        'report':state['report']
    })
    print('\n Critic Report -> \n', state['feedback'])

    return state

if __name__== "__main__":
    topic = input("\n Enter a Research Topic: ")
    run_research_pipeline(topic)