# Todo List Backend

A secure and efficient Todo List API built with FastAPI and SQLModel, featuring OAuth2.0 authentication with Password Flow and JWT Bearer Tokens for secure access control.

The API leverages SQLite as the database, using SQLModel—a modern ORM built on top of SQLAlchemy and Pydantic—to handle database operations efficiently.

## Key Features
- Secure authentication using OAuth2.0 Password Flow with JWT Tokens
- Password hashing with bcrypt for enhanced security
- Full CRUD operations for task management
- Category-based organization of tasks with proper relationships
- SQLite database with SQLModel ORM
- FastAPI-based architecture for high performance and built-in OpenAPI documentation

## Technology Stack
- FastAPI – High-performance framework for building APIs
- SQLModel – ORM combining SQLAlchemy and Pydantic
- SQLite – Lightweight, file-based database
- OAuth2.0 (Password Flow) – Secure authentication mechanism
- JWT (JSON Web Tokens) – Token-based authentication
- Passlib (bcrypt) – Secure password hashing
- Uvicorn – ASGI server for running FastAPI applications

## Authentication & Security

This API follows OAuth2.0 Password Flow, allowing users to authenticate using their username and password. Upon successful authentication, a JWT Bearer Token is issued, which must be included in all authenticated requests.

### Authentication Flow:
1.	User Registration: Create an account by providing a username and password.
2.	Token Generation: Authenticate using credentials to receive a JWT Token.
3.	Authenticated Requests: Use the Bearer Token in all API requests requiring authentication.

#### Example of an authenticated request:

`
GET /todos/
Authorization: Bearer YOUR_ACCESS_TOKEN
`

## Future Enhancements
- Migrate from SQLite to PostgreSQL for better scalability
- Implement Role-Based Access Control (RBAC) to restrict access based on user roles
- Enhance logging and monitoring for better observability
- Containerize the application with Docker
- Add comprehensive test coverage with Pytest

# License

This project is licensed under the MIT License.
