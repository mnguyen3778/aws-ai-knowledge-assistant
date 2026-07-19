# Milestone 11 - AI Readiness Assessment Foundation

## Objective

Prepare the backend contract for a future Nguyen-AI Readiness Assessment endpoint without changing the existing chat endpoint, invoking Bedrock for assessment recommendations, or persisting assessment data to DynamoDB.

The official Nguyen-AI assessment rubric does not exist yet. The implementation therefore provides a configuration-driven foundation and deterministic placeholder scoring only.

## Package Architecture

Assessment code is isolated under:

```text
src/assessment/
  config.py
  models.py
  schema.py
  validation.py
  scoring.py
  handler.py
```

Module responsibilities:

- `config.py`: single source for assessment versions, schema rules, question definitions, category definitions, weights, thresholds, recommendation mappings, and placeholder scoring output.
- `models.py`: version-aware request, response, validation, category, readiness-level, and recommendation dataclasses.
- `schema.py`: stable wire-format field names and lightweight answer-entry model.
- `validation.py`: JSON parsing, version resolution, configured field validation, answer normalization, numeric answer validation, duplicate question ID detection, and structured validation errors.
- `scoring.py`: deterministic scoring entry point that consumes version configuration.
- `handler.py`: Lambda route handler for assessment requests.

## Request Lifecycle

```text
POST /assessment
-> lambda_function.lambda_handler
-> assessment.handler.handle_assessment
-> assessment.validation.validate_assessment_request
-> assessment.scoring.score_assessment
-> JSON response
```

The assessment route is isolated from the existing chat route. Non-assessment requests continue through the existing Bedrock chat implementation.

## API Contract

Endpoint:

```text
POST /assessment
```

Required request fields for `nguyen-ai-readiness-v1`:

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

The `answers` object is intentionally keyed by question ID so the backend can consume the website's future canonical Question Bank without hardcoding Nguyen-AI question IDs in the schema.

The backend also accepts list-form answers:

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

Successful placeholder response:

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
    "details": [
      {
        "field": "answers.canonical.question.id",
        "message": "Answer value must be numeric.",
        "code": "INVALID_FIELD"
      }
    ]
  },
  "modelInvoked": false,
  "persisted": false
}
```

## Validation Flow

Validation runs in this order:

1. Parse the request body as JSON while rejecting duplicate object keys.
2. Resolve `assessmentVersion` against configured versions in `config.py`.
3. Validate required and allowed top-level fields from the selected version config.
4. Validate configured object fields, such as `organization` and `respondent`.
5. Require non-empty `answers`.
6. Normalize answers into a stable `dict[questionId, numericValue]`.
7. Reject non-numeric answer values.
8. Reject duplicate question IDs in list-form answers.
9. Return structured validation errors without scoring.

Validation intentionally does not enforce answer ranges, category membership, or required question IDs until the official question bank and scoring rubric exist.

## Scoring Flow

The scoring module exposes:

```python
score_assessment(request)
```

Current behavior:

1. Resolve the request's assessment version from `config.py`.
2. Read the configured placeholder result.
3. Return a deterministic response with no category scores and no recommendations.
4. Set `modelInvoked` to `false`.
5. Set `persisted` to `false`.

Future deterministic scoring should still use `score_assessment(request)` as the entry point.

## Configuration Architecture

`config.py` contains `AssessmentVersionConfig` entries keyed by version:

```python
ASSESSMENT_CONFIGS = {
    "nguyen-ai-readiness-v1": NGUYEN_AI_READINESS_V1,
}
```

Each version config owns:

- required request fields
- allowed request fields
- object fields
- answer-entry required fields
- answer-entry allowed fields
- question definitions
- category definitions
- weights
- thresholds
- recommendation mappings
- placeholder result

The rubric-specific structures are intentionally empty placeholders until the official Nguyen-AI rubric exists.

## Extension Strategy

To add a future assessment version:

1. Add a new `AssessmentVersionConfig` in `config.py`.
2. Add the version to `ASSESSMENT_CONFIGS`.
3. Populate official question definitions, category definitions, weights, thresholds, and recommendation mappings.
4. Add scoring tests for the new version.
5. Add boundary tests for readiness thresholds.

The validation layer and handler should not require major changes for a new version if the request shape is expressible through the version config.

## Future Bedrock Integration

Bedrock should not be the source of readiness scores. Future Bedrock integration should happen only after deterministic scoring exists and should be limited to narrative explanation, summary language, or recommendation wording.

The assessment response should continue to expose whether a model was invoked through `modelInvoked`.

## Future DynamoDB Persistence

Future persistence should store:

- request ID
- assessment version
- normalized answers
- deterministic score output
- Cognito user identity
- timestamp
- scoring/rubric version
- model invocation metadata, if Bedrock is later added

Persistence should occur after successful validation and deterministic scoring. The response should continue to expose whether data was persisted through `persisted`.

## Known TODO Items

- Add canonical Nguyen-AI Question Bank.
- Add official category definitions.
- Add official question-to-category mappings.
- Add official question/category weights.
- Add official readiness thresholds.
- Add official recommendation mappings.
- Add deterministic scoring rules.
- Add score boundary tests once thresholds are known.
- Add persistence contract once DynamoDB storage requirements are approved.
- Add Bedrock recommendation contract once model-generated narrative output is approved.

