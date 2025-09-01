# AI Dietitian Agent System

A comprehensive multi-agent AI system for personalized diet planning, tracking, and recommendations.

## 🏗️ Architecture

This system consists of three main components:
- **Frontend**: React + Vite application deployed on Vercel
- **Backend**: Python FastAPI application deployed on Render
- **Database**: PostgreSQL with Supabase

## 🤖 Multi-Agent System

The AI dietitian agent system includes the following specialized agents:

1. **Diet Planner Agent**: Creates personalized 7-day diet plans with structured meals (Breakfast, Snack, Lunch, Snack, Dinner)
2. **Follow-up Agent**: Monitors user adherence and engagement
3. **Tracker Agent**: Tracks eating and workout compliance
4. **Recommender Agent**: Suggests adjustments based on deviations
5. **Workout Planner Agent**: Plans exercise routines
6. **Data Analyzer Agent**: Analyzes weekly progress and suggests improvements
7. **Grocery List Generator Agent**: Creates shopping lists from diet plans
8. **Recipe Generator Agent**: Generates recipes for planned meals
9. **Grocery Ordering Agent**: Integrates with delivery services

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account
- OpenAI API key

### Setup
1. Clone the repository
2. Set up environment variables
3. Install dependencies for each component
4. Deploy to respective platforms

## 📁 Project Structure

```
ayushi/
├── frontend/          # React + Vite app (Vercel)
├── backend/           # Python FastAPI app (Render)
├── database/          # SQL schema files (Supabase)
└── README.md
```

## 🔧 Technologies Used

- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS
- **Backend**: Python 3.11, FastAPI, LangGraph, OpenAI
- **Database**: PostgreSQL, Supabase
- **AI/ML**: LangGraph, OpenAI GPT-4, LangChain
- **Deployment**: Vercel, Render, Supabase

## 📋 Features

- Client onboarding and profile management
- AI-powered 7-day diet planning with structured meal schedules
- Real-time tracking and monitoring
- Automated follow-ups and reminders
- Recipe generation and meal planning
- Grocery list management and ordering
- Workout planning and tracking
- Data analysis and progress insights

## 🔐 Security & Privacy

- End-to-end encryption for sensitive data
- HIPAA-compliant data handling
- Secure API authentication
- Data anonymization and privacy protection
- Regular security audits and updates

