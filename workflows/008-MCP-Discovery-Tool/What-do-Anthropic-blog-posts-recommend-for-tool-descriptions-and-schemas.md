Yes—there are several Anthropic engineers (plus a few protocol/community maintainers) who consistently publish concrete, reusable patterns for “skills/tools” (tool schemas, ergonomics, discovery, namespacing, eval-driven iteration), and they mostly publish on Anthropic’s Engineering/Research blogs and in MCP community docs/issues. [github](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1382)

## Key Anthropic voices (tool/skill patterns)

- **Bin Wu** (Anthropic) writes about scaling tool use to large tool libraries, including patterns like “search tools on-demand” (tool discovery), “programmatic tool calling” (orchestration in code), and “tool use examples” (teaching conventions beyond JSON Schema) in Anthropic’s engineering blog post “Introducing advanced tool use on the Claude Developer Platform.” [github](https://github.com/modelcontextprotocol)
- That same “advanced tool use” post also lists additional contributors (e.g., Adam Jones, Artur Renault, Henry Tay, Jake Noble, Nathan McCandlish, Noah Picard, Sam Jiang) as part of the Claude Developer Platform team, which is a good starting set of names if you’re tracking who’s shaping practical tool ergonomics inside Anthropic. [github](https://github.com/modelcontextprotocol)
- **Ken Aizawa** (Anthropic) writes directly about “writing effective tools for AI agents,” including specific tool design principles like namespacing, returning high-signal context, token-efficient responses (pagination/truncation), and evaluation-driven iteration, published on Anthropic Engineering. [github](https://github.com/modelcontextprotocol/servers)
- That “Writing effective tools…” post also credits contributors across Research/MCP/Product Engineering/Applied AI (e.g., Theodora Chu, John Welsh, David Soria Parra, Adam Jones, Barry Zhang, Zachary Witten, Daniel Jiang), which can help you identify additional Anthropic folks active around tool/MCP design. [github](https://github.com/modelcontextprotocol/servers)
- **Erik Schluntz** and **Barry Zhang** (Anthropic) are explicitly positioned as authors of “Building Effective AI Agents,” which frames agent/tool architecture as composable patterns and calls out MCP as a way to integrate “a growing ecosystem of third-party tools with a simple client implementation.” [block.github](https://block.github.io/goose/blog/2025/04/10/visual-guide-mcp/)

## Protocol/community voices (tool patterns)

- **MCP docs (modelcontextprotocol.io)** include tool design best practices (clear names/descriptions, JSON Schema, examples, atomic tools, error handling, timeouts, rate limiting, logging) and operational concerns like tool name conflicts and disambiguation strategies; this is a canonical “patterns” source even when it’s not tied to a single author. [block.github](https://block.github.io/goose/blog/2025/04/10/visual-guide-mcp/)
- The MCP community also discusses tool-description vs schema-description structure as a pattern: “SEP-1382: Documentation Best Practices for MCP Tools” argues for separation of concerns and “LLM-first” documentation conventions (in GitHub issues under the MCP spec repo). [github](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1382)
- **J. Lowin (jlowin)** (FastMCP) is a prominent community voice for MCP server/client ergonomics; FastMCP describes a pattern vocabulary of **Components / Providers / Transforms** (what you expose, where it comes from, how it’s presented), published in the project’s GitHub README/docs pointers. [github](https://github.com/jlowin/fastmcp)

## Where they publish

- **Anthropic Engineering blog**: long-form, implementation-oriented posts on tool design (e.g., “advanced tool use,” “writing tools for agents”). [github](https://github.com/modelcontextprotocol/servers)
- **Anthropic Research blog**: higher-level agent architecture patterns with practical guidance, often with appendices that get very tool/format-specific (e.g., ACI / “prompt engineering your tools”). [block.github](https://block.github.io/goose/blog/2025/04/10/visual-guide-mcp/)
- **Model Context Protocol docs**: protocol-level best practices and interoperability patterns (tool annotations, discovery/invocation, conflict resolution). [block.github](https://block.github.io/goose/blog/2025/04/10/visual-guide-mcp/)
- **GitHub issues/SEPs in MCP repos**: community-driven design discussions and proposed standards (e.g., SEP-1382). [github](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1382)
- **YouTube (community + Anthropic-adjacent)**: e.g., a discussion featuring **Anthropic’s Alex Albert** and **Erik Schluntz** focused on multi-agent patterns and “best practices for using skills, MCP servers, and tools,” with timestamps in the description. [youtube](https://www.youtube.com/watch?v=uhJJgc-0iTQ)

## Notes on “Twitter/X” and papers

Anthropic engineers often share work via the Engineering/Research sites (which are the most citable, stable sources), while X/Twitter tends to be more ephemeral; I can list specific handles once you tell me which of the names above you care about most (e.g., Bin Wu vs Ken Aizawa vs Erik Schluntz).

# What do Anthropic blog posts recommend for tool descriptions and schemas
Anthropic's blog posts provide detailed, prescriptive recommendations for tool descriptions and schemas, emphasizing that **descriptions are the single most important factor** in tool performance and should be written as if onboarding a new team member. [anthropic.mintlify](https://anthropic.mintlify.app/en/docs/agents-and-tools/tool-use/implement-tool-use)

## Tool Description Best Practices

### Extreme Detail is Critical

Anthropic emphasizes that tool descriptions should be **extremely detailed** (3-4+ sentences minimum per tool): [platform.claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use)
- What the tool does
- When it should be used (and when it shouldn't)
- What each parameter means and how it affects behavior
- Important caveats or limitations
- What information the tool does NOT return [github](https://github.com/vishnu2kmohan/mcp-server-langgraph/blob/main/adr/adr-0023-anthropic-tool-design-best-practices.md)

### "Prompt-Engineering Your Tool Descriptions"

Ken Aizawa's post "Writing effective tools for AI agents" describes tool descriptions as context that **collectively steers agents toward effective behaviors**: [anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)

> "Think of how you would describe your tool to a new hire on your team. Consider the context that you might implicitly bring—specialized query formats, definitions of niche terminology, relationships between underlying resources—and make it explicit." [github](https://github.com/modelcontextprotocol/servers)

Key principles: [github](https://github.com/modelcontextprotocol/servers)
- **Make implicit context explicit**: Don't assume Claude knows specialized query formats or domain-specific terminology
- **Avoid ambiguity**: Clearly describe and enforce expected inputs/outputs with strict data models
- **Name parameters unambiguously**: Instead of generic names like `query`, use specific names that indicate purpose

### Descriptions Over Examples

Anthropic recommends **prioritizing descriptions over examples**: [platform.claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use)
- Comprehensive explanations of purpose and parameters matter more than usage examples
- Only add examples after fully fleshing out the description
- Examples can be included in the description or accompanying prompt, but are secondary [anthropic.mintlify](https://anthropic.mintlify.app/en/docs/agents-and-tools/tool-use/implement-tool-use)

### Token Efficiency Guidelines

For tools that return large outputs, descriptions should specify: [github](https://github.com/vishnu2kmohan/mcp-server-langgraph/blob/main/adr/adr-0023-anthropic-tool-design-best-practices.md)
- **Token limits**: Expected response sizes
- **Response times**: Performance characteristics
- **Pagination/truncation strategies**: How to handle large result sets efficiently

## JSON Schema Best Practices

### Standard JSON Schema Format

Anthropic uses **standard JSON Schema format** for `input_schema` definitions: [codesignal](https://codesignal.com/learn/courses/developing-claude-agents-with-tool-integration/lessons/writing-tool-schemas-for-claude-1)

```json
{
  "name": "get_weather",
  "description": "Retrieves current weather data for a specified location...",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "City and state, e.g., San Francisco, CA"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "Temperature unit preference"
      }
    },
    "required": ["location"]
  }
}
```

### Property-Level Descriptions

Every property in the schema should have its own **detailed description**: [github](https://github.com/aws-samples/anthropic-on-aws/blob/main/complex-schema-tool-use/README.md)
- Describe what the parameter means
- Explain how it affects tool behavior
- Provide format examples (e.g., "City and state, e.g., San Francisco, CA")
- Specify constraints or valid ranges

Anthropic notes that "the description is one of the most important pieces of information" and "should be applied for each component of the JSON schema". [github](https://github.com/aws-samples/anthropic-on-aws/blob/main/complex-schema-tool-use/README.md)

### Parameter Naming Conventions

Use **unambiguous, descriptive parameter names**: [anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)
- ❌ Bad: `query`, `data`, `input`
- ✅ Good: `search_query`, `customer_name`, `transaction_id`

### Required vs Optional Parameters

Clearly distinguish required from optional parameters using the `required` array: [docs.agentops](https://docs.agentops.ai/v2/examples/anthropic)
- List all mandatory parameters in the `required` field
- Document default values for optional parameters in their descriptions
- Explain the impact of omitting optional parameters

## Advanced Schema Patterns

### Complex Nested Structures

Anthropic supports complex schemas including: [github](https://github.com/aws-samples/anthropic-on-aws/blob/main/complex-schema-tool-use/README.md)
- **Nested objects**: Multi-level data structures
- **Arrays**: Lists of items with specified types
- **Enums**: Constrained value sets
- **Unions**: Multiple valid types for a field

Example of nested structure: [github](https://github.com/aws-samples/anthropic-on-aws/blob/main/complex-schema-tool-use/README.md)

```json
{
  "order_items": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "product_id": {
          "type": "string",
          "description": "Unique product identifier"
        },
        "quantity": {
          "type": "integer",
          "description": "Number of units ordered"
        }
      },
      "required": ["product_id", "quantity"]
    }
  }
}
```

### Structured Outputs with `strict: true`

For guaranteed schema compliance, Anthropic introduced **strict tool mode**: [techbytes](https://techbytes.app/posts/claude-structured-outputs-json-schema-api/)
- Set `"strict": true` as a top-level property in tool definitions
- Enables **constrained decoding** to guarantee valid outputs
- Eliminates `JSON.parse()` errors and schema violations
- Works with Pydantic (Python) and Zod (TypeScript) for native validation [techbytes](https://techbytes.app/posts/claude-structured-outputs-json-schema-api/)

### Guidance on Tool Name Conflicts

The MCP documentation recommends strategies when multiple servers expose tools with the same name: [github](https://github.com/apappascs/mcp-servers-hub)
- Use **namespacing**: Prefix tool names with server/domain identifiers
- Provide **disambiguation context** in descriptions
- Let users configure which server's tool to prefer

## Tool Configuration in System Prompts

Anthropic's published tool system prompt shows how tools are loaded: [arcfu](https://arcfu.com/post/claude-json-solution/)

```
In this environment you have access to a set of tools you can use 
to answer the user's question.

{{ FORMATTING INSTRUCTIONS }}

String and scalar parameters should be specified as is, while lists 
and objects should use JSON format. Note that spaces for string 
values are not stripped. The output is not expected to be valid XML 
and is parsed with regular expressions.

Here are the functions available in JSONSchema format:

{{ TOOL DEFINITIONS IN JSON SCHEMA }}
```

This reveals that:
- Tools are presented to Claude in JSON Schema format
- String/scalar parameters use plain values, not JSON encoding
- Tool outputs are parsed with regular expressions, not strict XML parsers [arcfu](https://arcfu.com/post/claude-json-solution/)

## Evaluation-Driven Iteration

Anthropic strongly recommends **evaluation-driven tool development**: [github](https://github.com/modelcontextprotocol/servers)
- Build eval sets that test tool calling across representative scenarios
- Iterate on descriptions based on failure modes
- Use automated evaluations to catch regressions when updating tools
- Track metrics like tool selection accuracy and parameter correctness

## Tool Search Pattern (Advanced)

For systems with large tool libraries (1000+ tools), Anthropic recommends the **Tool Search Tool pattern**: [anthropic](https://www.anthropic.com/engineering/advanced-tool-use)
- Instead of loading all tools upfront, implement a meta-tool that discovers tools on-demand
- Claude only sees tools it actually needs for a given query
- Reduces context window usage and improves selection accuracy
- Described in "Introducing advanced tool use on the Claude Developer Platform" [github](https://github.com/modelcontextprotocol)

## Summary Table

| Aspect | Recommendation | Priority |
|--------|---------------|----------|
| Description length | 3-4+ sentences minimum | Critical [anthropic.mintlify](https://anthropic.mintlify.app/en/docs/agents-and-tools/tool-use/implement-tool-use) |
| Description content | What, when, parameters, caveats, limitations | Critical [anthropic.mintlify](https://anthropic.mintlify.app/en/docs/agents-and-tools/tool-use/implement-tool-use) |
| Parameter naming | Unambiguous, specific names | High [github](https://github.com/modelcontextprotocol/servers) |
| Property descriptions | Every parameter needs detailed description | High [github](https://github.com/aws-samples/anthropic-on-aws/blob/main/complex-schema-tool-use/README.md) |
| Examples vs descriptions | Prioritize descriptions, add examples second | Medium [anthropic.mintlify](https://anthropic.mintlify.app/en/docs/agents-and-tools/tool-use/implement-tool-use) |
| Schema format | Standard JSON Schema with nested support | Required [platform.claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use) |
| Strict mode | Use `strict: true` for guaranteed compliance | High for production [platform.claude](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) |
| Token efficiency | Document limits, pagination, truncation | Medium [github](https://github.com/modelcontextprotocol/servers) |
| Evaluation | Build eval sets, iterate on failures | High [github](https://github.com/modelcontextprotocol/servers) |

The overarching principle is to treat tool descriptions as **first-class prompt engineering**—they're loaded into Claude's context and directly influence tool selection and invocation accuracy. [anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)

What-do-Anthropic-blog-posts-recommend-for-tool-descriptions-and-schemas