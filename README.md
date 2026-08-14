# Teacher Report System
A Django REST Framework API for managing schools, classrooms, session reports, and teacher salary calculation.

## Description

A Django REST Framework project for managing:

- Teachers
- Schools
- Terms
- Classrooms
- Session Reports
- Salary Calculation

## Technologies

- Python
- Django
- Django REST Framework
- PostgreSQL
- Git
- GitHub

## Project Phases

- Phase 1: Authentication & Roles
- Phase 2: Education Management
- Phase 3: Session Reports
- Phase 4: Salary Calculation


## Phase 1 - Authentication & Roles

In Phase 1, the base authentication and role-based access system was implemented.

### Features

- Custom user model
  - Username
  - First name
  - Last name
  - Phone number
  - Emergency phone number
  - Role

- Supported roles
  - Teacher
  - Education Officer
  - Finance Officer

- JWT authentication
  - Login using username and password
  - Access token
  - Refresh token
  - Token refresh endpoint

- User profile
  - Authenticated users can view their own information
  - Users can see their assigned role

- Role-based permissions
  - Teachers can access teacher-specific endpoints
  - Education Officers can access education-specific endpoints
  - Finance Officers can access finance-specific endpoints
  - Users cannot access endpoints belonging to other roles

- User creation
  - There is no public registration endpoint
  - Users are created by the system administrator
  - A Django management command is available for creating users with a specific role

Example:

```bash
python manage.py create_user \
  --role teacher \
  --username teacher1 \
  --password 1234 \
  --first_name John \
  --last_name Doe \
  --phone_number 09123456789 \
  --emergency_phone 09987654321
```

- API documentation
  - OpenAPI schema
  - Swagger UI using drf-spectacular

### API Endpoints

```text
POST /api/accounts/login/
POST /api/accounts/refresh/

GET /api/accounts/me/

GET /api/accounts/teacher/
GET /api/accounts/education/
GET /api/accounts/finance/
```

### Tests

Phase 1 includes tests for:

- Custom user model
- User roles
- Authentication
- JWT login
- User profile
- Teacher permissions
- Education Officer permissions
- Finance Officer permissions
- Access boundaries between different roles
- User creation management command

Run all project tests:

```bash
python manage.py test
```

### Known Limitations

- There is no public user registration.
- Users must be created by the system administrator.
- The project is API-only and does not include a frontend interface.


## Phase 2 - Education Management

In Phase 2, the education management features were implemented.

### Features

- School management
  - Create schools
  - List schools
  - Update schools

- Term management
  - Create terms
  - List terms
  - Update terms
  - Validate start and end dates
  - Support normal and summer terms

- Classroom management
  - Create classrooms for a school and term
  - List classrooms
  - Update classrooms
  - Session duration limited to 60, 90, or 120 minutes

- Teacher assignments
  - Assign teachers to classrooms
  - Support assignment start and optional end dates
  - Support different teachers for the same classroom in different periods
  - Prevent overlapping teacher assignments
  - Validate assignment dates against the term

- Teacher classroom access
  - Teachers can view only their own current and previous classrooms

- Role-based permissions
  - Education officers manage education data
  - Teachers and finance officers cannot perform education management operations

### Tests

Run all project tests:

```bash
python manage.py test
