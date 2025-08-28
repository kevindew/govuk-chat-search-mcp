# GOV.UK Chat Search MCP Server

This is a very basic proof of concept of using a GOV.UK Chat OpenSearch instance
with [the Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk).

Results were a bit mixed using this with Claude Desktop, it seemed quite easy
for it to hit an error of "Claude hit the maximum length for this conversation"
on some topics. I guessed that that might mean too many tokens were used, so
I cut the number of search results down (drastically) to just 5 returned.

## Running it

To run it you need the credentials of an OpenSearch instance and configure these in a .env file. 
You will also need AWS credentials to access Bedrock, these can be created for a GOV.UK developer using `./export-aws-credentials.sh` where the results will be written to `.env.aws` and will expire.

To use it you can run:

```
uv run mcp dev server.py
```

to get the inspector.

To configure it in your Claude desktop there is a `uv run mcp install` command,
however this couldn't handle dependencies for me so I put:

```
    "GOV.UK Chat Search": {
      "command": "/Users/kevin.dew/.pyenv/versions/3.13.2/bin/uv",
      "args": [
        "run",
        "--directory",
        "/Users/kevin.dew/dev/govuk-chat-search-mcp",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "server.py"
      ]
    }
```

in my Claude config.
