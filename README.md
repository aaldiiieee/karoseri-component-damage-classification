# Karoseri Component Damage Classification

This is a FastAPI project for the final project of Pamulang University (UNPAM)

## Installation Guide

1. **Clone this repository** (if using Git):
    ```bash
    git clone https://github.com/aaldiiieee/karoseri-component-damage-classification.git
    cd karoseri-component-damage-classification
    ```

2. **Create a Virtual Environment (VENV)**:
   Ensure you are using Python 3
   ```bash
   python3 -m venv .venv
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

Start the server using uvicorn (development mode):

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Or using uvicorn (production mode):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Once running, you can access:
- **Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
