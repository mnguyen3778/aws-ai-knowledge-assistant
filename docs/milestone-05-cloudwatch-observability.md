# Milestone 05 – Amazon CloudWatch Observability and Monitoring

## Objective

The objective of this milestone is to add production-grade observability to the AWS AI Knowledge Assistant.

Rather than only deploying a working application, this milestone demonstrates how to monitor, troubleshoot, and operate an AWS workload using Amazon CloudWatch.

---

# Architecture

Internet User
        │
AWS WAF
        │
Amazon Cognito
        │
API Gateway (REST API)
   ├── CloudWatch Execution Logs
   ├── CloudWatch Metrics
   └── Detailed Metrics
        │
AWS Lambda
   ├── CloudWatch Logs
   └── CloudWatch Metrics
        │
Amazon Bedrock
        │
Amazon Nova Lite

---

# AWS Services Used

- Amazon CloudWatch
- API Gateway
- AWS Lambda
- IAM
- AWS WAF
- Amazon Cognito
- Amazon Bedrock

---

# Implementation

## 1. Verified Lambda CloudWatch Logs

Confirmed that the Lambda function automatically writes execution logs to CloudWatch.

Verified Log Group:

```
/aws/lambda/aws-ai-assistant
```

Verified multiple log streams generated from Lambda invocations.

---

## 2. Created API Gateway CloudWatch IAM Role

Created a dedicated IAM service role for API Gateway.

Role Name:

```
AWS-API-Gateway-CloudWatch-Logs
```

Attached AWS Managed Policy:

```
AmazonAPIGatewayPushToCloudWatchLogs
```

Configured the trust relationship:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

---

## 3. Configured API Gateway Account Logging

Configured the CloudWatch Log Role ARN within API Gateway account settings.

Configured ARN:

```
arn:aws:iam::<ACCOUNT_ID>:role/AWS-API-Gateway-CloudWatch-Logs
```

Successfully verified API Gateway accepted the role.

---

## 4. Enabled API Gateway Monitoring

Enabled:

- Errors and Info Execution Logs
- Detailed CloudWatch Metrics

Left disabled:

- Data Tracing
- X-Ray Tracing
- Access Logging

This configuration provides production monitoring while avoiding unnecessary logging of request payloads.

---

## 5. Verified CloudWatch Metrics

Generated traffic through the API.

Verified CloudWatch metrics:

- Request Count
- Latency
- Integration Latency
- 4XX Errors
- 5XX Errors

Successfully graphed metrics within CloudWatch Metrics.

---

# Security Considerations

CloudWatch observability was configured following AWS best practices.

Security improvements include:

- Dedicated IAM service role
- Principle of Least Privilege
- Execution logs enabled
- Detailed metrics enabled
- Sensitive payload logging disabled
- Temporary credentials via IAM AssumeRole

---

# Scalability

CloudWatch automatically scales with API traffic.

Monitoring remains available regardless of request volume.

Metrics can later support:

- Auto Scaling decisions
- CloudWatch Alarms
- Dashboards
- Operational monitoring

---

# Cost Considerations

CloudWatch pricing is based on:

- Log ingestion
- Log storage
- Metrics
- Dashboards
- Alarms

For this portfolio project, CloudWatch costs remain very low while significantly improving operational visibility.

---

# Business Value

CloudWatch provides operational insight into application health.

Operations teams can quickly determine:

- API request volume
- Request latency
- Backend latency
- Client errors
- Server errors
- Lambda execution activity

This significantly reduces troubleshooting time during production incidents.

---

# Interview Talking Points

## Why CloudWatch?

CloudWatch provides centralized observability for AWS workloads.

Instead of manually investigating application issues, engineers can monitor logs, metrics, and operational health from a single service.

---

## Why Detailed Metrics?

Detailed metrics expose:

- Request Count
- Latency
- Integration Latency
- 4XX Errors
- 5XX Errors

These metrics provide immediate visibility into API performance.

---

## Why Disable Data Tracing?

Data tracing captures request and response payloads.

Although useful for debugging, it may log sensitive information.

Leaving it disabled follows production security best practices.

---

## Architecture Discussion

CloudWatch integrates across multiple AWS services:

Internet User
        │
AWS WAF
        │
Amazon Cognito
        │
API Gateway
        │
CloudWatch Logs
CloudWatch Metrics
        │
AWS Lambda
        │
Amazon Bedrock

This centralized observability enables engineers to identify whether issues originate from:

- Client requests
- Authentication
- API Gateway
- Lambda
- Downstream AI services

---

# Lessons Learned

A production application requires more than successful deployments.

Observability is critical for:

- Troubleshooting
- Performance monitoring
- Operational visibility
- Incident response
- Capacity planning

Amazon CloudWatch provides these capabilities through centralized logging and metrics.

---

# Milestone Status

✅ Lambda CloudWatch Logs

✅ API Gateway Execution Logging

✅ Detailed CloudWatch Metrics

✅ API Gateway IAM Logging Role

✅ CloudWatch Metrics Verified

✅ Production Observability Enabled

---

# Next Milestone

Milestone 06

Amazon CloudWatch Dashboards and Operational Monitoring

Objectives:

- Build CloudWatch Dashboard
- Visualize API Gateway Metrics
- Visualize Lambda Metrics
- Visualize AWS WAF Metrics
- Prepare for CloudWatch Alarms
