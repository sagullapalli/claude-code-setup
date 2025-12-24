# Claude Interface

Custom UI and orchestration layer built on Claude Code SDK for managing multi-agent AI applications.

## Overview

This project provides a robust Claude Code setup designed to build fullstack applications using AI-powered multi-agent orchestration. It serves as the foundation for creating custom interfaces on top of the Claude Code SDK.

## Goals

- **Multi-Agent Orchestration**: Coordinate multiple specialized AI agents for complex tasks
- **Custom UI Layer**: Build intuitive interfaces for interacting with Claude-powered agents
- **Fullstack Development**: End-to-end application development with AI assistance
- **Reusable Patterns**: Establish best practices for Claude Code SDK integration

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, PostgreSQL
- **AI/Agents**: Claude Code SDK, Google ADK, Vertex AI
- **Frontend**: React + TypeScript (Vite, Tailwind CSS, TanStack Query)
- **Cloud**: Google Cloud Platform (Cloud Run, Cloud SQL)
- **Infrastructure**: Terraform, GitHub Actions

## Project Structure

```
.claude/
├── agents/          # Agent-specific instructions
├── memory/          # Persistent agent memory
└── skills/          # Technical patterns and best practices
docs/                # Implementation guides and ADRs
```

## Getting Started

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-interface.git
cd claude-interface

# Install dependencies
npm install

# Start development
npm run dev
```

## License

MIT
