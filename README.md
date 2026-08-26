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
### Demo Users

For a fresh database, sample users for all three roles can be created with:

```bash
python manage.py seed_users
```

This command creates sample users for:

- Teacher
- Education Officer
- Finance Officer



- API documentation
  - OpenAPI schema
  - Swagger UI using drf-spectacular

### API Endpoints

```text
POST /api/accounts/login/
POST /api/accounts/refresh/

GET /api/accounts/me/


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
```


## Phase 3 - Session Report Workflow

In Phase 3, the session reporting workflow was implemented.

### Features

- Session report creation
  - Teachers can create reports for their own classrooms
  - Each report includes:
    - Session date and time
    - Lesson summary
    - Present students count
    - Absent students count

- Teacher classroom validation
  - Teachers can only create reports for classrooms assigned to them
  - The session date must be inside the teacher assignment period

- Late submission detection
  - The system automatically stores the submission time
  - Reports submitted more than 48 hours after the session are marked as late
  - Reports submitted at exactly 48 hours are not considered late
  - Teachers cannot manually change the late submission status

- Teacher report access
  - Teachers can view only their own reports
  - Teachers cannot create reports for another teacher's classroom

- Education Officer report access
  - Education Officers can view submitted reports
  - Reports can be filtered by:
    - School
    - Classroom
    - Teacher
    - Start date
    - End date

- Report review workflow
  - Education Officers can approve reports
  - Education Officers can reject reports
  - A rejection reason is required when a report is rejected
  - Education Officers cannot modify report content
  - Teachers cannot approve or reject their own reports

- Rejected report resubmission
  - Teachers can edit rejected reports
  - Pending and approved reports cannot be edited by teachers
  - After editing a rejected report:
    - Status returns to pending
    - Rejection reason is cleared
    - The original late submission status is preserved

- System-controlled fields
  - Teacher
  - Report status
  - Submission time
  - Late submission flag
  - Rejection reason

  These fields cannot be manually manipulated by teachers.

### Optional Features

- Monthly report summary
  - Teachers can view a monthly summary of their reports
  - The summary includes:
    - Total reports
    - Pending reports
    - Approved reports
    - Rejected reports

- Group approval
  - Education Officers can approve multiple pending reports in one request
  - Only pending reports are affected

- Report status history
  - Status changes are recorded
  - Each history record contains:
    - Report
    - New status
    - User who made the change
    - Change time
    - Optional note
  - Teachers can view the history of their own reports
  - Education Officers can view report histories
  - Teachers cannot view another teacher's report history

### API Endpoints

```text
GET  /api/reports/
POST /api/reports/


PATCH /api/reports/{id}/

GET /api/reports/education/

PATCH /api/reports/{id}/review/

GET /api/reports/monthly-summary/

POST /api/reports/group-approve/

GET /api/reports/{id}/history/


## Phase 4 - Salary Calculation

In Phase 4, the salary calculation system was implemented based on approved and non-late session reports.

### Features

- Salary rate management
  - Finance Officers can define a base salary rate for each teacher and term
  - The base rate is based on a 90-minute session
  - Each teacher can have only one salary rate per term

- Monthly salary calculation
  - Finance Officers can calculate salary for a specific teacher and month
  - Only approved and non-late session reports are included
  - 60-minute sessions use 70% of the base rate
  - 90-minute sessions use 100% of the base rate
  - 120-minute sessions use 130% of the base rate
  - Summer term sessions receive a 10% increase

- All teachers salary calculation
  - Finance Officers can calculate salaries for all teachers for a specific month

- Monthly salary list
  - Finance Officers can view calculated salaries for a specific year and month

- Teacher salary history
  - Teachers can view only their own salary history
  - Teachers cannot view another teacher's salary history

- Salary records
  - Only one salary record is stored for each teacher, year, and month
  - Recalculating a salary updates the existing record


### API Endpoints

```text
GET  /api/finance/rates/
POST /api/finance/rates/

POST /api/finance/calculate/
POST /api/finance/calculate-all/

GET  /api/finance/salaries/?year=2026&month=8
GET  /api/finance/my-salaries/
```

### Tests

Phase 4 includes tests for:

- Salary rate creation and validation
- Role-based access to salary operations
- Salary calculation for 60, 90, and 120-minute sessions
- Exclusion of late and unapproved reports
- Summer term 10% increase
- Salary calculation for a teacher with no approved reports
- Monthly salary calculation for all teachers
- Monthly salary list
- Teacher salary history
- Complete end-to-end system flow


## Project Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
DB_NAME=teacher_report_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your_secret_key
```

Apply database migrations:

```bash
python manage.py migrate
```

Create demo users:

```bash
python manage.py seed_users
```

Run the development server:

```bash
python manage.py runserver
```

Run all tests:

```bash
python manage.py test
```