# Milestone 03 - Amazon Cognito Authentication

## Objective

Add user authentication and identity management to the AWS AI Knowledge Assistant.

## Architecture Before

Internet User
↓
API Gateway
↓
Lambda
↓
Amazon Bedrock
↓
Nova Lite

## Architecture After

Internet User
↓
Amazon Cognito
↓
API Gateway
↓
Lambda
↓
Amazon Bedrock
↓
Nova Lite

## Services Used

### Amazon Cognito

Purpose:
Provide authentication and identity management.

Why Chosen:
Managed authentication service with JWT support.

Security:
- User Pool
- Email authentication
- JWT token issuance
- Public sign-up disabled

Scalability:
Managed AWS service that automatically scales.

Cost:
Low-cost managed service with free tier support.

Business Value:
Protects AI endpoints from unauthorized access.

## Implementation

- Created Cognito User Pool
- Created App Client
- Created test user
- Enabled managed login
- Configured email sign-in

## Evidence

User Pool ID:
us-east-2_3cfsmE8Xt

App Client:
AWS AI Knowledge Assistant

Region:
us-east-2

## Interview Talking Points

What is a User Pool?
What is an App Client?
Why Cognito instead of custom authentication?
How does JWT authentication work?
