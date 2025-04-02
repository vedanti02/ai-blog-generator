from langchain_openai import ChatOpenAI
import settings.config as config
import time
from typing import List

def chunk_text(text_list: List[str], max_chunk_size: int = 3000) -> List[str]:
    """Split text into smaller chunks to avoid token limits."""
    chunks = []
    current_chunk = []
    current_size = 0
    
    for text in text_list:
        text_size = len(text.split())
        if current_size + text_size > max_chunk_size:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [text]
            current_size = text_size
        else:
            current_chunk.append(text)
            current_size += text_size
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def generate_summary(text_list: List[str], source_name: str, max_retries: int = 3) -> str:
    """Generate a summary with rate limit handling and retries."""
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.7, openai_api_key=config.OPEN_API_KEY)
    
    # Split text into manageable chunks
    chunks = chunk_text(text_list)
    summaries = []
    
    for chunk in chunks:
        retries = 0
        while retries < max_retries:
            try:
                prompt = f"Summarize the following {source_name} data:\n\n{chunk}"
                summary = llm.predict(prompt)
                summaries.append(summary)
                break
            except Exception as e:
                if "rate_limit_exceeded" in str(e):
                    retries += 1
                    if retries < max_retries:
                        wait_time = 20 ** retries  # Exponential backoff
                        print(f"Rate limit hit, waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                    else:
                        print(f"Max retries reached for chunk. Skipping...")
                        summaries.append("(Summary unavailable due to rate limits)")
                else:
                    print(f"Error generating summary: {e}")
                    summaries.append("(Summary unavailable due to error)")
                    break
    
    # Combine all chunk summaries
    if summaries:
        final_prompt = f"Combine these summaries into a coherent whole:\n\n{' '.join(summaries)}"
        try:
            return llm.predict(final_prompt)
        except Exception as e:
            print(f"Error combining summaries: {e}")
            return " ".join(summaries)
    else:
        return "No summaries generated."