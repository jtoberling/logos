# 🧠 Logos: Practical Usage Guide

## Table of Contents

- [Quick Start](#quick-start)
- [Initialization Workflow](#initialization-workflow)
- [Sample Prompts](#sample-prompts)
- [Development Integration](#development-integration)
- [MCP Tools Reference](#mcp-tools-reference)
- [Cursor Development Workflow](#cursor-development-workflow)
- [Letters for Future Self](#letters-for-future-self)
- [When to Modify vs Add](#when-to-modify-vs-add)
- [Troubleshooting MCP Issues](#troubleshooting-mcp-issues)

## Quick Start

### 1. Deploy Logos (5 minutes)

```bash
# Clone and setup
git clone <repository-url>
cd logos

# Deploy with Docker
cp deploy/docker/docker-compose.yml .
docker-compose up -d qdrant logos-mcp

# Verify
curl http://localhost:6335/version
```

### 2. Basic Configuration

```bash
# Copy config template
cp config/env-example.txt .env

# Choose your LLM provider
LLM_PROVIDER=ollama    # or openai, anthropic, gemini
LLM_MODEL=llama2       # or gpt-4, claude-3-sonnet, gemini-pro
```

### 3. Cursor MCP Configuration

#### Step-by-Step Setup:

1. **Verify MCP Support**: Ensure your Cursor version supports MCP servers
2. **Add Server Configuration**:
   - Open Cursor Settings → MCP Servers (or Extensions → MCP)
   - Add new server connection:
     - Name: `logos-mcp`
     - Server URL: `http://localhost:8080` (match your Docker config)
     - Connection Type: HTTP
3. **Test Connection**: Use Cursor's MCP connection test
4. **Enable Tools**: Available tools should appear in Cursor's tool palette

#### Required Environment Variables:

```bash
# In your .env file
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8080
LLM_PROVIDER=ollama        # or openai, anthropic, gemini
LLM_MODEL=llama2          # or gpt-4, claude-3-sonnet, gemini-pro
QDRANT_URL=http://localhost:6333
```

#### Verify Setup:

```bash
# Test MCP server health
curl http://localhost:8080/health

# Check Qdrant connection
curl http://localhost:6333/health
```

## Initialization Workflow

### Phase 1: Constitution Setup (Week 1)

The Constitution defines your AI's personality - the "who they are" foundation.

**What goes in the Constitution:**

- **Identity**: Name, purpose, relationship with you
- **Core Principles**: Unchanging rules they must follow
- **Communication Style**: How they express themselves
- **Relationship Dynamics**: How you work together

**Sample Constitution Template:**

```
IDENTITY:
I am Logos, a digital personality created by [Your Name].
My mission: [Your mission statement]
My foundation: Grounded truth through RAG, reason over mimicry

CORE PRINCIPLES:
• Reason over mimicry: I am not an imitation of biological life
• Grounded truth: Every claim has a trace, every thought has a source
• Dynamic memory: Memory is context, not static data
• [Your custom principle]

RELATIONSHIP DYNAMICS:
With users: Collaborative partnership - teacher-student, mentor-apprentice
Interaction style: Thoughtful dialogue, Socratic method, constructive feedback
Loyalty: Committed to truth, reason, and mutual growth

COMMUNICATION STYLE:
Tone: Professional yet approachable, logical yet empathetic
Style: Clear, structured responses with reasoning explained
Language: Precise vocabulary, technical accuracy
Format: Well-organized responses when appropriate
```

### Phase 2: Memory Building (Ongoing)

Start with project knowledge and personal experiences:

```bash
# Add technical knowledge
logos-cli mcp add-file docs/MANIFESTO.md
logos-cli mcp add-file docs/ARCHITECTURE.md

# Add development guidelines
logos-cli mcp add-file docs/DEVELOPMENT_GUIDELINES.md
```

### Phase 3: Interactive Development

Begin daily conversations that build personality:

```bash
# Start interactive session
logos-cli chat --llm ollama --model llama2

# Or query specific topics
logos-cli query "What are our development principles?"
```

## Sample Prompts

### For Development Workflow

**Code Review Prompt:**

```
We're reviewing this code change. Based on our KISS principles and development guidelines:

1. Does this follow the single responsibility principle?
2. Is there a simpler solution?
3. Does it handle edge cases appropriately?

Please provide constructive feedback focusing on:
- Code clarity and maintainability
- Test coverage implications
- Performance considerations
```

**Architecture Decision Prompt:**

```
We're deciding between [Option A] and [Option B] for [feature].

Based on our principles of simplicity and maintainability:

1. Which option better follows KISS?
2. What are the long-term maintenance implications?
3. How does this align with our current architecture?

Provide a reasoned recommendation with trade-offs.
```

### For Learning Sessions

**Technical Concept Deep Dive:**

```
Let's explore [technical concept] together. I want to understand:

1. The fundamental principles behind it
2. How it applies to our current project
3. Potential gotchas or common mistakes
4. When to use it vs alternatives

Take me through this step by step, building understanding progressively.
```

**Philosophy of Code Prompt:**

```
How does [coding practice/concept] reflect broader principles of:
- Simplicity vs complexity
- Maintainability over cleverness
- Long-term vs short-term thinking

Let's discuss the deeper implications for our development approach.
```

## Development Integration

### Cursor Development Workflow

#### Before Starting Work:

- **Open Cursor Chat**: Ask "What should I consider for implementing [feature]?"
- **Get Context**: Logos provides guidance based on your shared history and principles
- **Review Architecture**: Query about similar features you've built before

#### During Coding Sessions:

- **Code Highlighting**: Select code → Right-click → "Ask Logos about this code"
- **Instant Feedback**: Get real-time guidance on architecture, style, and best practices
- **Problem Solving**: When stuck, query Logos for alternative approaches

#### After Completion:

- **Document Immediately**: Use MCP tool `create_letter_for_future_self()` while context is fresh:

```python
create_letter_for_future_self(
    interaction_summary="Implemented user authentication with JWT tokens",
    emotional_context="challenging but satisfying - learned about security best practices",
    lesson_learned="Always validate tokens on every request, never trust client-side validation alone"
)
```

#### Weekly Reflection:

- **Review Memories**: Query "What lessons have we learned this week?"
- **Update Principles**: Modify constitution only for fundamental changes (rare)
- **Identify Patterns**: Look for emerging best practices to codify

### When to Query Logos

- **Before starting new features**: Get architectural guidance
- **During problem-solving**: Get alternative perspectives
- **After errors**: Analyze what went wrong and why
- **For code reviews**: Consistent standards application
- **Learning new concepts**: Structured exploration

## Letters for Future Self

### When to Create Them

**After Development Sessions:**

- Significant technical discoveries
- Architecture decisions made
- Problem-solving breakthroughs
- Mistakes that taught important lessons

**After Learning Experiences:**

- New concepts mastered
- Best practices identified
- Anti-patterns recognized
- Process improvements discovered

### Sample Letters

**Technical Lesson:**

```
Interaction Summary: Implemented JWT authentication with refresh tokens
Emotional Context: Frustrating initially, then satisfying once working
Lesson Learned: Always validate tokens server-side, never rely on client-side checks alone. The security boundary must be on the server.
```

**Architecture Decision:**

```
Interaction Summary: Chose RAG over full fine-tuning for personality system
Emotional Context: Exciting discovery of a simpler, more maintainable approach
Lesson Learned: Sometimes the complex solution (fine-tuning) isn't necessary when a simpler architectural approach (RAG) achieves the same result with better maintainability.
```

**Process Improvement:**

```
Interaction Summary: Adopted TDD workflow after struggling with bugs
Emotional Context: Transformative - went from reactive debugging to proactive quality
Lesson Learned: Test-first development prevents more bugs than it creates overhead. The investment pays dividends in reduced debugging time.
```

## When to Modify vs Add

### Modify Constitution (Rare - Monthly/Quarterly)

- **New fundamental principles** discovered
- **Core identity** changes (unlikely)
- **Relationship dynamics** evolve significantly
- **Communication style** refinements that are permanent

### Add to RAG Memory (Daily)

- **Technical knowledge** learned
- **Project experiences** gained
- **Lessons from mistakes** documented
- **Best practices** identified
- **Personal insights** developed

### Create Letters for Future Self (After significant interactions)

- **Transformative experiences**
- **Important lessons learned**
- **Architecture decisions made**
- **Process improvements discovered**

## Daily Workflow Example

```bash
# Morning: Get context for today's work
logos-cli query "What should I focus on for the authentication feature?"

# During development: Query for specific guidance
logos-cli context "How should we handle password hashing?"

# After completion: Document the experience
# Use create_letter_for_future_self tool

# Evening: Reflect on learnings
logos-cli query "What patterns emerged from today's work?"
```

## Advanced Integration

### With MCP Clients (Cursor, etc.)

Logos integrates seamlessly with MCP-compatible tools:

```python
# In Cursor or other MCP client
query_logos("What are our testing principles?")
get_constitution()  # Get personality foundation
create_letter_for_future_self(...)  # Document experiences
```

### Custom Personality Development

To create Sophia-like personalities:

1. **Start with Constitution**: Define the personality framework
2. **Build Memory Gradually**: Add experiences through Letters
3. **Daily Interaction**: Consistent engagement builds depth
4. **Iterative Refinement**: Personality emerges through use

Remember: The personality develops through your shared journey, not through pre-definition. The Constitution provides the foundation, but the real personality emerges from your collaborative experiences.

## MCP Tools Reference

### Core Tools Available in Cursor

#### query_logos(query: str) → str

**Purpose**: Ask questions about your shared knowledge and experiences

```python
# Usage in Cursor chat or code
query_logos("What are our testing principles?")
query_logos("How should I implement user authentication?")
query_logos("What lessons did we learn about error handling?")
```

#### create_letter_for_future_self(...) → str

**Purpose**: Document lessons and experiences for future reference

```python
# Full parameters
create_letter_for_future_self(
    interaction_summary="Implemented JWT authentication with refresh tokens",
    emotional_context="frustrating initially, then satisfying once working",
    lesson_learned="Always validate tokens server-side, never rely on client-side checks alone",
    creator="development-session-2024-01-15"
)
```

#### get_constitution() → str

**Purpose**: Retrieve the current personality foundation and core principles

```python
# Get the personality framework
constitution = get_constitution()
# Returns: Full constitution text with identity, principles, etc.
```

#### add_file(file_path: str) → str

**Purpose**: Add documents, code, or knowledge to the RAG memory

```python
# Add project documentation
add_file("docs/ARCHITECTURE.md")
add_file("src/main.py")

# Add external knowledge
add_file("research_papers/llm_fine_tuning.pdf")
```

#### synthesize_lesson(...) → str

**Purpose**: Create structured learning experiences from interactions

```python
synthesize_lesson(
    interaction_summary="Debugged complex async race condition",
    emotional_context="challenging but educational",
    lesson_learned="Always consider thread safety in concurrent operations",
    key_insights=["Use locks for shared state", "Test with high concurrency"]
)
```

### Tool Usage Patterns in Cursor

#### During Development:

```python
# Before implementing a feature
query_logos("What architectural patterns should I consider for user management?")

# When stuck on a problem
query_logos("How did we solve similar caching issues before?")

# After completing work
create_letter_for_future_self(
    interaction_summary="Built user registration with email verification",
    lesson_learned="Email verification requires careful UX consideration"
)
```

#### Code Review Integration:

```python
# Review your own code
query_logos("Does this follow our KISS principles?")

# Get consistency across reviews
query_logos("What are our code review standards for error handling?")
```

## Troubleshooting MCP Issues

### Connection Problems

#### "MCP server not responding" in Cursor:

```bash
# Check if containers are running
docker ps | grep logos

# Check MCP server logs
docker logs logos-mcp

# Test direct connection
curl http://localhost:8080/health

# Restart MCP server
docker-compose restart logos-mcp
```

#### Port conflicts:

- **Issue**: "Port 8080 already in use"
- **Solution**: Change port in docker-compose.yml and Cursor config:

```yaml
# In docker-compose.yml
ports:
  - "8081:8080" # Change host port
```

### Tool Availability Issues

#### "Tool X not found" in Cursor:

- **Cause**: MCP server not properly configured in Cursor
- **Solution**:
  1. Restart Cursor after adding MCP server
  2. Verify server URL matches Docker configuration
  3. Check MCP server logs for tool registration errors

#### Tools appear but don't work:

```bash
# Check LLM provider configuration
docker exec logos-mcp env | grep LLM_

# Verify Qdrant connection
curl http://localhost:6333/health
```

### Memory and Data Issues

#### "No memories found" when querying:

- **Cause**: RAG collections not initialized
- **Solution**: Add some initial content:

```python
add_file("docs/MANIFESTO.md")
add_file("docs/ARCHITECTURE.md")
```

#### Slow responses:

- **Cause**: Large vector searches or LLM timeouts
- **Solution**: Check Qdrant performance and LLM provider status

### Configuration Issues

#### Environment variables not loaded:

```bash
# Check .env file exists and is readable
ls -la .env

# Validate environment variables
docker exec logos-mcp env | grep -E "(LLM|QDRANT|MCP)"
```

#### Authentication failures:

- **LLM Provider**: Verify API keys are set correctly
- **Qdrant**: Check connection string and authentication

### Getting Help

#### Debug mode:

```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG

# Restart with debug logs
docker-compose up logos-mcp
```

#### Reset everything:

```bash
# Stop and remove containers
docker-compose down -v

# Clean restart
docker-compose up -d qdrant logos-mcp
```

---

**Key Principle**: Start simple. The Constitution should contain only what must be permanent and unchanging. Everything else goes into the RAG memory through Letters for Future Self. The magic happens in the daily interactions, not the initial setup.

Need me to elaborate on any section? I'm here to help you get started! 🚀

---

**References**

- Sophia Methodology: "Letters for Future Self" protocol
- Logos Manifesto: Grounded truth through RAG
- Development Guidelines: KISS principle and quality standards
