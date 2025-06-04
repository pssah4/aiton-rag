# Custom GPT Configuration for AITON-RAG

This directory contains configuration files and instructions for setting up ChatGPT Custom GPT Actions to integrate with the AITON-RAG API.

## Files Overview

- `actions_schema.json` - OpenAPI schema for Custom GPT Actions
- `custom_gpt_instructions.md` - Instructions for configuring the Custom GPT
- `system_prompts.md` - Recommended system prompts for the Custom GPT
- `example_conversations.md` - Example conversations showing how to use the integration

## Quick Setup

1. **Create a Custom GPT** in ChatGPT
2. **Import the Actions Schema** from `actions_schema.json`
3. **Configure the System Prompt** using content from `system_prompts.md`
4. **Test the Integration** using examples from `example_conversations.md`

## API Endpoints Available

- `/api/v1/search` - Search the knowledge base
- `/api/v1/knowledge-base` - Get complete knowledge base
- `/api/v1/categories` - List available categories
- `/api/v1/health` - System health check

## Authentication

Currently, the API does not require authentication. For production deployments, consider implementing API key authentication.

## Base URL Configuration

Replace `http://localhost:5000` with your actual deployment URL in the actions schema.
