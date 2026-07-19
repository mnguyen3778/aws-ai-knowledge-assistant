# Milestone 11 - AI Readiness Assessment Foundation

## Objective

Prepare the backend contract for a future Nguyen-AI Readiness Assessment endpoint without changing the existing chat endpoint, invoking Bedrock for assessment recommendations, or persisting assessment data to DynamoDB.

## Architecture

Current production request path:

Cloudflare
↓
CloudFront
↓
AWS WAF
↓
Amazon Cognito
↓
Amazon API Gateway
↓
AWS Lambda

The Lambda now has a dedicated assessment route:

POST /assessment
↓
assessment.handler
↓
assessment.validation
↓
assessment.scoring
↓
JSON response

The existing chat path continues to use the existing Lambda Bedrock integration.

## Request Flow

1. API Gateway invokes Lambda.
2. Lambda routes `POST /assessment` to `handle_assessment`.
3. The assessment handler validates the request body.
4. Valid requests are passed to the scoring framework.
5. The scoring framework returns a deterministic placeholder response until the official Nguyen-AI rubric is available.
6. The handler returns JSON to the client.

No Bedrock calls are made by the assessment flow.

No DynamoDB writes are made by the assessment flow.

## API Contract

Endpoint:

```text
POST /assessment
```

Required request fields:

```json
{
  "assessmentVersion": "nguyen-ai-readiness-v1",
  "organization": {},
  "respondent": {},
  "answers": {
    "canonical.question.id": 3
  }
}
```

The `answers` object is intentionally keyed by question ID so the backend can consume the website's canonical Question Bank without hardcoding question IDs in the schema.

The backend also supports answer entries:

```json
{
  "assessmentVersion": "nguyen-ai-readiness-v1",
  "organization": {},
  "respondent": {},
  "answers": [
    {
      "questionId": "canonical.question.id",
      "value": 3
    }
  ]
}
```

Successful response:

```json
{
  "requestId": "uuid",
  "assessmentVersion": "nguyen-ai-readiness-v1",
  "overallScore": 0,
  "readinessLevel": {
    "id": "pending-rubric",
    "label": "Pending Official Rubric",
    "description": "Deterministic scoring is not available until the official Nguyen-AI rubric is provided."
  },
  "categoryScores": [],
  "recommendations": [],
  "modelInvoked": false,
  "persisted": false
}
```

Validation error response:

```json
{
  "requestId": "uuid",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Assessment request is invalid.",
    "details": []
  },
  "modelInvoked": false,
  "persisted": false
}
```

## Validation Layer

Validation covers:

- valid JSON
- required top-level fields
- supported `assessmentVersion`
- non-empty `answers`
- numeric answer values
- duplicate question IDs
- unknown top-level fields
- unknown answer-entry fields

The validation layer does not implement scoring rules, answer ranges, category mapping, weights, or readiness thresholds because those depend on the official Nguyen-AI rubric.

## Scoring Framework

The scoring module exposes:

```python
score_assessment(request)
```

It currently returns a deterministic placeholder response with:

- `overallScore`: `0`
- `readinessLevel.id`: `pending-rubric`
- empty `categoryScores`
- empty `recommendations`
- `modelInvoked`: `false`
- `persisted`: `false`

## Future Bedrock Integration

Future Bedrock usage should be added only after deterministic scoring exists. Bedrock should be used for narrative explanation or recommendation wording, not as the source of the assessment score.

## Future DynamoDB Persistence

Future persistence should store the validated request, deterministic score output, request ID, user identity from Cognito claims, timestamp, and scoring version. Persistence should occur after successful validation and scoring.

## Known TODO Items

- Add canonical Nguyen-AI Question Bank mappings.
- Add category mappings.
- Add official question/category weights.
- Add official readiness thresholds.
- Add official recommendation mappings.
- Add score boundary tests once thresholds are known.
- Add persistence contract once DynamoDB storage requirements are approved.
- Add Bedrock recommendation contract once model-generated narrative output is approved.
