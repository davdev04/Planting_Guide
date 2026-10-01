# Planting Guide API

This project provides a small FastAPI app for storing plant records and generating a suggested planting date using the AI agent.

## Prerequisites

- Python 3.10 or newer
- A local OpenAI API key
- Access to the project dependencies in `requirements.txt`

## 1. Set up the environment

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file inside the `planting_guide` directory so the app can read the OpenAI configuration:

```env
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4o-mini
```

## 2. Run the local server

Start the app from the `planting_guide` folder:

```bash
cd planting_guide
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:

- http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs

## 3. Create a plant

Send a `POST` request to `/plants`.

If you do not provide a `planting_date`, the app will generate one automatically using the AI suggestion service.

### Example using curl

```bash
curl -X POST http://127.0.0.1:8000/plants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rose",
    "planting_age": "seedling"
  }'
```

Example response:

```json
{
  "id": 1,
  "plant": {
    "id": 1,
    "name": "Rose",
    "planting_date": "2026-02-27",
    "planting_age": "seedling"
  }
}
```

You can also include an explicit `planting_date` if needed:

```json
{
  "name": "Tomato",
  "planting_date": "2026-03-10",
  "planting_age": "seedling"
}
```

## 4. List plants

Send a `GET` request to `/plants`.

```bash
curl http://127.0.0.1:8000/plants
```

Example response:

```json
[
  {
    "id": 1,
    "name": "Rose",
    "planting_date": "2026-02-27",
    "planting_age": "seedling"
  }
]
```

## 5. Delete a plant

Send a `DELETE` request to `/plants/{plant_id}`.

```bash
curl -X DELETE http://127.0.0.1:8000/plants/1
```

This returns HTTP `204 No Content` when the plant is deleted successfully.

## 6. Optional: get a plant by ID

```bash
curl http://127.0.0.1:8000/plants/1
```

This endpoint returns the plant record for that ID, or a `404 Not Found` error if it does not exist.

## Notes

- The app keeps data in memory while the server is running.
- Restarting the server clears the plant list.
- The AI planting date suggestion endpoint is available at `/api/agent/suggest_planting_date`.
