# Milestone 09 – DynamoDB Conversation History

## Objective

The objective of this milestone is to add persistent conversation storage to the AWS AI Knowledge Assistant.

Prior to this milestone, Amazon Bedrock generated responses but conversation data was not retained after the request completed.

By integrating Amazon DynamoDB, the application can now store prompts and responses for future retrieval, analytics, auditing, and personalization.

---

## Architecture Before

Internet User
        │
Amazon Cognito
        │
API Gateway
        │
AWS Lambda
        │
Amazon Bedrock
        │
Amazon Nova Lite

---

## Architecture After

Internet User
        │
Route 53 (planned)
        │
CloudFront (planned)
        │
AWS WAF
        │
Amazon Cognito
        │
API Gateway
        │
AWS Lambda
   ┌────┴───────────────┐
   │                    │
Amazon Bedrock     Amazon DynamoDB
   │                    │
Nova Lite      AIConversationHistory

---

## Services Implemented

### Amazon DynamoDB

Table Name:

AIConversationHistory

Primary Key Design:

Partition Key:
- UserId (String)

Sort Key:
- Timestamp (String)

Billing Mode:
- On-Demand

Region:
- us-east-2

---

## Why DynamoDB Was Chosen

Amazon DynamoDB is a fully managed NoSQL database designed for low-latency, high-scale workloads.

Benefits include:

- Serverless architecture
- Automatic scaling
- No infrastructure management
- High availability
- Millisecond response times
- Pay-for-use pricing model

DynamoDB aligns well with serverless architectures built using API Gateway and Lambda.

---

## Security Design

### IAM Least Privilege

A dedicated IAM policy was created:

AWSAIAssistantDynamoDBConversationHistory

Allowed Actions:

- dynamodb:PutItem
- dynamodb:GetItem
- dynamodb:Query

The policy was scoped to:

arn:aws:dynamodb:us-east-2:683210040136:table/AIConversationHistory

This prevents Lambda from accessing unrelated DynamoDB resources.

### Existing Security Layers

- Amazon Cognito authentication
- AWS WAF protection
- API Gateway authorization
- IAM execution role permissions
- CloudWatch logging

---

## Lambda Integration

The Lambda function was updated to:

1. Receive requests
2. Invoke Amazon Bedrock Nova Lite
3. Capture the generated response
4. Store conversation data in DynamoDB
5. Return the AI response to the user

Stored attributes include:

- UserId
- Timestamp
- Prompt
- Response
- ModelId
- RequestId

Example Item:

{
  "UserId": "test-user",
  "Timestamp": "2026-07-18T03:34:14.535950+00:00",
  "Prompt": "Tell me one fact about AWS.",
  "Response": "One interesting fact about AWS...",
  "ModelId": "amazon.nova-lite-v1:0",
  "RequestId": "86a3bfa3-8a71-412b-a5f6-36a623868351"
}

---

## Scalability Considerations

DynamoDB was configured using On-Demand capacity mode.

Benefits:

- Automatic scaling
- No capacity planning
- Suitable for unpredictable traffic
- Cost-effective during development

Future enhancements could include:

- Global Tables
- DynamoDB Streams
- Time-to-Live (TTL)
- Secondary Indexes

---

## Cost Considerations

Current Cost Drivers:

- Storage consumed
- Read requests
- Write requests

Using On-Demand mode avoids paying for unused capacity.

This is appropriate for development and low-volume workloads.

---

## Business Value

Conversation history creates the foundation for:

- User conversation persistence
- Customer support history
- AI auditing
- Usage analytics
- Personalization
- Future retrieval-augmented workflows

Without persistence, AI interactions are lost after the request completes.

DynamoDB transforms the application from a stateless AI endpoint into a stateful AI platform.

---

## Validation Performed

### DynamoDB Table Validation

Successfully created:

AIConversationHistory

Configuration:

- UserId (Partition Key)
- Timestamp (Sort Key)

### IAM Validation

Created policy:

AWSAIAssistantDynamoDBConversationHistory

Verified Lambda execution role permissions.

### Lambda Validation

Executed Lambda test event.

Result:

Status: Succeeded

Response:

{
  "conversationSaved": true
}

### DynamoDB Validation

Verified successful record creation in:

AIConversationHistory

Stored fields:

- UserId
- Timestamp
- Prompt
- Response
- ModelId
- RequestId

End-to-end persistence was successfully validated.

---

## Interview Talking Points

### Why DynamoDB?

DynamoDB provides a serverless, highly scalable NoSQL database that integrates naturally with Lambda and API Gateway.

### Why UserId and Timestamp?

UserId groups conversations by user.

Timestamp enables chronological ordering and efficient retrieval of conversation history.

### Why On-Demand Capacity?

On-Demand capacity removes the need for capacity planning and automatically scales with workload demand.

### How was security implemented?

IAM least-privilege permissions were applied, restricting Lambda to only the required DynamoDB actions against a single table.

### How was the solution validated?

A Lambda test successfully invoked Bedrock, stored conversation data in DynamoDB, and returned a successful response. The stored record was verified through the DynamoDB console.

---

## Milestone Outcome

Milestone 09 successfully introduced persistent conversation storage using Amazon DynamoDB.

The AWS AI Knowledge Assistant can now:

- Generate AI responses using Amazon Bedrock
- Persist conversation history
- Retrieve user-specific records
- Support future analytics and personalization capabilities

This milestone establishes the application's persistent data layer and completes the core AI request lifecycle.
