import os
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from opensearchpy import OpenSearch
from pydantic import BaseModel

load_dotenv()

# Create an MCP server
mcp = FastMCP("GOV.UK Chat Search")

INDEX_NAME = "govuk_chat_chunked_content"
EMBEDDING_MODEL = "text-embedding-3-large"

search_client = OpenSearch(
    hosts=[os.getenv("OPENSEARCH_URL")],
    http_auth=(os.getenv("OPENSEARCH_USERNAME"), os.getenv("OPENSEARCH_PASSWORD")),
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_ACCESS_TOKEN"))


class SearchResult(BaseModel):
    url: str
    score: float
    document_type: str
    title: str
    description: Optional[str]
    heading_hierarchy: list[str]
    html_content: str


def semantic_search(search_query: str) -> list[SearchResult]:
    embedding_response = openai_client.embeddings.create(
        input=search_query, model=EMBEDDING_MODEL
    )

    embedding = embedding_response.data[0].embedding

    search_response = search_client.search(
        index=INDEX_NAME,
        body={
            "size": 5,
            "query": {
                "knn": {
                    "openai_embedding": {
                        "vector": embedding,
                        "k": 5,
                    }
                }
            },
            "_source": {"exclude": ["openai_embedding"]},
        },
    )

    results = []
    for hit in search_response["hits"]["hits"]:
        result = hit["_source"]
        result["url"] = f"https://www.gov.uk{result['exact_path']}"
        result["score"] = hit["_score"]
        results.append(SearchResult(**result))

    return results


@mcp.tool()
def fetch_govuk_content_chunks(search_query: str) -> list[SearchResult]:
    """Retrieve GOV.UK Content to answer queries related to the UK Government"""

    return semantic_search(search_query)
