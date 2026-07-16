# Milestone 04 – AWS WAF Protection

## Objective

Protect the public REST API before requests reach API Gateway by implementing AWS WAF.

---

## Architecture Before

Internet User
↓
Amazon Cognito
↓
API Gateway REST API
↓
AWS Lambda
↓
Amazon Bedrock
↓
Amazon Nova Lite

---

## Architecture After

Internet User
↓
AWS WAF
├── AWS Managed Core Rule Set
└── RateLimit100Requests
↓
Amazon Cognito
↓
API Gateway REST API
↓
AWS Lambda
↓
Amazon Bedrock
↓
Amazon Nova Lite

---

## AWS Services Used

### AWS WAF

Purpose:
Protect the REST API from common web exploits and abusive traffic before requests reach API Gateway.

Configuration:

- AWS Managed Core Rule Set
- RateLimit100Requests
- Rate limit: 100 requests
- Evaluation window: 5 minutes
- Action: Block
- Request aggregation: Source IP

---

## Security Benefits

- Protects against OWASP Top 10 attacks
- Blocks abusive request rates
- Reduces attack surface
- Adds defense in depth

---

## Scalability

AWS WAF is fully managed and automatically scales with application traffic.

---

## Cost Optimization

Requests blocked by AWS WAF never reach:

- API Gateway
- Lambda
- Amazon Bedrock

This reduces unnecessary compute and AI inference costs.

---

## Validation

- Web ACL created successfully
- Associated with API Gateway REST API
- AWS Managed Core Rule Set enabled
- RateLimit100Requests enabled
- Cognito authentication verified
- Managed Login completed successfully

---

## Interview Talking Points

### Purpose

Protect the public API before requests reach backend services.

### Why AWS WAF

Provides managed protection against common web attacks while allowing custom rules such as rate limiting.

### Security

Implements defense in depth by placing WAF before Cognito and API Gateway.

### Scalability

AWS manages scaling automatically.

### Cost

Blocks malicious traffic before it generates API Gateway, Lambda, or Bedrock charges.

### Business Value

Improves application security, reliability, and operational cost efficiency.
