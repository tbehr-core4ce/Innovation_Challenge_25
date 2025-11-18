# BETS Architecture Diagram

## System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        USER[User Browser]
    end

    subgraph "Frontend Layer - Next.js 15.5.4"
        NEXTJS[Next.js App Router<br/>Port 3000]

        subgraph "Pages"
            DASHBOARD[Dashboard Page<br/>/dashboard]
            MAP[Map Page<br/>/map]
            SETTINGS[Settings Page<br/>/settings]
        end

        subgraph "Components"
            MAPVIS[BETSMapVisualization<br/>Leaflet + Clustering]
            CHARTS[Charts Components<br/>Recharts]
            CARDS[Metric Cards<br/>Stats Display]
        end

        subgraph "Services"
            APISERVICE[betsApi Service<br/>HTTP Client]
        end

        subgraph "Frontend Features"
            AUTH[NextAuth 5.0<br/>Authentication]
            VALIDATION[Zod Schema<br/>Validation]
        end
    end

    subgraph "Backend Layer - FastAPI"
        FASTAPI[FastAPI App<br/>Port 8000]

        subgraph "API Routes"
            R_DASHBOARD[/api/dashboard/*<br/>Aggregations]
            R_MAP[/api/map-data<br/>Cases + Hotspots]
            R_ALERTS[/api/alerts/*<br/>Alert System]
            R_INGEST[/api/data-ingestion/*<br/>CSV Upload]
            R_ANALYTICS[/api/analytics/*<br/>Analysis]
        end

        subgraph "Services & Business Logic"
            S_HOTSPOT[Hotspot Detection<br/>PostGIS KMeans]
            S_ALERT[Alert Generation<br/>Rule Engine]
            S_GEO[Geocoding Service<br/>County → Lat/Long]
            S_TRANSFORM[Data Transformers]
        end

        subgraph "Data Parsers"
            P_COMMERCIAL[Commercial Poultry<br/>Parser]
            P_WILD[Wild Bird<br/>Parser]
            P_MAMMAL[Mammal<br/>Parser]
            P_BASE[Base Parser<br/>Template]
        end

        subgraph "Validators"
            V_SCHEMA[Schema Validator<br/>Enums + Rules]
            V_DATA[Data Validator<br/>Business Logic]
        end

        subgraph "ORM Layer"
            ORM[SQLAlchemy 2.0<br/>Models + Sessions]
            MODELS[Models:<br/>H5N1Case, Alert,<br/>DataImport, User]
        end
    end

    subgraph "Data Layer - PostgreSQL 18 + PostGIS 3.6"
        DB[(PostgreSQL Database<br/>Port 5432)]

        subgraph "Tables"
            T_CASES[h5n1_cases<br/>40,000+ records<br/>GEOMETRY column]
            T_ALERTS[alerts<br/>Alert tracking]
            T_IMPORTS[data_imports<br/>Import history]
            T_USERS[users<br/>Authentication]
        end

        subgraph "PostGIS Features"
            SPATIAL[ST_ClusterKMeans<br/>Spatial Queries<br/>GIST Indexes]
        end
    end

    subgraph "Data Sources"
        CSV_COMMERCIAL[Commercial Poultry CSV<br/>~200 records]
        CSV_WILD[Wild Birds CSV<br/>~40,000 records]
        CSV_MAMMAL[Mammals CSV<br/>~150 records]
    end

    subgraph "External Services"
        AZURE[Azure AD<br/>Optional SSO]
        WOAH[WOAH API<br/>Future]
        CDC[CDC API<br/>Future]
        USDA[USDA API<br/>Future]
    end

    %% User interactions
    USER -->|HTTPS| NEXTJS

    %% Frontend routing
    NEXTJS --> DASHBOARD
    NEXTJS --> MAP
    NEXTJS --> SETTINGS

    %% Component usage
    DASHBOARD --> CHARTS
    DASHBOARD --> CARDS
    MAP --> MAPVIS

    %% API calls
    DASHBOARD -->|API Calls| APISERVICE
    MAP -->|API Calls| APISERVICE
    APISERVICE -->|HTTP REST| FASTAPI

    %% Authentication
    AUTH -.->|OAuth| AZURE

    %% Backend routing
    FASTAPI --> R_DASHBOARD
    FASTAPI --> R_MAP
    FASTAPI --> R_ALERTS
    FASTAPI --> R_INGEST
    FASTAPI --> R_ANALYTICS

    %% Service layer
    R_DASHBOARD --> S_TRANSFORM
    R_MAP --> S_HOTSPOT
    R_MAP --> S_TRANSFORM
    R_ALERTS --> S_ALERT
    R_INGEST --> P_COMMERCIAL
    R_INGEST --> P_WILD
    R_INGEST --> P_MAMMAL

    %% Parser flow
    P_COMMERCIAL --> P_BASE
    P_WILD --> P_BASE
    P_MAMMAL --> P_BASE
    P_BASE --> S_GEO
    P_BASE --> V_SCHEMA
    P_BASE --> V_DATA

    %% ORM usage
    S_HOTSPOT --> ORM
    S_ALERT --> ORM
    S_TRANSFORM --> ORM
    V_DATA --> ORM
    ORM --> MODELS

    %% Database connections
    MODELS -->|psycopg3| DB

    %% Table relationships
    DB --> T_CASES
    DB --> T_ALERTS
    DB --> T_IMPORTS
    DB --> T_USERS
    T_CASES -.->|Uses| SPATIAL

    %% Data ingestion
    CSV_COMMERCIAL -->|Upload| R_INGEST
    CSV_WILD -->|Upload| R_INGEST
    CSV_MAMMAL -->|Upload| R_INGEST

    %% External API connections (future)
    R_INGEST -.->|Future| WOAH
    R_INGEST -.->|Future| CDC
    R_INGEST -.->|Future| USDA

    %% Styling
    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px,color:#000
    classDef backend fill:#009688,stroke:#333,stroke-width:2px,color:#fff
    classDef database fill:#336791,stroke:#333,stroke-width:2px,color:#fff
    classDef external fill:#ff9800,stroke:#333,stroke-width:2px,color:#000
    classDef data fill:#4caf50,stroke:#333,stroke-width:2px,color:#fff

    class NEXTJS,DASHBOARD,MAP,SETTINGS,MAPVIS,CHARTS,CARDS,APISERVICE,AUTH,VALIDATION frontend
    class FASTAPI,R_DASHBOARD,R_MAP,R_ALERTS,R_INGEST,R_ANALYTICS,S_HOTSPOT,S_ALERT,S_GEO,S_TRANSFORM,P_COMMERCIAL,P_WILD,P_MAMMAL,P_BASE,V_SCHEMA,V_DATA,ORM,MODELS backend
    class DB,T_CASES,T_ALERTS,T_IMPORTS,T_USERS,SPATIAL database
    class AZURE,WOAH,CDC,USDA external
    class CSV_COMMERCIAL,CSV_WILD,CSV_MAMMAL data
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant U as User Browser
    participant FE as Next.js Frontend
    participant API as FastAPI Backend
    participant SVC as Service Layer
    participant DB as PostgreSQL + PostGIS

    Note over U,DB: Typical Map View Request Flow

    U->>FE: Navigate to /map
    FE->>FE: Load BETSMapVisualization
    FE->>API: GET /api/map-data?days=7&category=all

    API->>SVC: Process map data request
    SVC->>DB: Query h5n1_cases<br/>(filtered by date, category)
    DB-->>SVC: Return case records

    SVC->>DB: Execute ST_ClusterKMeans<br/>(hotspot detection)
    DB-->>SVC: Return cluster data

    SVC->>SVC: Calculate risk levels<br/>Transform to GeoJSON
    SVC-->>API: Return formatted data
    API-->>FE: JSON response:<br/>cases + hotspots

    FE->>FE: Render Leaflet map<br/>with markers & zones
    FE-->>U: Display interactive map

    Note over U,DB: Alert Generation Flow

    SVC->>DB: Monitor new cases<br/>(background process)
    DB-->>SVC: New critical case detected

    SVC->>SVC: Evaluate alert rules:<br/>- Severity check<br/>- Geographic clustering<br/>- Outbreak size

    SVC->>DB: INSERT INTO alerts
    DB-->>SVC: Alert created

    U->>FE: Check dashboard
    FE->>API: GET /api/alerts?active=true
    API->>DB: Query active alerts
    DB-->>API: Return alerts
    API-->>FE: Alert list
    FE-->>U: Display alert badges
```

## Data Ingestion Pipeline

```mermaid
flowchart TD
    START([CSV File Upload]) --> DETECT{Detect<br/>Dataset Type}

    DETECT -->|Commercial| P1[CommercialPoultryParser]
    DETECT -->|Wild Birds| P2[WildBirdParser]
    DETECT -->|Mammals| P3[MammalParser]

    P1 --> PARSE[Parse CSV to DataFrame<br/>Pandas]
    P2 --> PARSE
    P3 --> PARSE

    PARSE --> GEOCODE[Geocoding Service<br/>County + State → Lat/Long]

    GEOCODE --> VALIDATE{Schema Validation}

    VALIDATE -->|Invalid| ERROR[Log Errors<br/>Return Failed Rows]
    VALIDATE -->|Valid| DEDUPE[Duplicate Detection<br/>File Hash + external_id]

    DEDUPE --> CHECK{Already<br/>Imported?}

    CHECK -->|Yes| SKIP[Skip Record]
    CHECK -->|No| TRANSFORM[Transform to H5N1Case Model]

    TRANSFORM --> BULK[Bulk Insert<br/>1000 records/batch]

    BULK --> DBINSERT[(Insert into<br/>h5n1_cases)]

    DBINSERT --> TRACK[Update data_imports<br/>tracking table]

    TRACK --> COMPLETE([Import Complete])

    SKIP --> TRACK
    ERROR --> TRACK

    style START fill:#4caf50,color:#fff
    style COMPLETE fill:#4caf50,color:#fff
    style ERROR fill:#f44336,color:#fff
    style DBINSERT fill:#336791,color:#fff
```

## Technology Stack

```mermaid
graph LR
    subgraph "Frontend Stack"
        FE1[Next.js 15.5.4]
        FE2[React 19]
        FE3[TypeScript 5.8]
        FE4[Tailwind CSS 3.4]
        FE5[Material-UI 7.3]
        FE6[Leaflet 1.9]
        FE7[Recharts 2.15]
        FE8[NextAuth 5.0]
    end

    subgraph "Backend Stack"
        BE1[FastAPI 0.115+]
        BE2[Python 3.12]
        BE3[SQLAlchemy 2.0]
        BE4[Alembic 1.17]
        BE5[Pydantic 2.11]
        BE6[Structlog 25.5]
        BE7[Pandas 2.3]
    end

    subgraph "Database Stack"
        DB1[PostgreSQL 18]
        DB2[PostGIS 3.6]
        DB3[psycopg3]
    end

    subgraph "DevOps"
        DO1[Docker Compose]
        DO2[Poetry]
        DO3[pnpm]
        DO4[Makefile]
    end

    style FE1 fill:#61dafb,color:#000
    style BE1 fill:#009688,color:#fff
    style DB1 fill:#336791,color:#fff
    style DO1 fill:#2496ed,color:#fff
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Docker Compose Environment"
        subgraph "Container: Frontend"
            C_FE[Next.js Server<br/>Port: 3000<br/>Health: /api/health]
        end

        subgraph "Container: Backend"
            C_BE[FastAPI + Uvicorn<br/>Port: 8000<br/>Workers: 4<br/>Health: /health]
        end

        subgraph "Container: Database"
            C_DB[PostgreSQL 18<br/>PostGIS 3.6<br/>Port: 5432<br/>Volume: pgdata]
        end

        subgraph "Volumes"
            V_DB[(pgdata<br/>Persistent Storage)]
            V_LOGS[(logs<br/>Application Logs)]
        end

        subgraph "Networks"
            NET[bets-network<br/>Bridge Network]
        end
    end

    subgraph "External Access"
        LB[Load Balancer<br/>HTTPS]
    end

    LB -->|Port 443| C_FE
    C_FE -->|API Proxy| C_BE
    C_BE -->|SQL| C_DB
    C_DB -->|Mount| V_DB
    C_BE -->|Mount| V_LOGS
    C_FE -->|Mount| V_LOGS

    C_FE -.-|Network| NET
    C_BE -.-|Network| NET
    C_DB -.-|Network| NET

    style C_FE fill:#61dafb,color:#000
    style C_BE fill:#009688,color:#fff
    style C_DB fill:#336791,color:#fff
    style V_DB fill:#ffc107,color:#000
    style V_LOGS fill:#ffc107,color:#000
    style NET fill:#e0e0e0,color:#000
```

## Database Schema

```mermaid
erDiagram
    h5n1_cases ||--o{ alerts : triggers
    h5n1_cases {
        int id PK
        varchar external_id UK
        timestamp case_date
        timestamp report_date
        enum status
        enum severity
        enum animal_category
        varchar animal_species
        int animals_affected
        int animals_dead
        varchar country
        varchar state_province
        varchar county
        varchar city
        varchar location_name
        geometry location
        float latitude
        float longitude
        enum data_source
        text source_url
        text description
        text control_measures
        json extra_metadata
        timestamp created_at
        timestamp updated_at
        varchar created_by
        varchar updated_by
        boolean is_deleted
        timestamp deleted_at
    }

    alerts {
        int id PK
        enum alert_type
        varchar title
        text description
        enum severity
        int case_id FK
        varchar country
        varchar state_province
        boolean is_active
        boolean acknowledged
        timestamp acknowledged_at
        varchar acknowledged_by
        timestamp created_at
    }

    data_imports {
        int id PK
        enum source
        varchar filename
        varchar file_hash UK
        int total_rows
        int successful_rows
        int failed_rows
        int duplicate_rows
        varchar status
        text error_log
        timestamp started_at
        timestamp completed_at
        float duration_seconds
        varchar imported_by
        timestamp created_at
    }

    users {
        int id PK
        varchar email UK
        varchar username UK
        varchar hashed_password
        varchar full_name
        varchar organization
        varchar role
        boolean is_active
        boolean is_superuser
        timestamp last_login
        int failed_login_attempts
        timestamp locked_until
        timestamp created_at
        timestamp updated_at
    }

    users ||--o{ data_imports : performs
    users ||--o{ alerts : acknowledges
```

## Component Interaction Map

```mermaid
graph TB
    subgraph "User Actions"
        A1[View Dashboard]
        A2[Explore Map]
        A3[Upload CSV]
        A4[View Alerts]
    end

    subgraph "Frontend Components"
        FC1[BETSDashboard]
        FC2[BETSMapVisualization]
        FC3[DataIngestionForm]
        FC4[AlertList]
    end

    subgraph "API Endpoints"
        EP1[GET /api/dashboard/stats]
        EP2[GET /api/dashboard/trends]
        EP3[GET /api/map-data]
        EP4[GET /api/hotspots]
        EP5[POST /api/data-ingestion/upload]
        EP6[GET /api/alerts]
    end

    subgraph "Backend Services"
        BS1[Dashboard Aggregator]
        BS2[Hotspot Detector]
        BS3[Alert Generator]
        BS4[Data Loader]
    end

    subgraph "Database Queries"
        Q1[Aggregate by Category]
        Q2[Time Series by Month]
        Q3[Spatial Query Cases]
        Q4[ST_ClusterKMeans]
        Q5[Bulk Insert Cases]
        Q6[Query Active Alerts]
    end

    A1 --> FC1
    A2 --> FC2
    A3 --> FC3
    A4 --> FC4

    FC1 --> EP1
    FC1 --> EP2
    FC2 --> EP3
    FC2 --> EP4
    FC3 --> EP5
    FC4 --> EP6

    EP1 --> BS1
    EP2 --> BS1
    EP3 --> BS2
    EP4 --> BS2
    EP5 --> BS4
    EP6 --> BS3

    BS1 --> Q1
    BS1 --> Q2
    BS2 --> Q3
    BS2 --> Q4
    BS4 --> Q5
    BS3 --> Q6

    style A1 fill:#bbdefb,color:#000
    style A2 fill:#bbdefb,color:#000
    style A3 fill:#bbdefb,color:#000
    style A4 fill:#bbdefb,color:#000
    style FC1 fill:#61dafb,color:#000
    style FC2 fill:#61dafb,color:#000
    style FC3 fill:#61dafb,color:#000
    style FC4 fill:#61dafb,color:#000
    style EP1 fill:#009688,color:#fff
    style EP2 fill:#009688,color:#fff
    style EP3 fill:#009688,color:#fff
    style EP4 fill:#009688,color:#fff
    style EP5 fill:#009688,color:#fff
    style EP6 fill:#009688,color:#fff
    style BS1 fill:#00796b,color:#fff
    style BS2 fill:#00796b,color:#fff
    style BS3 fill:#00796b,color:#fff
    style BS4 fill:#00796b,color:#fff
    style Q1 fill:#336791,color:#fff
    style Q2 fill:#336791,color:#fff
    style Q3 fill:#336791,color:#fff
    style Q4 fill:#336791,color:#fff
    style Q5 fill:#336791,color:#fff
    style Q6 fill:#336791,color:#fff
```

## Alert System Architecture

```mermaid
stateDiagram-v2
    [*] --> Monitoring: System Active

    Monitoring --> Detecting: New Case Inserted

    Detecting --> Evaluating: Case Data Retrieved

    state Evaluating {
        [*] --> CheckSeverity
        CheckSeverity --> CheckClustering: Severity >= High
        CheckClustering --> CheckOutbreakSize: Geographic Check
        CheckOutbreakSize --> CheckCrossSpecies: Count Animals
        CheckCrossSpecies --> [*]: Evaluate All Rules
    }

    Evaluating --> CreateAlert: Rule Triggered
    Evaluating --> Monitoring: No Alert Needed

    CreateAlert --> Active: Alert Stored in DB

    Active --> Acknowledged: User Acknowledges
    Active --> Expired: Time Limit Reached

    Acknowledged --> Archived: Store Historical Data
    Expired --> Archived: Store Historical Data

    Archived --> [*]: Alert Completed

    Monitoring --> Monitoring: Continuous Loop

    note right of Evaluating
        Alert Rules:
        - Critical Severity
        - 3+ Cases in County (7 days)
        - 10,000+ Animals Affected
        - Cross-Species Detection
        - Geographic Spread Rate
    end note

    note right of Active
        Alert contains:
        - Type
        - Severity
        - Location
        - Case Reference
        - Timestamp
    end note
```

---

## Key Features Summary

### 1. Real-Time Monitoring
- Dashboard with live statistics
- Time series trend analysis
- Geographic distribution tracking

### 2. Spatial Analysis
- Interactive map with Leaflet
- PostGIS-powered hotspot detection
- Cluster visualization with risk zones
- County-level aggregation

### 3. Data Management
- Multi-source CSV ingestion
- Automated geocoding
- Duplicate detection
- Import tracking and auditing

### 4. Alert System
- Rule-based alert generation
- Severity escalation
- Geographic clustering detection
- User acknowledgment workflow

### 5. Security & Access
- NextAuth 5.0 ready
- Role-based access control
- Azure AD integration support
- Audit trails

---

## Performance Considerations

### Database Optimization
- GIST spatial indexes for geographic queries
- Composite indexes on frequently filtered columns
- Connection pooling (SQLAlchemy)
- Bulk insert operations (1000 records/batch)

### Frontend Optimization
- Next.js SSR for initial page loads
- React 19 concurrent features
- Leaflet marker clustering (reduces DOM nodes)
- Lazy loading for large datasets

### Backend Optimization
- FastAPI async endpoints
- Uvicorn with multiple workers
- Structlog for efficient logging
- Pydantic for fast validation

---

## Development Workflow

```mermaid
gitGraph
    commit id: "Initial setup"
    branch feature/dashboard
    checkout feature/dashboard
    commit id: "Add dashboard components"
    commit id: "Integrate charts"
    checkout main
    merge feature/dashboard

    branch feature/map
    checkout feature/map
    commit id: "Add Leaflet integration"
    commit id: "Implement hotspot detection"
    checkout main
    merge feature/map

    branch feature/alerts
    checkout feature/alerts
    commit id: "Create alert system"
    commit id: "Add notification UI"
    checkout main
    merge feature/alerts

    commit id: "Release v1.0"
```

---

## Monitoring & Logging

### Structured Logging (Structlog)
- Request/response logging
- Database query logging
- Error tracking with stack traces
- Performance metrics

### Health Checks
- Frontend: `GET /api/health`
- Backend: `GET /health`
- Database: Connection pool status

### Metrics Tracked
- API response times
- Database query performance
- Data import success rates
- Alert generation frequency
- User authentication events

---

## Security Architecture

```mermaid
graph TD
    subgraph "Security Layers"
        L1[Transport Layer<br/>HTTPS/TLS]
        L2[Authentication Layer<br/>NextAuth + JWT]
        L3[Authorization Layer<br/>Role-Based Access]
        L4[Data Layer<br/>Encrypted at Rest]
        L5[Audit Layer<br/>Logging & Tracking]
    end

    USER[User Request] --> L1
    L1 --> L2
    L2 --> L3
    L3 --> APP[Application Logic]
    APP --> L4
    L4 --> DATABASE[(Database)]

    L2 -.-> L5
    L3 -.-> L5
    APP -.-> L5
    L4 -.-> L5

    style L1 fill:#f44336,color:#fff
    style L2 fill:#ff9800,color:#fff
    style L3 fill:#ffc107,color:#000
    style L4 fill:#4caf50,color:#fff
    style L5 fill:#2196f3,color:#fff
```

---

## Future Enhancements

### Planned Features
1. **Real-Time Updates**: WebSocket integration for live dashboard
2. **Mobile App**: React Native mobile application
3. **Advanced Analytics**: ML-based outbreak prediction
4. **Export Functionality**: PDF reports, Excel exports
5. **Public API**: RESTful API for external integrations
6. **Notification System**: Email/SMS alerts
7. **Dark Mode**: Theme switching support
8. **Multi-Language**: i18n internationalization

### Scalability Roadmap
- Redis caching layer
- Load balancer (Nginx/Traefik)
- Database read replicas
- CDN for static assets
- Kubernetes deployment
- Microservices architecture (if needed)

---

*This architecture documentation was generated for the BETS (Bio-Event Tracking System) project.*
*Last updated: 2025-11-18*
