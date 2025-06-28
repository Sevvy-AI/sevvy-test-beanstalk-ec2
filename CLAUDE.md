# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is a simple Python Flask server designed for testing AWS Beanstalk, EC2, and CloudWatch monitoring integrations. The server provides controllable error endpoints to test monitoring system integrations with AWS services.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run server locally for development
python application.py

# Deploy to AWS Beanstalk
eb init
eb create sevvy-test-env
eb deploy
```

## Architecture Overview

**Single-File Flask Application**: The entire server logic is contained in `application.py` following AWS Beanstalk naming conventions.

**Error Simulation Architecture**: The server implements a pattern of deliberate error generation for testing purposes:
- Structured error endpoints under `/error/*` routes
- Consistent error response format with timestamps and error types
- Comprehensive logging for each error type with stack traces

**AWS Integration Design**:
- Uses the `application` variable name required by Beanstalk
- CloudWatch logging configured via `.ebextensions/logging.config`
- Request/response middleware logging for monitoring integration testing
- Structured JSON responses for easy parsing by monitoring tools

**Logging Strategy**: All endpoints log both incoming requests and error details with specific prefixes (e.g., `NULL_POINTER_ERROR:`, `DIVISION_BY_ZERO_ERROR:`) to facilitate log parsing and alerting in monitoring systems.

## Key Implementation Patterns

**Error Endpoint Pattern**: Each error endpoint follows the same structure:
1. Log the attempt
2. Trigger the specific error condition
3. Catch and log the error with detailed context
4. Return structured JSON with error type, message, and timestamp

**Health Check Design**: Implements both `/health` (basic) and `/status` (detailed) endpoints for different monitoring needs.

**Custom Error Configuration**: The `/error/custom/<error_type>` endpoint uses a dictionary-based configuration system for different HTTP error codes and messages.