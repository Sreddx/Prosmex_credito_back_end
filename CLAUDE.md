# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based serverless backend API for the Prosmex credit management system, designed to run on AWS Lambda via Zappa. The system manages loans, payments, clients, and related financial operations for microfinance operations.

## Development Commands

This is a Python Flask application with no package.json. Common operations:

- **Install dependencies**: `pip install -r requirements.txt`
- **Run locally**: Use Flask's built-in development server
- **Deploy**: `zappa deploy dev` or `zappa update dev` (requires AWS credentials and Zappa configuration)
- **Database migrations**: Uses Flask-Migrate - run migrations with `flask db migrate` and `flask db upgrade`

## Architecture

### Core Structure
- **Flask App Factory**: `app/__init__.py` creates the Flask application with configuration management
- **Blueprints**: API routes organized by domain in `app/blueprints/` (auth, clientes, prestamos, pagos, etc.)
- **Models**: SQLAlchemy models in `app/models/` representing database entities
- **Services**: Business logic layer in `app/services/` handling complex operations
- **Database**: PostgreSQL with SQLAlchemy ORM and Flask-Migrate for schema management

### Key Components
- **Authentication**: JWT-based auth with Flask-JWT-Extended
- **Database**: PostgreSQL connection configured via environment variables
- **Deployment**: Serverless deployment using Zappa for AWS Lambda
- **CORS**: Configured to accept all origins with credential support
- **Timezone**: Mexico City timezone handling via pytz
- **Scheduled Tasks**: APScheduler for background payment verification tasks

### Configuration
- **Environment-based configs**: LocalConfig, QAConfig, ProductionConfig in `config.py`
- **Secrets**: Uses environment variables for sensitive data (DATABASE_URL, SECRET_KEY, JWT keys)
- **Zappa Settings**: AWS deployment configuration in `zappa_settings.json`

### Data Model Domains
- **Users & Auth**: Usuario, Rol, Permiso models with role-based access
- **Clients**: ClienteAval for client and guarantor information
- **Loans**: Prestamo, TipoPrestamo for loan management
- **Payments**: Pago model with payment tracking and scheduling
- **Groups & Routes**: Grupo, Ruta for organizing clients and payment collection
- **Financial Operations**: Bono, Corte, Falta for bonuses, cuts, and infractions

### Important Notes
- The app automatically populates initial data on startup via `populate_data()`
- Uses production config by default in the app factory
- Database connection and session management handled in `app/database.py`
- Blueprint registration includes all major functional areas
- Error handling configured at the app level with logging

## Cross-Repository Coordination

When implementing changes from other repositories (typically frontend), use this template to systematically handle updates:

### Change Assessment Process
1. **Identify Impact Areas**: Review changes against these backend components:
   - API endpoints in `app/blueprints/*/routes.py`
   - Data models in `app/models/`
   - Service layer logic in `app/services/`
   - Authentication/authorization flows
   - Database schema and migrations

2. **Common Integration Points**:
   - **Authentication**: JWT token structure, user roles, permissions
   - **API Contracts**: Request/response formats, validation rules
   - **Data Models**: Field additions, relationship changes, constraints
   - **Business Logic**: Payment processing, loan calculations, reporting

### Implementation Checklist
When receiving cross-repository updates:
- [ ] Update API endpoints to match new frontend requirements
- [ ] Modify data models and create migrations if schema changes needed
- [ ] Update service layer business logic
- [ ] Adjust authentication/authorization rules
- [ ] Update CORS settings if new frontend domains added
- [ ] Verify database constraints and validation rules
- [ ] Test API responses match expected frontend contracts
- [ ] Update environment variables in `zappa_settings.json` if needed

### Manual Testing Integration Changes
- Test all modified API endpoints with expected request formats using tools like Postman or curl
- Verify JWT token handling and user session management manually
- Validate database operations and constraint enforcement through direct API calls
- Test CORS functionality with frontend domains
- Manually test payment processing workflows end-to-end
- Verify scheduled task functionality remains intact through logs and database checks