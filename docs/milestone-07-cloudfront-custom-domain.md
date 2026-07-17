# Milestone 7 — CloudFront and Custom Domain

## Objective

Replace the long API Gateway endpoint with a professional custom domain and place Amazon CloudFront at the network edge.

Benefits:

- Improved user experience
- Global edge delivery
- TLS termination
- Reduced latency
- Additional layer of protection before requests reach API Gateway
- Production-style architecture commonly used in AWS environments

---

## Architecture Before

Internet User
        │
AWS WAF
        │
Amazon Cognito
        │
API Gateway (REST API)
        │
AWS Lambda
        │
Amazon Bedrock
        │
Amazon Nova Lite

API Endpoint:

https://x2oc3toutj.execute-api.us-east-2.amazonaws.com

---

## Architecture After

Internet User
        │
Cloudflare DNS
        │
assistant.nguyen-ai.com
        │
Amazon CloudFront
        │
AWS WAF
        │
Amazon Cognito
        │
API Gateway (REST API)
        │
AWS Lambda
        │
Amazon Bedrock
        │
Amazon Nova Lite

---

## Services Implemented

### Amazon CloudFront

Purpose:

- Global content delivery network (CDN)
- Provides low-latency access through AWS edge locations
- Hides direct API Gateway endpoint from users
- Supports TLS certificates and custom domains

Configuration:

- Origin Type: API Gateway
- Origin:
  x2oc3toutj.execute-api.us-east-2.amazonaws.com
- Viewer Protocol Policy:
  Redirect HTTP to HTTPS
- Cache Policy:
  CachingDisabled
- Origin Request Policy:
  AllViewerExceptHostHeader
- Allowed Methods:
  GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE

Distribution Name:

assistant-nguyen-ai

CloudFront Domain:

d3p0yjo6ppcv4v.cloudfront.net

---

### TLS Certificate

Service:

AWS Certificate Manager (ACM)

Domain:

assistant.nguyen-ai.com

Purpose:

- HTTPS encryption
- Secure browser connections
- Required for custom CloudFront domains

Status:

Issued and attached to CloudFront distribution

---

### Cloudflare DNS

Purpose:

- Authoritative DNS provider for nguyen-ai.com
- Routes traffic to CloudFront

Record Created:

Type:
CNAME

Name:
assistant

Target:
d3p0yjo6ppcv4v.cloudfront.net

Result:

assistant.nguyen-ai.com

---

## Validation Performed

### CloudFront Distribution

Verified:

- Distribution successfully created
- Distribution deployed
- CloudFront domain accessible

### Custom Domain

Verified:

- assistant.nguyen-ai.com resolves successfully
- DNS propagation completed
- TLS certificate active

### Security Validation

Accessing:

https://assistant.nguyen-ai.com

Returns:

{
  "message": "Forbidden"
}

This confirms:

- CloudFront is forwarding requests
- API Gateway is reachable
- Cognito authorization remains enforced
- Unauthorized requests are blocked

---

## Security Considerations

### CloudFront

Provides:

- TLS termination
- Edge network protection
- Hides direct origin endpoint
- Improved resilience

### Cognito

Still protects API access.

Users must authenticate before accessing protected API resources.

### AWS WAF

Continues protecting API Gateway from:

- Common web exploits
- Malicious requests
- Rate abuse
- Automated attacks

---

## Scalability

CloudFront automatically scales globally.

Benefits:

- Reduced latency worldwide
- Increased availability
- Distributed edge infrastructure
- Reduced load on backend services

No infrastructure management required.

---

## Cost Considerations

CloudFront Pricing:

- Pay-as-you-go
- Requests
- Data transfer out

Current expected usage:

Minimal cost for development environment.

Cloudflare DNS:

Existing provider for nguyen-ai.com

No Route 53 charges incurred.

---

## Business Value

This milestone transitions the application from a development endpoint to a professional production-style architecture.

Benefits include:

- Professional branded endpoint
- Improved user trust
- HTTPS encryption
- Better performance
- Global scalability
- Foundation for future production deployment

Example:

Before:

https://x2oc3toutj.execute-api.us-east-2.amazonaws.com

After:

https://assistant.nguyen-ai.com

---

## Interview Talking Points

Why CloudFront?

- Improves latency through edge locations
- Supports custom domains
- Integrates with ACM certificates
- Reduces exposure of backend services

Why use a custom domain?

- Professional user experience
- Easier integration with applications
- Better branding and trust

Why Cloudflare instead of Route 53?

- Domain was already hosted in Cloudflare
- Avoided unnecessary DNS migration
- Demonstrates ability to integrate AWS with third-party DNS providers

How is security maintained?

- Cognito authorizer remains enforced
- WAF protects the API
- HTTPS enforced through CloudFront
- Unauthorized requests return Forbidden

Result:

A globally distributed, HTTPS-enabled AI application accessible through a professional custom domain.
