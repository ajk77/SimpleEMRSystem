# API Documentation

## Overview

The Simple EMR System provides a RESTful API for managing studies, users, cases, and medical data. All API endpoints return JSON responses and follow consistent error handling patterns.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses Django's CSRF protection. Include the CSRF token in all POST requests:

```javascript
headers: {
    'X-CSRFToken': getCookie('csrftoken')
}
```

## Response Format

All API responses follow this standard format:

```json
{
    "status": "success|error",
    "message": "Optional message",
    "data": { /* Response data */ }
}
```

## Endpoints

### Study Management

#### GET `/`
Get the unified selection interface.

**Response:**
- Renders the study selection page with available studies

#### POST `/`
Handle study, user, and case selection requests.

**Request Body:**
```json
{
    "type": "fetch_users|fetch_cases",
    "study_id": "string",
    "user_id": "string" // Required for fetch_cases
}
```

**Response:**
```json
{
    "status": "success",
    "users": [ // For fetch_users
        {
            "id": "user_id",
            "name": "User Name"
        }
    ],
    "cases": { // For fetch_cases
        "assigned": ["case_id1", "case_id2"],
        "completed": ["case_id3"]
    }
}
```

### Case Management

#### GET `/case_viewer/`
Get the case viewer interface.

**Query Parameters:**
- `study_id` (required): Study identifier
- `user_id` (required): User identifier  
- `case_id` (required): Case identifier

**Response:**
- Renders the case viewer page with case data

#### GET `/api/get_case_data/`
Retrieve case data for viewing.

**Query Parameters:**
- `study_id` (required): Study identifier
- `case_id` (required): Case identifier

**Response:**
```json
{
    "status": "success",
    "case_data": {
        "demographics": {
            "age": "45",
            "gender": "M",
            "race": "White"
        },
        "medications": {
            "active": ["medication1", "medication2"],
            "discontinued": ["medication3"]
        },
        "notes": {
            "admission": "Patient admitted for...",
            "progress": "Daily progress notes..."
        },
        "observations": {
            "vitals": [
                {
                    "timestamp": "2024-01-01T10:00:00Z",
                    "systolic_bp": 120,
                    "diastolic_bp": 80,
                    "heart_rate": 72
                }
            ],
            "labs": [
                {
                    "timestamp": "2024-01-01T08:00:00Z",
                    "test": "CBC",
                    "value": "12.5",
                    "unit": "g/dL"
                }
            ]
        }
    }
}
```

#### POST `/SEMRinterface/selected_items/{study_id}/{user_id}/{case_id}/`
Save selected items for a case.

**Path Parameters:**
- `study_id`: Study identifier
- `user_id`: User identifier
- `case_id`: Case identifier

**Request Body:**
```json
{
    "selected_ids": ["item1", "item2", "item3"]
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Items saved successfully"
}
```

#### POST `/SEMRinterface/markcompleteurl/{study_id}/{user_id}/{case_id}/`
Mark a case as complete.

**Path Parameters:**
- `study_id`: Study identifier
- `user_id`: User identifier
- `case_id`: Case identifier

**Response:**
```json
{
    "status": "success",
    "message": "Case marked as complete"
}
```

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `405 Method Not Allowed`: Invalid HTTP method
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
    "status": "error",
    "message": "Error description",
    "code": "ERROR_CODE",
    "details": { /* Additional error details */ }
}
```

### Common Error Codes

- `MISSING_PARAMETERS`: Required parameters missing
- `STUDY_NOT_FOUND`: Study does not exist
- `USER_NOT_FOUND`: User does not exist
- `CASE_NOT_FOUND`: Case does not exist
- `INVALID_REQUEST_TYPE`: Invalid request type
- `SAVE_FAILED`: Failed to save data

## Data Models

### Study
```json
{
    "id": "study_identifier",
    "name": "Study Name",
    "description": "Study description",
    "created_date": "2024-01-01T00:00:00Z"
}
```

### User
```json
{
    "id": "user_identifier",
    "name": "User Name",
    "email": "user@example.com",
    "role": "researcher|clinician|admin",
    "cases_assigned": ["case1", "case2"],
    "cases_completed": ["case3"]
}
```

### Case
```json
{
    "id": "case_identifier",
    "study_id": "study_identifier",
    "patient_id": "patient_identifier",
    "status": "assigned|in_progress|completed",
    "created_date": "2024-01-01T00:00:00Z",
    "assigned_to": "user_identifier",
    "completed_date": "2024-01-02T00:00:00Z"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production deployments.

## CORS

CORS is not configured by default. Configure CORS settings if the API needs to be accessed from different domains.

## Security Considerations

1. **CSRF Protection**: All POST requests require valid CSRF tokens
2. **Input Validation**: All input parameters are validated
3. **SQL Injection**: Uses Django ORM to prevent SQL injection
4. **XSS Protection**: Template auto-escaping prevents XSS attacks
5. **File Access**: Restricted file access through service layer

## Examples

### JavaScript API Usage

```javascript
// Get case data
const response = await fetch('/api/get_case_data/?study_id=study1&case_id=case1');
const data = await response.json();

// Save selected items
const saveResponse = await fetch('/SEMRinterface/selected_items/study1/user1/case1/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        selected_ids: ['item1', 'item2']
    })
});
```

### Python API Usage

```python
import requests

# Get case data
response = requests.get('http://localhost:8000/api/get_case_data/', 
                       params={'study_id': 'study1', 'case_id': 'case1'})
data = response.json()

# Save selected items
save_response = requests.post(
    'http://localhost:8000/SEMRinterface/selected_items/study1/user1/case1/',
    json={'selected_ids': ['item1', 'item2']},
    headers={'X-CSRFToken': csrf_token}
)
```

## Changelog

### Version 2024.1
- Added comprehensive error handling
- Standardized response format
- Added detailed API documentation
- Improved parameter validation
- Enhanced security measures
