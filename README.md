# Livedisplaced.com

A comprehensive web platform for tracking and visualizing refugee displacement data over time.

## Overview

Livedisplaced.com is a full-stack web application that provides updated visualization and analysis of refugee displacement data worldwide. The platform offers interactive dashboards, detailed country reports, and comprehensive data analysis tools to help understand global displacement patterns.

## Features

- **Real-time Data Visualization**: Interactive charts and graphs showing refugee movement patterns
- **Country-Specific Reports**: Detailed analysis of refugee flows for individual countries
- **Bilateral Analysis**: Compare refugee movements between specific countries
- **User Authentication**: Secure login and registration system
- **Cookie Management**: GDPR-compliant cookie consent system
- **Responsive Design**: Mobile-friendly interface

## Tech Stack

### Frontend
- HTML5, CSS3
- Bootstrap 5
- Chart.js for data visualization
- JavaScript (ES6+)
- Jinja2 templating

### Backend
- Python 3.13
- Quart (async web framework)
- SQLAlchemy (async database ORM)
- PostgreSQL
- Alembic (database migrations)
- SendGrid (email services)

## Project Structure

```
livedisplaced_/
├── front/                 # Frontend templates and static files
├── src/                   # Backend source code
│   ├── Controllers/       # Route handlers and views
│   ├── Infrastructure/    # Database, email, and logging services
│   ├── Context/          # Business logic and services
│   └── Middlewares/      # Application middleware
├── tests/                # Test suite
└── alembic/             # Database migrations
```

## Getting Started

### Prerequisites
- Python 3.13
- PostgreSQL
- Poetry (Python package manager)

## Security

- All rights reserved. No license is granted to use, copy, or distribute this work.
- User data is protected with secure authentication
- GDPR-compliant cookie management
- Secure session handling
- CSRF protection

## Contributing

This is a private project. All rights reserved. No contributions are accepted.

## License

All rights reserved. No license is granted to use, copy, or distribute this work.

## Contact

For inquiries about using this work, please contact the copyright holder.
