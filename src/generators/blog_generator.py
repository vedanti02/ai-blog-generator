from settings import config
from openai import OpenAI
from langchain.schema import Document
from src.publishers.google_docs import upload_to_google_docs
from src.crud.get_semantic_data import get_relevant_docs
from src.data_loaders.slack_fetcher import slack_client
import logging
from typing import Optional, List, Dict, Any

# Set up logging
logger = logging.getLogger(__name__)

class BlogGenerationError(Exception):
    """Custom exception for blog generation errors."""
    pass

class BlogGenerator:
    def __init__(self):
        try:
            self.client = OpenAI(api_key=config.OPEN_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise BlogGenerationError("Failed to initialize blog generator")

    def generate_blogs(self, vector_db, embeddings, keyword: str) -> List[Dict[str, Any]]:
        """
        Generate blog posts with comprehensive error handling.
        
        Args:
            vector_db: Vector database instance
            embeddings: Embeddings model
            keyword: Topic keyword for blog generation
            
        Returns:
            List of generated blog posts with their metadata
            
        Raises:
            BlogGenerationError: If blog generation fails
        """
        try:
            # Get relevant documents
            docs = vector_db.get(include=["documents"])["documents"]
            examples = [{"content": doc} for doc in docs]

            context = "\n".join(get_relevant_docs(examples, embeddings, keyword))
            if not context:
                logger.warning(f"No relevant context found for keyword: {keyword}")
                raise BlogGenerationError("No relevant context found for the given keyword")

            # blog prompts
            blog_types = [
                
                f"""Write a thought-provoking thought leadership blog about {keyword} that positions us as industry experts:
                - First paragraph: Open with a compelling industry challenge or opportunity that resonates with readers
                - Second paragraph: Share unique insights and expert analysis, backed by data and market research
                - Third paragraph: Provide actionable recommendations and future predictions that readers can implement
                
                Make it stand out by:
                - Challenging conventional wisdom
                - Providing fresh perspectives
                - Including specific examples and case studies
                - Offering practical, implementable solutions""",
                
                f"""Write an accessible technical blog about {keyword} that makes complex concepts engaging:
                - First paragraph: Start with a real-world problem or use case that readers can relate to
                - Second paragraph: Break down technical concepts with clear examples and analogies
                - Third paragraph: Showcase future innovations and their practical applications
                
                Make it accessible by:
                - Using clear, non-technical language where possible
                - Including visual analogies and examples
                - Breaking down complex concepts into digestible parts
                - Focusing on practical applications and benefits"""
            ]

            generated_blogs = []
            for i, blog_prompt in enumerate(blog_types):
                try:
                    blog_content = self._generate_single_blog(blog_prompt, context, i)
                    if blog_content:
                        generated_blogs.append(blog_content)
                except Exception as e:
                    logger.error(f"Failed to generate blog {i+1}: {e}")
                    continue

            if not generated_blogs:
                raise BlogGenerationError("Failed to generate any blog posts")

            return generated_blogs

        except Exception as e:
            logger.error(f"Blog generation failed: {e}")
            raise BlogGenerationError(f"Failed to generate blogs: {str(e)}")

    def _generate_single_blog(self, blog_prompt: str, context: str, index: int) -> Optional[Dict[str, Any]]:
        """
        Generate a single blog post with error handling.
        
        Args:
            blog_prompt: The prompt for blog generation
            context: The context to use for generation
            index: The index of the blog type
            
        Returns:
            Dictionary containing the blog title and content, or None if generation fails
        """
        try:
            prompt = f"""
            Based on the following data, write a compelling 1200-word blog post that engages readers from start to finish.
            The blog should be professional yet conversational, with a clear narrative arc and memorable insights.

            Data:
            {context}

            {blog_prompt}
            
            Output format:
            Title: [Create a compelling, SEO-friendly title that captures attention]

            [First paragraph]
            Start with a strong hook that grabs attention. Use specific details and engaging language.
            
            [Second paragraph]
            Build on the opening with concrete examples and clear explanations. Make it informative yet engaging.
            
            [Third paragraph]
            End with impact and action. Leave readers with clear takeaways and next steps.
            """

            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert content strategist and storyteller. Write engaging, memorable content that combines professional insights with compelling narrative. Focus on clarity, impact, and reader engagement."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )

            blog_content = response.choices[0].message.content

            title_line = blog_content.split("\n")[0]
            if title_line.lower().startswith("title:"):
                title = title_line.replace("Title:", "").strip()
                blog_body = "\n".join(blog_content.split("\n")[1:]).strip()
            else:
                title = f"Generated Blog {index+1}"
                blog_body = blog_content.strip()

            # Post to Slack with error handling
            try:
                self._post_to_slack(title, blog_body)
            except Exception as e:
                logger.error(f"Failed to post blog to Slack: {e}")
                # Continue even if Slack posting fails

            return {
                "title": title,
                "content": blog_body,
                "type": ["Company Update", "Thought Leadership", "Technical Deep-Dive"][index]
            }

        except Exception as e:
            logger.error(f"Failed to generate blog {index+1}: {e}")
            return None

    def _post_to_slack(self, title: str, content: str) -> None:
        """
        Post blog content to Slack with error handling.
        
        Args:
            title: Blog title
            content: Blog content
            
        Raises:
            Exception: If posting to Slack fails
        """
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
