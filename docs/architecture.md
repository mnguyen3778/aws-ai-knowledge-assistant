# AWS AI Knowledge Assistant

## Objective

Build a secure, scalable, and cost-conscious AI knowledge assistant using AWS managed services.

## Business Problem

Organizations need a simple way for authenticated users to ask questions against approved knowledge while maintaining security, observability, scalability, and predictable operating costs.

## Proposed Architecture

User
 |
CloudFront
 |
AWS WAF
 |
Amazon Cognito
 |
Amazon API Gateway
 |
AWS Lambda
 |
Amazon Bedrock
 |
Amazon DynamoDB

## Service Decisions

### Amazon CloudFront

Delivers the application through AWS edge locations to improve performance for users in different geographic regions.

### AWS WAF

Protects the application from common web attacks and provides traffic visibility through logging and rule metrics.

### Amazon Cognito

Provides managed user authentication and identity services without requiring a custom authentication system.

### Amazon API Gateway

Provides a managed HTTPS API layer between the application and backend services.

### AWS Lambda

Runs backend logic without provisioning or maintaining servers. It scales automatically and charges primarily for actual usage.

### Amazon Bedrock

Provides managed access to foundation models with AWS security controls, model choice, pay-as-you-go pricing, and support for guardrails.

### Amazon DynamoDB

Stores user sessions, conversation metadata, and chat history using a serverless database that scales automatically.

## Architecture Priorities

- Security
- Scalability
- Resilience
- Cost efficiency
- Operational visibility
- Simplicity
