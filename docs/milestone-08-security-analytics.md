# Milestone 08 – Security Analytics with AWS WAF, S3, Glue, and Athena

## Objective

Build a security analytics pipeline that enables investigation of AWS WAF events using serverless AWS services.

## Architecture

Internet User
↓
AWS WAF
↓
Amazon S3
↓
AWS Glue Crawler
↓
Glue Data Catalog
↓
Amazon Athena

## Services Used

- AWS WAF
- Amazon S3
- AWS Glue
- AWS Glue Crawler
- AWS Glue Data Catalog
- Amazon Athena

## Implementation

### WAF Logging

Configured AWS WAF logging to Amazon S3.

### S3 Storage

WAF logs stored in compressed JSON format.

### Glue Crawler

Created crawler:
- waf-log-crawler

Database:
- security_logs

### Athena

Configured Athena query results location.

Validated queries against WAF log data.

Example query:

```sql
SELECT action, COUNT(*) AS requests
FROM aws_waf_logs_nguyen_ai_683210040136_us_east_2_an
GROUP BY action;
