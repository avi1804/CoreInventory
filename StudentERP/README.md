# 🎓 StudentERP — Spring Boot Backend

A full-featured Student Enterprise Resource Planning system built with Spring Boot 3, Spring Security + JWT, Hibernate/JPA, and MySQL.

---

## 🏗️ Architecture

```
StudentERP/
├── controller/        REST controllers (AuthController, StudentController, ...)
├── service/           Business logic (StudentService, AttendanceService, ...)
├── repository/        JPA repositories (Spring Data)
├── model/             JPA entities (User, Student, Faculty, ...)
├── security/          JWT utils, filters, UserDetails
├── dto/               Request/Response DTOs
├── exception/         GlobalExceptionHandler, ResourceNotFoundException
├── config/            SecurityConfig, DataInitializer, SchedulerConfig
└── resources/
    ├── application.properties
    └── schema.sql
```

---

## ⚙️ Setup & Run

### 1. Prerequisites
- Java 17+
- Maven 3.8+
- MySQL 8.0+

### 2. Configure Database
Edit `src/main/resources/application.properties`:
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/student_erp?createDatabaseIfNotExist=true
spring.datasource.username=root
spring.datasource.password=YOUR_PASSWORD
```

### 3. Build & Run
```bash
cd StudentERP
mvn clean install
mvn spring-boot:run
```

The app starts at **http://localhost:8080**

On first run, a default admin is seeded automatically:
```
Email    : admin@college.edu
Password : Admin@1234
```

---

## 🔐 Authentication

All protected endpoints require a `Bearer` token in the `Authorization` header.

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@college.edu",
  "password": "Admin@1234"
}
```

**Response:**
```json
{
  "token": "eyJhbGci...",
  "type": "Bearer",
  "id": 1,
  "name": "System Administrator",
  "email": "admin@college.edu",
  "role": "ADMIN"
}
```

### Use the token
```http
GET /api/students
Authorization: Bearer eyJhbGci...
```

---

## 📡 API Reference

### Auth
| Method | Endpoint             | Role     | Description         |
|--------|----------------------|----------|---------------------|
| POST   | /api/auth/login      | Public   | Login → JWT         |
| POST   | /api/auth/register   | Public   | Register new user   |
| GET    | /api/auth/me         | Any      | Current user info   |

### Students
| Method | Endpoint                        | Role          | Description           |
|--------|---------------------------------|---------------|-----------------------|
| POST   | /api/students                   | ADMIN         | Enroll student        |
| GET    | /api/students                   | ADMIN,FACULTY | List all students     |
| GET    | /api/students/{id}              | Any           | Student by ID         |
| GET    | /api/students/roll/{rollNo}     | Any           | Student by roll no    |
| GET    | /api/students/search?q=...      | ADMIN,FACULTY | Search students       |
| GET    | /api/students/class?branch=CSE&semester=3 | ADMIN,FACULTY | Class list |
| PUT    | /api/students/{id}              | ADMIN         | Update profile        |
| PATCH  | /api/students/{id}/status       | ADMIN         | Update status         |
| DELETE | /api/students/{id}              | ADMIN         | Deactivate student    |

### Attendance
| Method | Endpoint                        | Role          | Description              |
|--------|---------------------------------|---------------|--------------------------|
| POST   | /api/attendance/mark            | FACULTY,ADMIN | Mark single attendance   |
| POST   | /api/attendance/mark-bulk       | FACULTY,ADMIN | Mark entire class        |
| GET    | /api/attendance/student/{id}    | Any           | Student records          |
| GET    | /api/attendance/report          | Any           | % report per subject     |
| GET    | /api/attendance/class           | FACULTY,ADMIN | Class attendance by date |
| GET    | /api/attendance/low             | FACULTY,ADMIN | Below-threshold students |

### Marks & Results
| Method | Endpoint                        | Role          | Description           |
|--------|---------------------------------|---------------|-----------------------|
| POST   | /api/marks/enter                | FACULTY,ADMIN | Enter marks           |
| POST   | /api/marks/enter-bulk           | FACULTY,ADMIN | Bulk marks entry      |
| GET    | /api/marks/result               | Any           | Full result card      |
| GET    | /api/marks/subject              | FACULTY,ADMIN | Subject-wise marks    |

