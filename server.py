import json
import os
from typing import Optional

import boto3
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from opensearchpy import OpenSearch
from pydantic import BaseModel

load_dotenv()

# Create an MCP server
mcp = FastMCP("GOV.UK Chat Search")

INDEX_NAME = "govuk_chat_chunked_content"

search_client = OpenSearch(
    hosts=[os.getenv("OPENSEARCH_URL")],
    http_auth=(os.getenv("OPENSEARCH_USERNAME"), os.getenv("OPENSEARCH_PASSWORD")),
)

bedrock = boto3.client('bedrock-runtime', region_name='eu-west-1')


class SearchResult(BaseModel):
    url: str
    score: float
    document_type: str
    title: str
    description: Optional[str]
    heading_hierarchy: list[str]
    html_content: str


def semantic_search(search_query: str) -> list[SearchResult]:
    embedding_response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({ "inputText": search_query })
    )

    response_body = json.loads(embedding_response['body'].read())

    search_response = search_client.search(
        index=INDEX_NAME,
        body={
            "size": 5,
            "query": {
                "knn": {
                    "titan_embedding": {
                        "vector": response_body["embedding"],
                        "k": 5,
                    }
                }
            },
            "_source": {"exclude": ["titan_embedding"]},
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
