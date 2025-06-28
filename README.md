# Sevvy Test Server

A simple Python Flask server designed for testing AWS Beanstalk, EC2, and CloudWatch monitoring integrations.

## Overview

This server provides controllable error endpoints to test monitoring system integrations with AWS services. It's designed to run on AWS Elastic Beanstalk and integrate with CloudWatch for log aggregation.

## API Endpoints

### Health & Status
- `GET /health` - Health check endpoint for load balancers
- `GET /status` - Detailed service status and available endpoints

### Error Testing Endpoints
- `POST /error/null-pointer` - Triggers AttributeError (null pointer simulation)
- `POST /error/server-error` - Generic 500 internal server error
- `POST /error/division-zero` - Division by zero error with detailed logging
- `POST /error/custom/<error_type>` - Configurable error types (timeout, forbidden, not_found, bad_request, unauthorized)

## Usage Examples

```bash
# Health check
curl -X GET http://your-beanstalk-url/health

# Trigger division by zero error
curl -X POST http://your-beanstalk-url/error/division-zero \
  -H "Content-Type: application/json" \
  -d '{"numerator": 42}'

# Trigger custom timeout error
curl -X POST http://your-beanstalk-url/error/custom/timeout
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python application.py
```

The server will run on `http://localhost:5000`

## AWS Beanstalk Deployment

1. Install AWS CLI and EB CLI
2. Configure AWS credentials
3. Deploy to Beanstalk:

```bash
eb init
eb create sevvy-test-env
eb deploy
```

## CloudWatch Integration

The server is configured to stream logs to CloudWatch with:
- 7-day retention period
- Health streaming enabled
- Structured logging format for easy parsing

## Features

- **Structured Logging**: All requests/responses and errors are logged with timestamps
- **Error Simulation**: Multiple error types for comprehensive monitoring testing
- **Health Monitoring**: Standard health check endpoints
- **AWS Ready**: Configured for Beanstalk deployment with CloudWatch integration