### Fee Management
| Method | Endpoint                        | Role    | Description           |
|--------|---------------------------------|---------|-----------------------|
| POST   | /api/fees                       | ADMIN   | Create fee record     |
| PUT    | /api/fees/{id}/pay              | ADMIN   | Mark as paid          |
| GET    | /api/fees/student/{id}          | Any     | Student's fees        |
| GET    | /api/fees/summary               | ADMIN   | Dashboard summary     |
| POST   | /api/fees/mark-overdue          | ADMIN   | Flag overdue fees     |
| GET    | /api/fees/{id}/receipt          | Any     | Download PDF receipt  |

### Notices
| Method | Endpoint                        | Role          | Description           |
|--------|---------------------------------|---------------|-----------------------|
| GET    | /api/notices                    | Any           | All active notices    |
| GET    | /api/notices/category/{cat}     | Any           | Filter by category    |
| POST   | /api/notices                    | FACULTY,ADMIN | Post a notice         |
| DELETE | /api/notices/{id}               | ADMIN         | Archive notice        |

---

## 👥 Role Permissions

| Feature             | ADMIN | FACULTY | STUDENT |
|---------------------|-------|---------|---------|
| Manage Students     | ✅    | 👁 Read | 👁 Self |
| Mark Attendance     | ✅    | ✅      | ❌      |
| Enter Marks         | ✅    | ✅      | ❌      |
| View Results        | ✅    | ✅      | ✅ Self |
| Manage Fees         | ✅    | ❌      | 👁 Self |
| Download Receipt    | ✅    | ❌      | ✅ Self |
| Post Notices        | ✅    | ✅      | ❌      |
| Delete Notices      | ✅    | ❌      | ❌      |

---

## 🗄️ Database Tables

| Table        | Purpose                                    |
|--------------|--------------------------------------------|
| `users`      | All users (Admin, Faculty, Student)        |
| `students`   | Student profiles (linked to users)         |
| `faculty`    | Faculty profiles (linked to users)         |
| `subjects`   | Course subjects per branch/semester        |
| `attendance` | Daily attendance per student per subject   |
| `marks`      | Exam marks per student per subject         |
| `fees`       | Fee records with payment status            |
| `notices`    | Notice board entries                       |

---

## 📚 Advanced Java Concepts Used

| Concept                 | Where Used                                         |
|-------------------------|----------------------------------------------------|
| Spring Boot             | Core framework, auto-configuration                 |
| Hibernate / JPA         | ORM entities, repositories, JPQL queries           |
| Spring Security         | Filter chain, role-based access control            |
| JWT (jjwt)              | Stateless authentication tokens                    |
| Maven                   | Dependency management, build lifecycle             |
| REST APIs               | All controllers (JSON in/out)                      |
| DTO Pattern             | AuthDTOs, service-level request/response objects   |
| iText PDF               | Fee receipt generation in FeeService               |
| @Scheduled              | Nightly overdue fee detection                      |
| @Transactional          | All write operations in service layer              |
| Global Exception Handler| @RestControllerAdvice with typed handlers          |
| Spring Data Auditing    | createdAt / updatedAt on entities                  |
| @PreAuthorize           | Method-level security on controllers               |
| CommandLineRunner       | DataInitializer seeds admin on first boot          |

---

## 🧪 Sample Requests (cURL)

```bash
# Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@college.edu","password":"Admin@1234"}'

# List students (replace TOKEN)
curl http://localhost:8080/api/students \
  -H "Authorization: Bearer TOKEN"

# Mark attendance
curl -X POST http://localhost:8080/api/attendance/mark \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"studentId":1,"subjectId":2,"date":"2026-04-03","status":"PRESENT"}'

# Get result card
curl "http://localhost:8080/api/marks/result?studentId=1&examType=MID_SEM" \
  -H "Authorization: Bearer TOKEN"

# Download fee receipt (returns PDF)
curl http://localhost:8080/api/fees/1/receipt \
  -H "Authorization: Bearer TOKEN" \
  --output receipt.pdf
```
