from settings import config
from openai import OpenAI
from langchain.schema import Document
from src.publishers.google_docs import upload_to_google_docs
from src.crud.get_semantic_data import get_relevant_docs
from src.data_loaders.slack_fetcher import slack_client
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class BlogGenerationError(Exception):
    pass

class BlogGenerator:
    def __init__(self):
        try:
            self.client = OpenAI(api_key=config.OPEN_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise BlogGenerationError("Failed to initialize blog generator")

    def generate_blogs(self, vector_db, keyword: str) -> List[Dict[str, Any]]:
        try:
            docs = vector_db.get(include=["documents"])["documents"]
            examples = [{"content": doc} for doc in docs]

            context = "\n".join(get_relevant_docs(examples, keyword))
            if not context:
                logger.warning(f"No relevant context found for keyword: {keyword}")
                raise BlogGenerationError("No relevant context found for the given keyword")

            # Step 1: Summarize internal knowledge
            summary_prompt = f"""
                You are a summarization assistant for Panda Money, a global fintech platform focused on improving cross-border payments.

                You will receive internal content collected from Slack and Confluence. Your task is to extract the most relevant information to support a blog on the topic:

                **"{keyword}"**

                Please summarize using the following structure:

                ---

                1. **Key Talking Points**  
                Summarize the most relevant insights, trends, or arguments that support the blog topic.

                2. **Panda Money Product Mentions**  
                Extract all platform-specific references such as the Google exchange rate, NFT rewards, instant transfers, fee transparency, etc.

                3. **Competitive / Market Insights**  
                List mentions of other platforms (e.g., SWIFT, Wise, PayPal), industry trends, or user frustrations with existing solutions.

                4. **Customer Pain Points**  
                Highlight common challenges discussed internally (e.g., slow remittance, hidden fees, confusing rates, lack of transparency).

                5. **Quotes or On-Brand Phrases**  
                Pull in strong lines, internal taglines, or memorable phrases that represent Panda’s voice and positioning.

                ---

                Keep it clear, concise, and focused on helping the next step: high-quality SEO blog generation.
            """

            summary_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": summary_prompt + "\n\n" + context}],
                max_tokens=1000,
                temperature=0.3
            )
            internal_summary = summary_response.choices[0].message.content.strip()

            # Step 2: Generate SEO-enriched blog
            blog_prompt = f"""
                You are an expert SEO content writer for Panda Money — a platform that helps users send money globally with speed, fairness, and transparency.

                Your job is to write a natural, editorial-style blog post that ranks well on Google and reads beautifully for humans. The blog is based on a user-defined topic and real internal knowledge.

                ---

                ## 📝 Topic:
                **"{keyword}"**

                ## 🔍 Internal Knowledge Summary:
                {internal_summary}

                ## 📈 Real-Time SEO Enrichment:
                - **Primary Keyword**: "{keyword}"
                - **Long-Tail & Semantic Variants**: 
                - "{keyword} guide"  
                - "how to {keyword}"  
                - "cross-border {keyword} tips"
                - **Related Search Intent**: 
                - "Is {keyword} safe?"  
                - "Best way to {keyword}"  
                - "{keyword} for beginners"
                - **Search-Based FAQ Suggestions**: 
                - "What is the Panda Money exchange rate?"  
                - "How does Panda Money compare to Wise?"  
                - "Are Panda’s transfers instant?"

                ## 🌍 Panda Default Parameters:
                - Audience: customers with the need to transfer currency across borders  
                - Tone: friendly and informative  
                - Geo: any country to any country  
                - Feature focus: Google exchange rate  
                - FAQ section: yes

                ---

                ## ✏️ Writing Instructions:

                - Write a **natural, narrative-style blog** — no robotic headers or SEO blocks. Flow like an article from Stripe, Wise, or TechCrunch.
                - Use **keywords naturally** throughout the blog (1–2% keyword density).
                - Embed `[COMMENT: ...]` wherever user review is needed:
                - Feature claims (e.g., speed, coverage, NFT rewards)
                - Audience or geography assumptions
                - CTA alignment with current campaigns
                - Any technical or compliance-related product mentions
                - Use an **organic soft paragraph CTA** at the end of the blog.
                - Include a **3-question FAQ** section, based on enriched queries.
                - Add a structured **JSON-LD schema block** for Article + FAQ.
                - Include a list at the end labeled:
                **Referenced Resources in This Blog**, containing any internal Panda links used in the copy:
                - “Google exchange rate” → `/how-panda-beats-bank-rates`
                - “NFT rewards” → `/believers-nft-remittance-rewards`
                - “Fee transparency” → `/eliminate-hidden-fees-cross-border`

                ---

                ## 🧱 Output Structure:

                1. **Blog Body** (3-5 paragraphs of natural flow, no headings)  
                2. **Soft Paragraph CTA** (Method 2, woven into closing paragraph)  
                3. **FAQ Section** (3 questions with clear, concise answers)  
                4. **Referenced Resources in This Blog** (list internal links mentioned)  
                5. **JSON-LD Schema Block** (Article + FAQ markup)

                ---

                Your writing should feel authentic, helpful, and aligned with Panda Money’s mission: fast, fair, transparent global finance for everyone.
            """

            final_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior SEO blog writer for Panda Money."},
                    {"role": "user", "content": blog_prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )

            blog_content = final_response.choices[0].message.content.strip()
            title = blog_content.split("\n")[0].replace("Title:", "").strip() if "Title:" in blog_content else f"Generated Blog on {keyword}"
            body = blog_content.strip()

            # Post to Slack and return
            try:
                self._post_to_slack(title, body)
            except Exception as e:
                logger.error(f"Failed to post blog to Slack: {e}")

            return [{
                "title": title,
                "content": body,
                "type": "SEO Thought Leadership"
            }]

        except Exception as e:
            logger.error(f"Blog generation failed: {e}")
            raise BlogGenerationError(f"Failed to generate blogs: {str(e)}")

    def _post_to_slack(self, title: str, content: str) -> None:
        try:
            doc_link = upload_to_google_docs(title, content)
            response = slack_client.chat_postMessage(
                channel=config.SLACK_CHANNEL_ID,
                text=f"*{title}*\nRead the full blog here: {doc_link}"
            )
            if not response["ok"]:
                raise Exception(f"Slack API error: {response.get('error', 'Unknown error')}")
        except Exception as e:
            logger.error(f"Failed to post to Slack: {e}")
            raise
