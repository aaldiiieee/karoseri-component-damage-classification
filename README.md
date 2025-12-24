# Final Project (UNPAM)

This is a FastAPI project for the final project assignment.

## Prerequisites
- **Python 3.13** (Important: Version 3.14 is currently not fully supported by `pydantic-core`)

## Installation Guide

1. **Clone this repository** (if using Git):
    ```bash
    git clone <repository-url>
    cd final-project
    ```

2. **Create a Virtual Environment (VENV)**:
   Ensure you are using Python 3.13.
   ```bash
   python3.13 -m venv .venv
   ```

3. **Activate the Virtual Environment**:
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Running the Application

Start the server using the FastAPI CLI (development mode):

```bash
fastapi dev main.py
```

Once running, you can access:
- **Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Troubleshooting

### `subprocess-exited-with-error` during `pydantic-core` installation
This usually occurs because you are using **Python 3.14**. Please ensure you are using **Python 3.13** as specified in the prerequisites section.
