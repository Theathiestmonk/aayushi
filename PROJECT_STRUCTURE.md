# AI Dietitian Agent System - Project Structure

## 🏗️ Overall Architecture

```
ayushi/
├── frontend/          # React + Vite app (Vercel deployment)
├── backend/           # Python FastAPI app (Render deployment)
├── database/          # SQL schema files (Supabase deployment)
├── README.md          # Project overview
├── DEPLOYMENT.md      # Deployment instructions
└── PROJECT_STRUCTURE.md # This file
```

## 🎨 Frontend Structure (React + Vite)

```
frontend/
├── public/                    # Static assets
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── ui/              # Basic UI components
│   │   ├── Layout.tsx       # Main layout wrapper
│   │   ├── Navigation.tsx   # Navigation component
│   │   └── ...              # Other components
│   ├── pages/               # Page components
│   │   ├── Dashboard.tsx    # Main dashboard
│   │   ├── Onboarding.tsx   # Client onboarding form
│   │   ├── DietPlans.tsx    # Diet plan management
│   │   ├── Tracking.tsx     # Progress tracking
│   │   ├── Profile.tsx      # User profile
│   │   ├── Login.tsx        # Authentication
│   │   └── Register.tsx     # User registration
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API service functions
│   ├── stores/              # State management (Zustand)
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # App entry point
│   └── index.css            # Global styles
├── package.json              # Dependencies and scripts
├── vite.config.ts            # Vite configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
└── vercel.json               # Vercel deployment config
```

## 🔧 Backend Structure (Python FastAPI)

```
backend/
├── app/
│   ├── agents/               # Multi-agent system
│   │   ├── base_agent.py    # Base agent class
│   │   ├── agent_manager.py # Agent orchestration
│   │   ├── diet_planner_agent.py      # Diet planning
│   │   ├── follow_up_agent.py         # User follow-ups
│   │   ├── tracker_agent.py           # Progress tracking
│   │   ├── recommender_agent.py       # AI recommendations
│   │   ├── workout_planner_agent.py   # Exercise planning
│   │   ├── data_analyzer_agent.py     # Data analysis
│   │   ├── grocery_list_agent.py      # Shopping lists
│   │   ├── recipe_generator_agent.py  # Recipe creation
│   │   └── grocery_ordering_agent.py  # Order management
│   ├── api/                  # API endpoints
│   │   └── v1/              # API version 1
│   │       ├── api.py       # Main router
│   │       └── endpoints/   # Endpoint modules
│   │           ├── auth.py      # Authentication
│   │           ├── users.py     # User management
│   │           ├── diet_plans.py # Diet plan CRUD
│   │           ├── agents.py    # Agent interactions
│   │           └── tracking.py  # Progress tracking
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Configuration settings
│   │   ├── database.py       # Database connection
│   │   ├── security.py       # Authentication & security
│   │   └── dependencies.py   # Dependency injection
│   ├── models/               # Data models
│   │   ├── user.py           # User model
│   │   ├── diet_plan.py      # Diet plan model
│   │   └── ...               # Other models
│   ├── schemas/              # Pydantic schemas
│   │   ├── user.py           # User schemas
│   │   ├── diet_plan.py      # Diet plan schemas
│   │   └── ...               # Other schemas
│   ├── services/             # Business logic
│   │   ├── user_service.py   # User operations
│   │   ├── diet_service.py   # Diet plan operations
│   │   └── ...               # Other services
│   └── utils/                # Utility functions
├── main.py                   # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                # Container configuration
├── .env.example              # Environment variables template
└── env.example               # Environment variables template
```

## 🗄️ Database Structure (Supabase)

```
database/
├── schema.sql                # Complete database schema
├── migrations/               # Database migrations (future)
├── seeds/                    # Sample data (future)
└── functions/                # Database functions (future)
```

## 🤖 Multi-Agent System Architecture

### Agent Hierarchy
```
AgentManager (LangGraph Orchestrator)
├── DietPlannerAgent
├── FollowUpAgent
├── TrackerAgent
├── RecommenderAgent
├── WorkoutPlannerAgent
├── DataAnalyzerAgent
├── GroceryListAgent
├── RecipeGeneratorAgent
└── GroceryOrderingAgent
```

### Agent Responsibilities

#### 1. Diet Planner Agent
- **Input**: User profile, health goals, preferences
- **Process**: AI-powered diet plan creation
- **Output**: Personalized 7-day meal plan
- **Tools**: OpenAI GPT-4, nutritional databases

