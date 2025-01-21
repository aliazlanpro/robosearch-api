# RoboSearch API

A FastAPI-based service for classifying research papers as RCTs (Randomized Controlled Trials).

This API application is based on [RobotSearch](https://github.com/ijmarshall/robotsearch), wrapping its core functionality into a API service.

## Features

- Fast and efficient RCT classification
- Publication Type (PTYP) integration
- Secure API authentication
- Docker support
- GitHub Actions CI/CD pipeline

## Environment Setup
The API requires authentication using an API token. This token must be:
1. Set in the application environment
2. Included in the request header when calling the `/predict` endpoint
3. Kept secure and not shared publicly

You can set the token in two ways:
- Development: In the `.env` file
- Production: As a GitHub repository secret

### Local Development
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Generate a secure token and set it in `.env`:
   ```bash
   API_TOKEN=your_generated_secure_token
   ```

### Production Setup
1. Go to GitHub repository settings
2. Navigate to Secrets and Variables → Actions
3. Add a new repository secret named `API_TOKEN` with your production token

### Running with Docker
Local development:
```bash
docker build --build-arg API_TOKEN=$(cat .env | grep API_TOKEN | cut -d '=' -f2) -t robosearch-api .
docker run -d -p 8000:8000 -e API_TOKEN=$(cat .env | grep API_TOKEN | cut -d '=' -f2) robosearch-api
```

Alternatively, you can pull the pre-built image from Docker Hub:
```bash
docker pull aliazlan/robosearch
docker run -d -p 8000:8000 -e API_TOKEN=your_token aliazlan/robosearch
```

## API Reference

### Authentication Details
- Token-based authentication using Bearer scheme
- Tokens must be kept secure and not shared
- Invalid tokens return 401 Unauthorized response
- Token rotation recommended every 90 days

### Detailed API Endpoints

#### 1. Health Check
```http
GET /
Returns: OpenAPI documentation
```

#### 2. RCT Prediction Endpoint
```http
POST /predict
Authorization: Bearer <your_token>

Request Body:
{
  "citations": [
    {
      "id": "string",
      "title": "string",
      "abstract": "string",
      "ptyp": ["string"],
      "use_ptyp": boolean
    }
  ]
}

Response:
[
  {
    "id": "string",
    "is_rct": boolean,
    "threshold_value": float,
    "ptyp_rct": integer
  }
]
```

Example curl request:
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Authorization: Bearer your_token" \
     -H "Content-Type: application/json" \
     -d '{
       "citations": [{
         "id": "123",
         "title": "A Randomized Trial of...",
         "abstract": "Background: This study...",
         "ptyp": ["Randomized Controlled Trial"],
         "use_ptyp": true
       }]
     }'
```

## Using RoboSearch as a Module

### Basic Usage
```python
from robosearch.robots.rct_robot import RCTRobot

# Initialize the classifier
rct_clf = RCTRobot()

# Single prediction
result = rct_clf.predict({
    "title": "Your paper title",
    "abstract": "Paper abstract text",
    "ptyp": ["Randomized Controlled Trial"],
    "use_ptyp": True
})

# Batch prediction
results = rct_clf.predict([
    {
        "title": "First paper title",
        "abstract": "First paper abstract",
        "ptyp": [],
        "use_ptyp": False
    },
    {
        "title": "Second paper title",
        "abstract": "Second paper abstract",
        "ptyp": ["Randomized Controlled Trial"],
        "use_ptyp": True
    }
])
```

### Advanced Configuration

#### Prediction Parameters
```python
rct_clf.predict(
    X,                          # Dict or List[Dict] of papers
    filter_class="svm",         # Model type: "svm" (default)
    filter_type="sensitive",    # Threshold type: "sensitive" or "specific"
    auto_use_ptyp=True,        # Auto-detect PTYP usage
    raw_scores=False           # Return raw prediction scores
)
```

#### Return Values
```python
# Standard return format
[{
    "model": "svm_ptyp",           # or "svm" if no PTYP
    "score": 0.85,                 # Classification score
    "threshold_value": 0.75,       # Classification threshold
    "is_rct": true,               # Final classification
    "ptyp_rct": 1,                # PTYP status (1=RCT, 0=not RCT, -1=no info)
    "preds": {                     # All prediction scores
        "svm": 0.82,
        "ptyp": 0.3,
        "svm_ptyp": 0.85
    }
}]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
5. Submit a pull request

## License

GPL-3.0 License - see LICENSE file for details
