# Milestone 10 – Cloudflare + CloudFront Production Delivery

## Objective

Implement production-grade edge delivery for the AWS AI Knowledge Assistant using Cloudflare and Amazon CloudFront.

## Services Implemented

- Cloudflare DNS
- Amazon CloudFront
- AWS Certificate Manager (ACM)
- API Gateway Origin
- Amazon Cognito
- AWS WAF

## Architecture Before

Internet User
      │
AWS WAF
      │
Amazon Cognito
      │
API Gateway
      │
AWS Lambda
      │
Amazon Bedrock

## Architecture After

Internet User
      │
Cloudflare
DNS + DDoS Protection
      │
CloudFront
HTTPS + CDN + Compression
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
Amazon Bedrock     DynamoDB
 │
Nova Lite

CloudWatch Metrics
      │
CloudWatch Alarms
      │
Amazon SNS
      │
Email Notifications

Security Analytics
 ├── Amazon S3
 ├── AWS Glue
 ├── Glue Data Catalog
 └── Amazon Athena

## Cloudflare Configuration

- Cloudflare remains authoritative DNS provider.
- Route 53 was intentionally not used.
- Created DNS record:
  - assistant.nguyen-ai.com
- Traffic routed to CloudFront distribution.

## CloudFront Configuration

Distribution Name:
- assistant-nguyen-ai

Origin:
- API Gateway REST API

Custom Domain:
- assistant.nguyen-ai.com

Viewer Protocol Policy:
- Redirect HTTP to HTTPS

Allowed Methods:
- GET
- HEAD
- OPTIONS
- PUT
- POST
- PATCH
- DELETE

Cache Policy:
- Managed-CachingDisabled

Origin Request Policy:
- Managed-AllViewerExceptHostHeader

Compression:
- Enabled

## Security Validation

Test URLs:

- https://assistant.nguyen-ai.com
- https://assistant.nguyen-ai.com/chat

Results:

- HTTPS certificate validated successfully.
- CloudFront served requests successfully.
- API Gateway returned expected protected responses.
- Cognito authorization enforced.

Observed Response:

```json
{"message":"Forbidden"}
```

This confirms unauthorized requests are blocked.

## Monitoring Validation

CloudFront Metrics Verified:

- Requests > 0
- Data Transfer > 0
- 4XX Responses observed

This confirms traffic traversed:

Internet User
→ Cloudflare
→ CloudFront
→ API Gateway

## Architecture Rationale

### Purpose

Provide global content delivery, HTTPS enforcement, caching controls, and edge security.

### Security

- TLS termination through CloudFront
- Cognito authorization
- AWS WAF protection
- Cloudflare DDoS protection

### Scalability

CloudFront edge locations reduce latency and improve global performance.

### Cost

CloudFront reduces direct API origin traffic and provides pay-as-you-go scaling.

### Business Value

Creates a production-grade public endpoint suitable for customer-facing AI applications.

## Interview Talking Points

- Cloudflare used as authoritative DNS provider.
- CloudFront deployed as CDN and HTTPS edge layer.
- API Gateway configured as CloudFront origin.
- Cognito authorization verified through protected endpoint testing.
- CloudFront metrics validated successful traffic flow.
- Production architecture follows layered security principles.

## Completion Evidence

- CloudFront distribution deployed
- Custom domain configured
- HTTPS operational
- CloudFront metrics validated
- Protected API responses verified
