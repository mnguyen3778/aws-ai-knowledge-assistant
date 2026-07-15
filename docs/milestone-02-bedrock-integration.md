# Milestone 02 - Amazon Bedrock Integration

## Objective

Integrate Amazon Bedrock with AWS Lambda to transform the application from a static API response into an AI-powered assistant.

---

## Architecture

User
↓
API Gateway
↓
AWS Lambda
↓
Amazon Bedrock
↓
Amazon Nova Lite
↓
AI Response

---

## Services Used

### AWS Lambda

#### Purpose
Runs application logic without managing servers.

#### Why Chosen
- Serverless
- Automatic scaling
- Pay only for execution time
- Native integration with Bedrock

#### Security
Uses IAM execution role instead of embedded credentials.

#### Scalability
Automatically scales based on requests.

#### Cost
Pay-per-request.

#### Business Value
Reduces operational overhead and infrastructure management.

---

### Amazon Bedrock

#### Purpose
Provides managed access to foundation models.

#### Why Chosen
- No GPU management
- Managed AI service
- Supports multiple foundation models
- Easy model replacement

#### Security
Integrated with IAM permissions.

#### Scalability
Fully managed by AWS.

#### Cost
Pay only for model invocations.

#### Business Value
Accelerates AI application development without managing model infrastructure.

---

### Amazon Nova Lite

#### Purpose
Foundation model used by the AI assistant.

#### Why Chosen
- Cost efficient
- Fast inference
- Suitable for question answering and conversational AI
- AWS-native model

#### Tradeoff
Nova Premier provides stronger reasoning but at higher cost.

---

## IAM Configuration

Created custom policy:

AWSAIAssistantInvokeNovaLite

Permission:

- bedrock:InvokeModel

Resource:

arn:aws:bedrock:us-east-2::foundation-model/amazon.nova-lite-v1:0

Attached to Lambda execution role:

aws-ai-assistant-role-4x5upr0p

---

## Lambda Implementation

Previous Response

```python
return {
    "statusCode": 200,
    "body": "AWS AI Assistant Online"
}
