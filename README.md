# FastAPI Project

This is a FastAPI application using SQLAlchemy and JWT authentication.
The project includes several entities: **Users, Hotels, Rooms, and Bookings.**

## Prerequisites

Make sure you have the following installed on your machine:
- [Python](https://www.python.org/) (Recommended: 3.8+)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Installation

1. Clone this repository:
\`\`\`sh
git clone <repository_url>
cd <repository_directory>
\`\`\`

2. Create a virtual environment:
\`\`\`sh
python -m venv venv
\`\`\`

3. Activate the virtual environment:
- On macOS/Linux:
\`\`\`sh
source venv/bin/activate
\`\`\`
- On Windows (Command Prompt):
\`\`\`cmd
venv\Scripts\activate
\`\`\`
- On Windows (PowerShell):
\`\`\`powershell
venv\Scripts\Activate.ps1
\`\`\`

4. Install dependencies using Poetry:
\`\`\`sh
poetry install
\`\`\`

## Running the Application

To start the application, use Docker Compose:

\`\`\`sh
make run
\`\`\`

This will build and run the containers in detached mode.

Once running, the FastAPI application will be available at:
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

You can also access the interactive API documentation at:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Running Tests

To execute tests, follow these steps:

1. Create a virtual environment (if not done already):
\`\`\`sh
python -m venv venv
\`\`\`

2. Activate the virtual environment:
\`\`\`sh
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows Command Prompt
venv\Scripts\Activate.ps1 # Windows PowerShell
\`\`\`

3. Run tests using Make:
\`\`\`sh
make testing
\`\`\`

This will:
- Stop and remove any existing Docker containers.
- Rebuild and start new containers.
- Wait for FastAPI to start.
- Run tests using \`pytest\`.
- Shut down the containers after tests complete.

## Environment Variables

Ensure you have a \`.env\` file containing required environment variables:

\`\`\`ini
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
DATABASE_URL=postgresql://your_user:your_password@postgres_db:5432/your_database
TEST_DATABASE_URL=postgresql://your_user:your_password@postgres_db:5432/your_test_database
ENDPOINT=your_endpoint
ACCESS_KEY=your_access_key
SECRET_KEY=your_secret_key
BUCKET_NAME=your_bucket_name
\`\`\`

## Stopping the Application

To stop the running containers, use:

\`\`\`sh
docker-compose down -v
\`\`\`

---

## License

This project is licensed under the MIT License.
EOL# akkor-hotel-back