#### 2. Follow-up Agent
- **Input**: User responses, meal photos, progress updates
- **Process**: Engagement monitoring, reminders
- **Output**: Personalized follow-up messages
- **Tools**: Natural language processing, scheduling

#### 3. Tracker Agent
- **Input**: User meal logs, workout data, photos
- **Process**: Compliance analysis, progress tracking
- **Output**: Adherence scores, progress reports
- **Tools**: Image recognition, data analytics

#### 4. Recommender Agent
- **Input**: Tracking data, deviation patterns
- **Process**: AI analysis of user behavior
- **Output**: Personalized recommendations
- **Tools**: Machine learning, pattern recognition

#### 5. Workout Planner Agent
- **Input**: User profile, fitness goals, diet plan
- **Process**: Exercise routine creation
- **Output**: Personalized workout schedule
- **Tools**: Fitness databases, AI planning

#### 6. Data Analyzer Agent
- **Input**: Weekly tracking data, progress metrics
- **Process**: Statistical analysis, trend identification
- **Output**: Insights, improvement suggestions
- **Tools**: Data science libraries, visualization

#### 7. Grocery List Agent
- **Input**: Diet plan, user preferences, budget
- **Process**: Shopping list generation
- **Output**: Organized grocery lists
- **Tools**: Recipe analysis, cost optimization

#### 8. Recipe Generator Agent
- **Input**: Diet plan, ingredients, preferences
- **Process**: AI recipe creation
- **Output**: Custom recipes with instructions
- **Tools**: Culinary AI, nutritional calculation

#### 9. Grocery Ordering Agent
- **Input**: Grocery list, delivery preferences
- **Process**: Order placement automation
- **Output**: Order confirmations, tracking
- **Tools**: Delivery service APIs, payment processing

## 🔄 Data Flow

### Client Onboarding Flow
```
User Input → Onboarding Form → Backend API → Agent Manager → Diet Planner Agent → Workout Planner Agent → Grocery List Agent → Recipe Generator Agent → Database Storage
```

### Daily Tracking Flow
```
User Activity → Tracker Agent → Follow-up Agent → Recommender Agent → Database Storage → Data Analyzer Agent (Weekly)
```

### Weekly Analysis Flow
```
Weekly Data → Data Analyzer Agent → Diet Planner Agent → Workout Planner Agent → Updated Plans → Database Storage
```

## 🛡️ Security Architecture

### Authentication & Authorization
- JWT tokens for API access
- Role-based access control
- Secure password hashing
- Session management

### Data Protection
- End-to-end encryption
- HIPAA compliance measures
- Data anonymization
- Secure API endpoints

### Privacy Controls
- User consent management
- Data retention policies
- GDPR compliance
- Audit logging

## 📊 Monitoring & Observability

### Application Monitoring
- Health check endpoints
- Performance metrics
- Error tracking
- User analytics

### Agent Monitoring
- Agent performance metrics
- Success/failure rates
- Processing times
- Resource usage

### Database Monitoring
- Query performance
- Connection pooling
- Storage usage
- Backup status

## 🚀 Deployment Architecture

### Frontend (Vercel)
- Global CDN distribution
- Automatic deployments
- Preview deployments
- Edge functions support

### Backend (Render)
- Auto-scaling containers
- Health monitoring
- Load balancing
- SSL termination

### Database (Supabase)
- Managed PostgreSQL
- Real-time subscriptions
- Row-level security
- Automated backups

## 🔧 Development Workflow

### Local Development
1. Clone repository
2. Set up environment variables
3. Start backend server
4. Start frontend dev server
5. Connect to local/remote database

### Testing Strategy
- Unit tests for agents
- Integration tests for APIs
- E2E tests for user flows
- Performance testing

### CI/CD Pipeline
- Automated testing
- Code quality checks
- Security scanning
- Automated deployment

## 📈 Scalability Considerations

### Horizontal Scaling
- Multiple backend instances
- Database read replicas
- CDN for static assets
- Load balancers

### Performance Optimization
- Caching strategies
- Database indexing
- API response optimization
- Image compression

### Cost Optimization
- Resource monitoring
- Usage-based scaling
- Efficient algorithms
- Data compression

---

This structure provides a solid foundation for building and scaling the AI Dietitian Agent System while maintaining modularity, security, and performance.





