# Blog Generation Bot Documentation

## Overview
The Blog Generation Bot is an AI-powered system that automatically generates, manages, and publishes blog content based on data from various sources including Slack conversations and Confluence documents. The system uses advanced language models and vector databases to create engaging, relevant content.

## System Architecture

### Core Components

1. **Data Collection Layer**
   - `src/data_loaders/`: Handles data ingestion from various sources
     - `slack_fetcher.py`: Fetches messages from Slack channels
     - `confluence_fetcher.py`: Retrieves content from Confluence pages

2. **Data Processing Layer**
   - `src/data_preprocessors/`: Processes and prepares data for analysis
   - `src/crud/`: Handles database operations
     - `get.py`: Retrieves data from vector database
     - `update.py`: Updates content in the database
     - `store.py`: Stores processed data

3. **Content Generation Layer**
   - `src/generators/`: Manages content creation
     - `blog_generator.py`: Generates blog posts using GPT-4
     - `summary_generator.py`: Creates content summaries

4. **Publishing Layer**
   - `src/publishers/`: Handles content distribution
     - `google_docs.py`: Publishes content to Google Docs
     - `confluence_appender.py`: Updates Confluence pages

5. **Event Handling Layer**
   - `src/event_listener/`: Manages system events
     - `slack_listener.py`: Handles Slack interactions and commands

6. **API Layer**
   - `src/routes/`: Provides API endpoints
     - `support_routes.py`: Handles support-related API requests

### Key Technologies

- **Language Models**: OpenAI GPT-4 Turbo
- **Vector Database**: ChromaDB
- **API Framework**: FastAPI
- **Document Processing**: LangChain
- **Integration Platforms**: 
  - Slack (for communication and commands)
  - Confluence (for content storage)
  - Google Docs (for blog publishing)

## Features

### 1. Blog Generation
- Automatically generates three types of blog posts:
  - Company Updates
  - Thought Leadership
  - Technical Deep-Dives
- Each blog post includes:
  - SEO-friendly title
  - Three focused paragraphs (100 words each)
  - Data-driven insights
  - Clear call-to-action

### 2. Slack Integration
- Supports multiple slash commands:
  - `/blog`: Generates new blog posts
  - `/get`: Retrieves information from the knowledge base
  - `/update`: Updates existing content
  - `/support`: Provides support assistance

### 3. Content Management
- Automatic content summarization
- Regular updates to Confluence pages
- Vector-based semantic search
- Content deduplication and preprocessing

### 4. Support System
- AI-powered support bot
- REST API endpoints for support queries
- Context-aware responses

## Setup and Installation

### Prerequisites
- Python 3.8+
- OpenAI API key
- Slack Bot Token
- Confluence API credentials
- Google Docs API credentials

### Environment Variables
Required environment variables in `.env`:
```
OPEN_API_KEY=your_openai_api_key
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_APP_TOKEN=your_slack_app_token
SLACK_CHANNEL_ID=your_channel_id
SLACK_SIGNING_SECRET=your_signing_secret
CONFLUENCE_URL=your_confluence_url
CONFLUENCE_USERNAME=your_username
CONFLUENCE_API_KEY=your_api_key
CONFLUENCE_SPACE=your_space_key
CHROMA_DB_PATH=path_to_chroma_db
```

### Installation Steps
1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables
5. Initialize the vector database

## Usage

### Starting the Application
```bash
python src/main.py
```

### Available Commands

#### Blog Generation
```bash
/blog [keyword]
```
Generates a blog post about the specified keyword.

#### Information Retrieval
```bash
/get [query]
```
Retrieves relevant information from the knowledge base.

#### Content Update
```bash
/update
```
Opens a modal to update existing content.

#### Support
```bash
/support [question]
```
Gets AI-powered support for your question.

## API Endpoints

### Support Chat
```
POST /support/chat
```
Request body:
```json
{
    "message": "your question",
    "session_id": "optional_session_id"
}
```

## Maintenance and Monitoring

### Logging
- Application logs are stored in the standard output
- Error handling and logging are implemented throughout the application

### Database Management
- ChromaDB is used for vector storage
- Regular cleanup and optimization are recommended

### Performance Optimization
- Content is cached in the vector database
- Regular updates ensure fresh content
- Rate limiting is implemented for API calls

## Security Considerations

1. **API Security**
   - All API keys are stored in environment variables
   - Secure token management for external services

2. **Data Protection**
   - Sensitive information is not stored in logs
   - Secure handling of user data

3. **Access Control**
   - Slack command permissions
   - API endpoint authentication

## Troubleshooting

### Common Issues
1. **API Connection Issues**
   - Verify API keys and tokens
   - Check network connectivity
   - Validate service credentials

2. **Content Generation Problems**
   - Check OpenAI API quota
   - Verify input data quality
   - Monitor token usage

3. **Database Issues**
   - Verify ChromaDB connection
   - Check storage permissions
   - Monitor database size

## Future Enhancements

1. **Planned Features**
   - Enhanced content analytics
   - Multi-language support
   - Advanced content scheduling
   - Improved error handling

2. **Integration Opportunities**
   - Additional content sources
   - More publishing platforms
   - Advanced analytics tools

## Support and Contact

For technical support or questions, please contact the development team or raise an issue in the repository. 