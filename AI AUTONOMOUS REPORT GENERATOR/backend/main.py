# ============================================================================
# AUTONOMOUS REPORT GENERATOR - BACKEND API WITH MONGODB
# Framework: FastAPI (Python)
# Database: MongoDB Atlas
# Features: JWT Auth, AI Analysis, Report Generation, NLP Queries, Alerts
# ============================================================================

# import os
# from typing import Optional, List, Dict, Any
# from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, BackgroundTasks, Request, Form
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, EmailStr, Field
# from datetime import datetime, timedelta
# from passlib.context import CryptContext
# import jwt
# import json
# from enum import Enum
# import pandas as pd
# from io import StringIO
# import uuid
# import io
# import base64
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib import colors
# from reportlab.lib.units import inch
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# import tempfile
# import logging

# # AI Agents
# from ai_models.llama_agent import get_llama_agent
# from ai_models.analysis_agent import get_analysis_agent

# # MongoDB
# from motor.motor_asyncio import AsyncIOMotorClient
# from bson import ObjectId
# from pymongo import ReturnDocument
# from fastapi.responses import JSONResponse

# # ============================================================================
# # LOGGING CONFIGURATION
# # ============================================================================

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # ============================================================================
# # LIFESPAN & APP INITIALIZATION
# # ============================================================================

# from contextlib import asynccontextmanager
# from dotenv import load_dotenv

# load_dotenv()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup: Initialize MongoDB connection
#     print("✅ Initializing Backend API with MongoDB...")
    
#     # Initialize MongoDB connection
#     app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
#     app.mongodb = app.mongodb_client[os.getenv("MONGODB_DB_NAME", "report_generator")]
    
#     # Create indexes
#     await create_indexes(app.mongodb)
    
#     # Create default admin user if not exists
#     admin_user = await app.mongodb.users.find_one({"email": "admin@company.com"})
#     if not admin_user:
#         admin_id = str(uuid.uuid4())
#         admin_user = {
#             "id": admin_id,
#             "email": "admin@company.com",
#             "password": get_password_hash("admin123"),
#             "name": "Admin User",
#             "role": UserRole.ADMIN,
#             "departments": [Department.FINANCE, Department.HR, Department.SALES, 
#                            Department.OPERATIONS, Department.COMPLIANCE],
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow()
#         }
#         await app.mongodb.users.insert_one(admin_user)
#         print("📧 Default admin created: admin@company.com / admin123")
    
#     # Create sample alerts if none exist
#     alerts_count = await app.mongodb.alerts.count_documents({})
#     if alerts_count == 0:
#         sample_alerts = []
#         for i in range(4):
#             alert_id = str(uuid.uuid4())
#             sample_alerts.append({
#                 "id": alert_id,
#                 "type": ["warning", "info", "success"][i % 3],
#                 "department": [Department.FINANCE, Department.HR, Department.SALES, Department.OPERATIONS][i],
#                 "message": f"Sample alert message {i+1}",
#                 "priority": [AlertPriority.HIGH, AlertPriority.MEDIUM, AlertPriority.LOW][i % 3],
#                 "created_at": datetime.utcnow(),
#                 "acknowledged": False,
#                 "created_by": admin_id
#             })
#         await app.mongodb.alerts.insert_many(sample_alerts)
    
#     print("🚀 Server running at http://localhost:8000")
#     print("📚 API docs available at http://localhost:8000/docs")
    
#     yield  # Server is running
    
#     # Cleanup: Close MongoDB connection
#     print("Shutting down...")
#     app.mongodb_client.close()

# # Initialize FastAPI with lifespan
# app = FastAPI(
#     title="Autonomous Report Generator API",
#     description="Enterprise AI-powered reporting system with MongoDB",
#     version="1.0.0",
#     lifespan=lifespan
# )

# # ============================================================================
# # CORS CONFIGURATION
# # ============================================================================

# cors_origins = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173", 
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "http://localhost:8080",
#     "http://127.0.0.1:8080",
#     "*"  # For development only - remove in production
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=cors_origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
#     allow_headers=["*"],
#     expose_headers=["*"]
# )

# # ============================================================================
# # CORS EXCEPTION HANDLING MIDDLEWARE
# # ============================================================================

# @app.middleware("http")
# async def catch_exceptions_middleware(request: Request, call_next):
#     try:
#         response = await call_next(request)
        
#         # Ensure CORS headers are added to all responses
#         origin = request.headers.get('origin')
#         if origin and origin in cors_origins:
#             response.headers["Access-Control-Allow-Origin"] = origin
#         elif "*" in cors_origins:
#             response.headers["Access-Control-Allow-Origin"] = "*"
            
#         response.headers["Access-Control-Allow-Credentials"] = "true"
#         response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
#         response.headers["Access-Control-Allow-Headers"] = "*"
        
#         return response
        
#     except Exception as exc:
#         # Handle exceptions and still add CORS headers
#         import traceback
#         logger.error(f"Unhandled exception: {str(exc)}")
#         logger.error(traceback.format_exc())
        
#         # Use JSONResponse instead of Response
#         response = JSONResponse(
#             status_code=500,
#             content={"detail": "Internal server error", "error": str(exc)}
#         )
        
#         origin = request.headers.get('origin')
#         if origin and origin in cors_origins:
#             response.headers["Access-Control-Allow-Origin"] = origin
#         elif "*" in cors_origins:
#             response.headers["Access-Control-Allow-Origin"] = "*"
            
#         response.headers["Access-Control-Allow-Credentials"] = "true"
#         response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
#         response.headers["Access-Control-Allow-Headers"] = "*"
        
#         return response

# # ============================================================================
# # SECURITY CONFIGURATION
# # ============================================================================

# SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# security = HTTPBearer()

# # MongoDB Configuration
# MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
# DB_NAME = os.getenv("MONGODB_DB_NAME", "report_generator")

# # ============================================================================
# # ENUMS & CONSTANTS
# # ============================================================================

# class UserRole(str, Enum):
#     ADMIN = "admin"
#     MANAGER = "manager"
#     ANALYST = "analyst"
#     VIEWER = "viewer"

# class Department(str, Enum):
#     FINANCE = "finance"
#     HR = "hr"
#     SALES = "sales"
#     OPERATIONS = "operations"
#     COMPLIANCE = "compliance"

# class ReportType(str, Enum):
#     PDF = "pdf"
#     PPT = "ppt"
#     EXCEL = "excel"

# class ReportFrequency(str, Enum):
#     DAILY = "daily"
#     WEEKLY = "weekly"
#     MONTHLY = "monthly"

# class AlertPriority(str, Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"

# # ============================================================================
# # PYDANTIC MODELS
# # ============================================================================

# class UserRegister(BaseModel):
#     email: EmailStr
#     password: str
#     name: str
#     role: UserRole
#     departments: List[Department]

# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# class Token(BaseModel):
#     access_token: str
#     token_type: str
#     user: Dict[str, Any]

# class User(BaseModel):
#     id: str
#     email: EmailStr
#     name: str
#     role: UserRole
#     departments: List[Department]
#     created_at: datetime

# class ReportGenerate(BaseModel):
#     title: str
#     department: Department
#     report_type: ReportType
#     date_range: Dict[str, str]
#     frequency: Optional[ReportFrequency] = None
#     schedule: Optional[bool] = False

# class Report(BaseModel):
#     id: str
#     title: str
#     department: Department
#     report_type: ReportType
#     file_url: str
#     size: str
#     status: str
#     created_by: str
#     created_at: datetime

# class NLPQuery(BaseModel):
#     query: str
#     department: Optional[Department] = None
#     context: Optional[Dict[str, Any]] = None

# class QueryResponse(BaseModel):
#     query: str
#     answer: str
#     insights: List[str]
#     chart_data: Optional[List[Dict[str, Any]]] = None
#     recommendations: Optional[List[str]] = None

# class Alert(BaseModel):
#     id: str
#     type: str
#     department: Department
#     message: str
#     priority: AlertPriority
#     created_at: datetime
#     acknowledged: bool = False

# class CommentCreate(BaseModel):
#     report_id: str
#     content: str
#     mentioned_users: Optional[List[str]] = []

# class Comment(BaseModel):
#     id: str
#     report_id: str
#     user_id: str
#     user_name: str
#     content: str
#     mentioned_users: List[str]
#     created_at: datetime
#     replies: List[Dict[str, Any]] = []

# class UserSettings(BaseModel):
#     language: str = "english"
#     theme: str = "light"
#     report_format: ReportType = ReportType.PDF
#     notifications: Dict[str, bool] = {
#         "email": True,
#         "slack": False,
#         "teams": False
#     }

# class KPIData(BaseModel):
#     department: Department
#     kpis: List[Dict[str, Any]]
#     chart_data: List[Dict[str, Any]]
#     summary: str

# # ============================================================================
# # DATABASE UTILITIES
# # ============================================================================

# async def create_indexes(db):
#     """Create database indexes for better performance"""
#     # Users collection indexes
#     await db.users.create_index("email", unique=True)
#     await db.users.create_index("role")
#     await db.users.create_index("departments")
    
#     # Reports collection indexes
#     await db.reports.create_index("department")
#     await db.reports.create_index("created_by")
#     await db.reports.create_index("created_at")
#     await db.reports.create_index([("department", 1), ("created_at", -1)])
    
#     # Alerts collection indexes
#     await db.alerts.create_index("department")
#     await db.alerts.create_index("priority")
#     await db.alerts.create_index("acknowledged")
#     await db.alerts.create_index("created_at")
    
#     # Comments collection indexes
#     await db.comments.create_index("report_id")
#     await db.comments.create_index("user_id")
#     await db.comments.create_index("created_at")
    
#     # Activities collection indexes
#     await db.activities.create_index("user_id")
#     await db.activities.create_index("timestamp")
    
#     # New indexes for report files
#     await db.report_files.create_index("report_id", unique=True)
#     await db.report_files.create_index("created_at")
    
#     # New collection for data uploads
#     await db.data_uploads.create_index("uploaded_by")
#     await db.data_uploads.create_index("department")
#     await db.data_uploads.create_index("uploaded_at")
    
#     print("✅ Database indexes created")

# def serialize_doc(doc):
#     """Convert MongoDB document to JSON serializable format"""
#     if doc and '_id' in doc:
#         doc['id'] = str(doc['_id'])
#         del doc['_id']
#     return doc

# async def get_database():
#     """Dependency to get database instance"""
#     return app.mongodb

# # ============================================================================
# # AUTHENTICATION UTILITIES
# # ============================================================================

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)

# def create_access_token(data: dict) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def decode_token(token: str) -> dict:
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token has expired")
#     except jwt.JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db=Depends(get_database)
# ) -> dict:
#     token = credentials.credentials
#     payload = decode_token(token)
#     user_id = payload.get("sub")
    
#     user = await db.users.find_one({"id": user_id})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     return serialize_doc(user)

# def check_role(required_roles: List[UserRole]):
#     async def role_checker(current_user: dict = Depends(get_current_user)):
#         if current_user["role"] not in required_roles:
#             raise HTTPException(status_code=403, detail="Insufficient permissions")
#         return current_user
#     return role_checker

# # ============================================================================
# # AI INTEGRATION FUNCTIONS
# # ============================================================================

# def analyze_with_ai(query: str, data: Any) -> Dict[str, Any]:
#     """Mock AI analysis function"""
#     insights = [
#         "Sales performance increased by 22% compared to previous quarter",
#         "Technology sector showed strongest growth at 28%",
#         "Customer retention improved by 15% through loyalty programs"
#     ]
    
#     recommendations = [
#         "Increase marketing budget in high-performing regions by 12%",
#         "Focus on customer retention strategies in underperforming segments",
#         "Expand product line in technology sector based on demand trends"
#     ]
    
#     return {
#         "insights": insights,
#         "recommendations": recommendations,
#         "confidence": 0.92
#     }

# def detect_anomalies(data: pd.DataFrame) -> List[Dict[str, Any]]:
#     """Anomaly detection using ML"""
#     anomalies = []
#     if len(data) > 0:
#         anomalies.append({
#             "type": "spike",
#             "metric": "expenses",
#             "value": "+15%",
#             "severity": "medium",
#             "description": "Unusual increase in marketing expenses detected"
#         })
#     return anomalies

# def generate_executive_summary(department: Department, data: Dict) -> str:
#     """Generate AI-powered executive summary"""
#     summaries = {
#         Department.FINANCE: "Q2 financial performance exceeded expectations with 12.5% revenue growth. Operating margins improved to 25% through strategic cost optimization. Cash flow remains strong with $2.4M total revenue.",
#         Department.HR: "Workforce expansion on track with 23 new hires. Attrition rate decreased to 8.2%, below industry average. Employee satisfaction scores improved to 87% following new wellness initiatives.",
#         Department.SALES: "Outstanding quarter with 156 deals closed, representing 22% growth. Average deal size increased to $27K. Sales pipeline robust at $4.2M with 34% conversion rate.",
#         Department.OPERATIONS: "Operational efficiency reached 94% with significant reduction in equipment downtime. Order volume increased 18% while maintaining 96% on-time delivery rate.",
#         Department.COMPLIANCE: "All regulatory requirements met with 12 successful audits. Issue resolution rate at 89%. Risk assessment remains at Low level with proactive monitoring in place."
#     }
#     return summaries.get(department, "Performance metrics within expected parameters.")

# def process_nlp_query(query: str, department: Optional[Department]) -> Dict[str, Any]:
#     """Process natural language queries using AI"""
#     query_lower = query.lower()
    
#     if "sales" in query_lower or "revenue" in query_lower:
#         return {
#             "answer": "Sales performance for Q2 shows 22% growth with 156 deals closed. Revenue reached $2.4M with strong pipeline of $4.2M.",
#             "chart_data": [
#                 {"month": "Jan", "sales": 540},
#                 {"month": "Feb", "sales": 675},
#                 {"month": "Mar", "sales": 756},
#                 {"month": "Apr", "sales": 594},
#                 {"month": "May", "sales": 810},
#                 {"month": "Jun", "sales": 837}
#             ],
#             "insights": [
#                 "Technology sector led growth with 28% increase",
#                 "Average deal size increased from $25K to $27K",
#                 "Conversion rate improved to 34%"
#             ],
#             "recommendations": [
#                 "Invest in high-performing sales channels",
#                 "Expand sales team in technology vertical"
#             ]
#         }
#     elif "hr" in query_lower or "employee" in query_lower or "attrition" in query_lower:
#         return {
#             "answer": "HR metrics show positive trends with attrition decreasing to 8.2% and employee satisfaction at 87%.",
#             "chart_data": [
#                 {"month": "Jan", "hires": 5, "exits": 3},
#                 {"month": "Feb", "hires": 8, "exits": 2},
#                 {"month": "Mar", "hires": 6, "exits": 4},
#                 {"month": "Apr", "hires": 7, "exits": 3},
#                 {"month": "May", "hires": 9, "exits": 5},
#                 {"month": "Jun", "hires": 4, "exits": 3}
#             ],
#             "insights": [
#                 "Net workforce growth of 5.2%",
#                 "Wellness programs contributed to improved satisfaction",
#                 "Retention in key departments above 95%"
#             ],
#             "recommendations": [
#                 "Continue investment in employee wellness",
#                 "Implement mentorship programs for new hires"
#             ]
#         }
#     else:
#         return {
#             "answer": "Based on current data analysis, overall business metrics show positive growth across departments with 12% average improvement.",
#             "insights": [
#                 "Revenue growth trending upward",
#                 "Operational efficiency at peak levels",
#                 "Customer satisfaction improving"
#             ],
#             "recommendations": [
#                 "Maintain current strategic initiatives",
#                 "Monitor emerging market trends"
#             ]
#         }

# # ============================================================================
# # MOCK DATA GENERATOR
# # ============================================================================

# def generate_mock_kpi_data(department: Department):
#     kpi_mapping = {
#         Department.FINANCE: {
#             "kpis": [
#                 {"label": "Total Revenue", "value": "$2.4M", "change": "+12.5%", "positive": True},
#                 {"label": "Expenses", "value": "$1.8M", "change": "+8.2%", "positive": False},
#                 {"label": "Net Profit", "value": "$600K", "change": "+18.3%", "positive": True},
#                 {"label": "Profit Margin", "value": "25%", "change": "+2.1%", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "revenue": 180, "expenses": 140},
#                 {"month": "Feb", "revenue": 200, "expenses": 150},
#                 {"month": "Mar", "revenue": 220, "expenses": 160},
#                 {"month": "Apr", "revenue": 240, "expenses": 180},
#                 {"month": "May", "revenue": 260, "expenses": 190},
#                 {"month": "Jun", "revenue": 280, "expenses": 200}
#             ],
#             "summary": "Q2 revenue grew by 12.5% with controlled expense management. Profit margins improved across all divisions."
#         },
#         Department.HR: {
#             "kpis": [
#                 {"label": "Total Employees", "value": "342", "change": "+5.2%", "positive": True},
#                 {"label": "Attrition Rate", "value": "8.2%", "change": "-1.3%", "positive": True},
#                 {"label": "New Hires", "value": "23", "change": "+15%", "positive": True},
#                 {"label": "Satisfaction", "value": "87%", "change": "+3%", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "hires": 5, "exits": 3},
#                 {"month": "Feb", "hires": 8, "exits": 2},
#                 {"month": "Mar", "hires": 6, "exits": 4},
#                 {"month": "Apr", "hires": 7, "exits": 3},
#                 {"month": "May", "hires": 9, "exits": 5},
#                 {"month": "Jun", "hires": 4, "exits": 3}
#             ],
#             "summary": "Workforce grew steadily with reduced attrition. Employee satisfaction improved through new wellness programs."
#         },
#         Department.SALES: {
#             "kpis": [
#                 {"label": "Total Deals", "value": "156", "change": "+22%", "positive": True},
#                 {"label": "Conversion Rate", "value": "34%", "change": "+5%", "positive": True},
#                 {"label": "Pipeline Value", "value": "$4.2M", "change": "+28%", "positive": True},
#                 {"label": "Avg Deal Size", "value": "$27K", "change": "+8%", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "deals": 20, "value": 540},
#                 {"month": "Feb", "deals": 25, "value": 675},
#                 {"month": "Mar", "deals": 28, "value": 756},
#                 {"month": "Apr", "deals": 22, "value": 594},
#                 {"month": "May", "deals": 30, "value": 810},
#                 {"month": "Jun", "deals": 31, "value": 837}
#             ],
#             "summary": "Outstanding sales performance with 22% growth in closed deals. Pipeline value reached all-time high."
#         },
#         Department.OPERATIONS: {
#             "kpis": [
#                 {"label": "Efficiency", "value": "94%", "change": "+2%", "positive": True},
#                 {"label": "Downtime", "value": "2.3h", "change": "-15%", "positive": True},
#                 {"label": "Orders", "value": "1,234", "change": "+18%", "positive": True},
#                 {"label": "On-Time", "value": "96%", "change": "+3%", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "efficiency": 91, "downtime": 3.2},
#                 {"month": "Feb", "efficiency": 92, "downtime": 2.8},
#                 {"month": "Mar", "efficiency": 93, "downtime": 2.5},
#                 {"month": "Apr", "efficiency": 94, "downtime": 2.3},
#                 {"month": "May", "efficiency": 94, "downtime": 2.1},
#                 {"month": "Jun", "efficiency": 95, "downtime": 1.9}
#             ],
#             "summary": "Operational efficiency improved with reduced equipment downtime. On-time delivery exceeds target."
#         },
#         Department.COMPLIANCE: {
#             "kpis": [
#                 {"label": "Audits", "value": "12", "change": "0%", "positive": True},
#                 {"label": "Open Issues", "value": "3", "change": "-40%", "positive": True},
#                 {"label": "Resolved", "value": "89%", "change": "+12%", "positive": True},
#                 {"label": "Risk Level", "value": "Low", "change": "Stable", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "audits": 2, "issues": 5},
#                 {"month": "Feb", "audits": 2, "issues": 4},
#                 {"month": "Mar", "audits": 2, "issues": 6},
#                 {"month": "Apr", "audits": 2, "issues": 5},
#                 {"month": "May", "audits": 2, "issues": 4},
#                 {"month": "Jun", "audits": 2, "issues": 3}
#             ],
#             "summary": "Compliance metrics remain strong with 89% issue resolution rate. All audits passed successfully."
#         }
#     }
#     return kpi_mapping.get(department, kpi_mapping[Department.FINANCE])

# # ============================================================================
# # PDF GENERATION FUNCTIONS
# # ============================================================================

# async def generate_pdf_report(department: str, filename: str, data_preview: List[Dict], 
#                             analysis_result: Dict, user_name: str) -> bytes:
#     """Generate PDF report from AI analysis"""
#     try:
#         # Create a buffer for PDF
#         buffer = io.BytesIO()
        
#         # Create PDF document
#         doc = SimpleDocTemplate(buffer, pagesize=letter, 
#                               topMargin=0.5*inch, bottomMargin=0.5*inch,
#                               leftMargin=0.5*inch, rightMargin=0.5*inch)
        
#         # Story to hold PDF elements
#         story = []
#         styles = getSampleStyleSheet()
        
#         # Custom styles
#         title_style = ParagraphStyle(
#             'CustomTitle',
#             parent=styles['Heading1'],
#             fontSize=18,
#             spaceAfter=30,
#             textColor=colors.HexColor('#1E40AF'),
#             alignment=1  # Center alignment
#         )
        
#         heading_style = ParagraphStyle(
#             'CustomHeading',
#             parent=styles['Heading2'],
#             fontSize=14,
#             spaceAfter=12,
#             spaceBefore=20,
#             textColor=colors.HexColor('#2D3748')
#         )
        
#         normal_style = ParagraphStyle(
#             'CustomNormal',
#             parent=styles['Normal'],
#             fontSize=10,
#             spaceAfter=6,
#             textColor=colors.HexColor('#4A5568')
#         )
        
#         bullet_style = ParagraphStyle(
#             'CustomBullet',
#             parent=styles['Normal'],
#             fontSize=10,
#             spaceAfter=4,
#             leftIndent=20,
#             textColor=colors.HexColor('#4A5568')
#         )
        
#         # Title
#         dept_display = department.title() if department else "Unknown"
#         title = Paragraph(f"AI Analysis Report - {dept_display} Department", title_style)
#         story.append(title)
        
#         # File info
#         info_style = ParagraphStyle(
#             'InfoStyle',
#             parent=styles['Normal'],
#             fontSize=9,
#             textColor=colors.gray,
#             alignment=1
#         )
#         story.append(Paragraph(f"<b>File:</b> {filename}", info_style))
#         story.append(Paragraph(f"<b>Generated by:</b> {user_name}", info_style))
#         story.append(Paragraph(f"<b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC", info_style))
#         story.append(Spacer(1, 25))
        
#         # Executive Summary
#         story.append(Paragraph("Executive Summary", heading_style))
#         summary_text = analysis_result.get('summary', 'No summary available.')
#         # Clean summary text - remove markdown and fix formatting
#         summary_text = clean_text_for_pdf(summary_text)
#         story.append(Paragraph(summary_text, normal_style))
#         story.append(Spacer(1, 15))
        
#         # Key Insights
#         story.append(Paragraph("Key Insights", heading_style))
#         insights = analysis_result.get('insights', [])
#         if insights:
#             for insight in insights:
#                 # Clean each insight text
#                 clean_insight = clean_text_for_pdf(insight)
#                 story.append(Paragraph(f"• {clean_insight}", bullet_style))
#         else:
#             story.append(Paragraph("No specific insights generated.", normal_style))
#         story.append(Spacer(1, 15))
        
#         # Recommendations
#         story.append(Paragraph("Actionable Recommendations", heading_style))
#         recommendations = analysis_result.get('recommendations', [])
#         if recommendations:
#             for rec in recommendations:
#                 # Clean each recommendation text
#                 clean_rec = clean_text_for_pdf(rec)
#                 story.append(Paragraph(f"• {clean_rec}", bullet_style))
#         else:
#             story.append(Paragraph("No specific recommendations generated.", normal_style))
#         story.append(Spacer(1, 15))
        
#         # Data Overview
#         story.append(Paragraph("Data Overview", heading_style))
#         if data_preview and len(data_preview) > 0:
#             data_info = f"Dataset contains {len(data_preview)} sample rows with {len(data_preview[0]) if data_preview else 0} columns."
#             story.append(Paragraph(data_info, normal_style))
#             story.append(Spacer(1, 10))
        
#         # Trends Analysis
#         trends = analysis_result.get('trends', {})
#         if trends and trends.get('trend') != 'unknown':
#             story.append(Paragraph("Trend Analysis", heading_style))
            
#             trend_info = []
#             if trends.get('trend'):
#                 trend_info.append(f"<b>Overall Trend:</b> {trends['trend'].title()}")
#             if trends.get('confidence'):
#                 trend_info.append(f"<b>Confidence Level:</b> {trends['confidence'].title()}")
#             if trends.get('pattern'):
#                 clean_pattern = clean_text_for_pdf(trends['pattern'])
#                 trend_info.append(f"<b>Pattern:</b> {clean_pattern}")
#             if trends.get('prediction'):
#                 clean_prediction = clean_text_for_pdf(trends['prediction'])
#                 trend_info.append(f"<b>Prediction:</b> {clean_prediction}")
#             if trends.get('reasoning'):
#                 clean_reasoning = clean_text_for_pdf(trends['reasoning'])
#                 trend_info.append(f"<b>Reasoning:</b> {clean_reasoning}")
            
#             for info in trend_info:
#                 story.append(Paragraph(info, normal_style))
#             story.append(Spacer(1, 15))
        
#         # Anomalies
#         anomalies = analysis_result.get('anomalies', [])
#         if anomalies:
#             story.append(Paragraph("Detected Anomalies", heading_style))
#             for i, anomaly in enumerate(anomalies[:5], 1):  # Show first 5 anomalies
#                 desc = clean_text_for_pdf(anomaly.get('description', 'N/A'))
#                 severity = anomaly.get('severity', 'N/A').title()
#                 anomaly_type = anomaly.get('type', 'N/A').title()
                
#                 anomaly_text = f"<b>Anomaly {i}:</b> {desc} | <b>Type:</b> {anomaly_type} | <b>Severity:</b> {severity}"
#                 story.append(Paragraph(anomaly_text, bullet_style))
#             story.append(Spacer(1, 15))
        
#         # Data Preview Table
#         if data_preview and len(data_preview) > 0:
#             story.append(Paragraph("Data Preview (First 10 Rows)", heading_style))
            
#             # Create table data
#             headers = list(data_preview[0].keys())
#             table_data = [headers]
            
#             for row in data_preview[:10]:
#                 # Clean and truncate cell values
#                 clean_row = []
#                 for val in row.values():
#                     clean_val = str(val)
#                     # Remove any markdown formatting
#                     clean_val = clean_val.replace('*', '').replace('_', '').replace('#', '')
#                     # Truncate long values
#                     if len(clean_val) > 30:
#                         clean_val = clean_val[:27] + '...'
#                     clean_row.append(clean_val)
#                 table_data.append(clean_row)
            
#             # Create table
#             if len(table_data) > 1:
#                 table = Table(table_data, repeatRows=1)
#                 table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 9),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
#                     ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F7FAFC')),
#                     ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                     ('FONTSIZE', (0, 1), (-1, -1), 8),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
#                     ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')])
#                 ]))
#                 story.append(table)
#                 story.append(Spacer(1, 15))
        
#         # Footer with generation info
#         story.append(Spacer(1, 20))
#         footer_style = ParagraphStyle(
#             'FooterStyle',
#             parent=styles['Normal'],
#             fontSize=8,
#             textColor=colors.gray,
#             alignment=1
#         )
#         story.append(Paragraph("Generated by AI-Powered Report Generator", footer_style))
#         story.append(Paragraph("Confidential - For Internal Use Only", footer_style))
        
#         # Build PDF
#         doc.build(story)
        
#         # Get PDF bytes
#         pdf_bytes = buffer.getvalue()
#         buffer.close()
        
#         return pdf_bytes
        
#     except Exception as e:
#         logger.error(f"PDF generation error: {str(e)}")
#         # Return a simple error PDF
#         return generate_error_pdf(str(e))
    
# def clean_text_for_pdf(text: str) -> str:
#     """Clean text for PDF formatting - remove markdown and fix common issues"""
#     if not text:
#         return ""
    
#     # Remove markdown formatting
#     clean_text = text.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
    
#     # Remove excessive newlines and spaces
#     clean_text = ' '.join(clean_text.split())
    
#     # Fix common AI response artifacts
#     clean_text = clean_text.replace('•', '-')  # Replace bullet points with dashes
#     clean_text = clean_text.replace('```', '')  # Remove code blocks
#     clean_text = clean_text.replace('`', '')    # Remove inline code
    
#     # Ensure proper sentence capitalization
#     if clean_text and clean_text[0].islower():
#         clean_text = clean_text[0].upper() + clean_text[1:]
    
#     return clean_text




# def generate_error_pdf(error_message: str) -> bytes:
#     """Generate a simple error PDF"""
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     story = []
#     styles = getSampleStyleSheet()
    
#     # Title
#     title_style = ParagraphStyle(
#         'ErrorTitle',
#         parent=styles['Heading1'],
#         fontSize=16,
#         spaceAfter=20,
#         textColor=colors.red,
#         alignment=1
#     )
#     story.append(Paragraph("Report Generation Error", title_style))
#     story.append(Spacer(1, 20))
    
#     # Error message
#     normal_style = ParagraphStyle(
#         'ErrorNormal',
#         parent=styles['Normal'],
#         fontSize=12,
#         spaceAfter=12,
#         textColor=colors.darkred,
#         alignment=1
#     )
#     story.append(Paragraph("We encountered an issue while generating your report:", normal_style))
#     story.append(Spacer(1, 10))
#     story.append(Paragraph(error_message, normal_style))
#     story.append(Spacer(1, 20))
    
#     # Contact info
#     contact_style = ParagraphStyle(
#         'ContactStyle',
#         parent=styles['Normal'],
#         fontSize=10,
#         textColor=colors.gray,
#         alignment=1
#     )
#     story.append(Paragraph("Please try again or contact support if the issue persists.", contact_style))
    
#     doc.build(story)
#     pdf_bytes = buffer.getvalue()
#     buffer.close()
#     return pdf_bytes

# # ============================================================================
# # API ENDPOINTS
# # ============================================================================

# @app.get("/")
# async def root():
#     return {
#         "service": "Autonomous Report Generator API with MongoDB",
#         "status": "operational",
#         "version": "1.0.0",
#         "timestamp": datetime.utcnow().isoformat()
#     }

# # ============================================================================
# # AUTHENTICATION ENDPOINTS
# # ============================================================================

# @app.post("/api/auth/register", response_model=Token)
# async def register(user_data: UserRegister, db=Depends(get_database)):
#     """Register a new user"""
#     # Check if user exists
#     existing_user = await db.users.find_one({"email": user_data.email})
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Create new user
#     user_id = str(uuid.uuid4())
#     hashed_password = get_password_hash(user_data.password)
    
#     user = {
#         "id": user_id,
#         "email": user_data.email,
#         "password": hashed_password,
#         "name": user_data.name,
#         "role": user_data.role,
#         "departments": user_data.departments,
#         "created_at": datetime.utcnow(),
#         "updated_at": datetime.utcnow()
#     }
    
#     await db.users.insert_one(user)
    
#     # Create access token
#     access_token = create_access_token({"sub": user_id})
    
#     # Return token and user info
#     user_response = {k: v for k, v in user.items() if k != "password"}
#     user_response = serialize_doc(user_response)
    
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": user_response
#     }

# @app.post("/api/auth/login", response_model=Token)
# async def login(credentials: UserLogin, db=Depends(get_database)):
#     """Login with email and password"""
#     # Find user by email
#     user = await db.users.find_one({"email": credentials.email})
    
#     if not user or not verify_password(credentials.password, user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
    
#     # Create access token
#     access_token = create_access_token({"sub": user["id"]})
    
#     # Return token and user info
#     user_response = {k: v for k, v in user.items() if k != "password"}
#     user_response = serialize_doc(user_response)
    
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": user_response
#     }

# @app.get("/api/auth/me")
# async def get_current_user_info(current_user: dict = Depends(get_current_user)):
#     """Get current user information"""
#     return {k: v for k, v in current_user.items() if k != "password"}

# # ============================================================================
# # CSV UPLOAD & ANALYSIS ENDPOINTS
# # ============================================================================

# @app.post("/api/reports/upload-csv")
# async def upload_csv_analysis(
#     file: UploadFile = File(...),
#     department: str = Form(None),
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Upload CSV for AI analysis and report generation"""
#     try:
#         logger.info(f"Upload received: {file.filename}, department: {department}")
        
#         if not file.filename.endswith('.csv'):
#             raise HTTPException(
#                 status_code=400, 
#                 detail="Only CSV files are supported"
#             )
        
#         # Validate department
#         if not department:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Department is required"
#             )
        
#         try:
#             # Convert string to Department enum
#             department_enum = Department(department.lower())
#         except ValueError:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid department: {department}. Must be one of: {[d.value for d in Department]}"
#             )
        
#         # Check if user has access to this department
#         if department_enum not in current_user["departments"]:
#             raise HTTPException(
#                 status_code=403,
#                 detail=f"Access denied to {department} department"
#             )
        
#         # Read and parse CSV
#         content = await file.read()
#         logger.info(f"File size: {len(content)} bytes")
        
#         try:
#             csv_text = content.decode('utf-8')
#             df = pd.read_csv(io.StringIO(csv_text))
#             logger.info(f"CSV parsed successfully: {len(df)} rows, {len(df.columns)} columns")
#         except Exception as csv_error:
#             raise HTTPException(
#                 status_code=400, 
#                 detail=f"Invalid CSV file: {str(csv_error)}"
#             )
        
#         # Basic data validation
#         if df.empty:
#             raise HTTPException(status_code=400, detail="CSV file is empty")
        
#         if len(df.columns) == 0:
#             raise HTTPException(status_code=400, detail="CSV file has no columns")
        
#         # Convert DataFrame to list of dictionaries for AI processing
#         data_records = df.to_dict('records')
        
#         # Get AI agents
#         try:
#             llama_agent = get_llama_agent()
#             analysis_agent = get_analysis_agent()
#             logger.info("AI agents initialized successfully")
#         except Exception as agent_error:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"AI service unavailable: {str(agent_error)}"
#             )
        
#         # Prepare context for AI analysis
#         context = {
#             "department": department_enum.value,
#             "data_preview": data_records[:5],  # First 5 records for context
#             "columns": list(df.columns),
#             "total_records": len(df),
#             "data_summary": {
#                 "columns": list(df.columns),
#                 "total_rows": len(df),
#                 "data_types": df.dtypes.to_dict()
#             }
#         }
        
#         # Generate AI analysis with error handling
#         try:
#             analysis_result = analysis_agent.analyze_department_performance(
#                 department=department_enum.value,
#                 kpis=[{"label": col, "value": "Analyzing...", "change": "0%", "positive": True} for col in df.columns[:4]],
#                 chart_data=data_records[:10]  # Use first 10 records for chart data
#             )
#             logger.info("AI analysis completed successfully")
#         except Exception as analysis_error:
#             logger.error(f"AI analysis failed: {str(analysis_error)}")
#             # Provide fallback analysis
#             analysis_result = {
#                 "summary": f"Basic analysis of {len(df)} records from {file.filename} in {department} department",
#                 "insights": [
#                     f"Data loaded successfully with {len(df)} rows and {len(df.columns)} columns",
#                     "AI analysis encountered issues but data is ready for review"
#                 ],
#                 "recommendations": [
#                     "Review data quality and structure",
#                     "Consider manual analysis for specific insights"
#                 ],
#                 "trends": {
#                     "trend": "unknown", 
#                     "pattern": "Analysis limited due to technical issues",
#                     "prediction": "Further analysis required",
#                     "confidence": "low",
#                     "reasoning": "AI analysis encountered technical difficulties"
#                 },
#                 "anomalies": []
#             }
        
#         # Generate PDF report
#         try:
#             pdf_report = await generate_pdf_report(
#                 department=department_enum.value,  # Use string value, not enum
#                 filename=file.filename,
#                 data_preview=data_records[:10],
#                 analysis_result=analysis_result,
#                 user_name=current_user["name"]
#             )
#             logger.info("PDF report generated successfully")
#         except Exception as pdf_error:
#             logger.error(f"PDF generation failed: {str(pdf_error)}")
#             # Generate a simple error PDF instead of failing completely
#             pdf_report = generate_error_pdf(f"PDF generation issue: {str(pdf_error)}")
        
#         # Store report in database
#         report_id = str(uuid.uuid4())
#         report_data = {
#             "id": report_id,
#             "title": f"AI Analysis - {file.filename}",
#             "department": department_enum.value,
#             "report_type": ReportType.PDF.value,
#             "file_url": f"/api/reports/download/{report_id}",
#             "size": f"{(len(content) / 1024 / 1024):.1f} MB",
#             "status": "completed",
#             "created_by": current_user["id"],
#             "created_by_name": current_user["name"],
#             "created_at": datetime.utcnow(),
#             "source": "csv_upload",
#             "original_filename": file.filename,
#             "analysis_data": analysis_result
#         }
        
#         await db.reports.insert_one(report_data)
        
#         # Store PDF file
#         await db.report_files.insert_one({
#             "report_id": report_id,
#             "pdf_content": base64.b64encode(pdf_report).decode('utf-8'),
#             "created_at": datetime.utcnow()
#         })
        
#         # Log activity
#         activity = {
#             "id": str(uuid.uuid4()),
#             "action": f"CSV Analysis Report Generated: {file.filename}",
#             "user_id": current_user["id"],
#             "user_name": current_user["name"],
#             "timestamp": datetime.utcnow(),
#             "type": "csv_analysis",
#             "department": department_enum.value
#         }
#         await db.activities.insert_one(activity)
        
#         return {
#             "message": "CSV analyzed and report generated successfully",
#             "report_id": report_id,
#             "analysis": analysis_result,
#             "data_preview": {
#                 "columns": list(df.columns),
#                 "first_five_rows": data_records[:5],
#                 "total_rows": len(df)
#             }
#         }
        
#     except HTTPException:
#         # Re-raise HTTP exceptions
#         raise
#     except Exception as e:
#         logger.error(f"Unexpected error in upload_csv_analysis: {str(e)}")
#         import traceback
#         logger.error(traceback.format_exc())
#         raise HTTPException(
#             status_code=500, 
#             detail=f"Internal server error: {str(e)}"
#         )

# @app.get("/api/reports/download/{report_id}")
# async def download_report_pdf(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Download generated PDF report"""
#     try:
#         logger.info(f"Download request for report: {report_id}")
        
#         # Get report metadata
#         report = await db.reports.find_one({"id": report_id})
#         if not report:
#             logger.error(f"Report not found: {report_id}")
#             raise HTTPException(status_code=404, detail="Report not found")
        
#         logger.info(f"Found report: {report['title']} for department: {report['department']}")
        
#         # Check user access
#         user_departments = [d.value if isinstance(d, Department) else d for d in current_user["departments"]]
#         if report["department"] not in user_departments:
#             logger.error(f"Access denied: User {current_user['id']} cannot access {report['department']}")
#             raise HTTPException(status_code=403, detail="Access denied to this report")
        
#         # Get PDF content
#         pdf_file = await db.report_files.find_one({"report_id": report_id})
#         if not pdf_file:
#             logger.error(f"PDF file not found for report: {report_id}")
#             raise HTTPException(status_code=404, detail="PDF file not found")
        
#         logger.info(f"PDF file found, size: {len(pdf_file['pdf_content'])} bytes")
        
#         # Decode PDF content
#         try:
#             pdf_content = base64.b64decode(pdf_file["pdf_content"])
#             logger.info(f"PDF decoded successfully, size: {len(pdf_content)} bytes")
#         except Exception as decode_error:
#             logger.error(f"PDF decode error: {str(decode_error)}")
#             raise HTTPException(status_code=500, detail="Corrupted PDF file")
        
#         # Validate PDF content
#         if len(pdf_content) == 0:
#             logger.error("PDF content is empty")
#             raise HTTPException(status_code=500, detail="Empty PDF file")
        
#         # Return PDF file
#         from fastapi.responses import Response
#         filename = f"{report['title']}.pdf".replace(" ", "_")
        
#         logger.info(f"Returning PDF file: {filename}")
        
#         return Response(
#             content=pdf_content,
#             media_type="application/pdf",
#             headers={
#                 "Content-Disposition": f"attachment; filename={filename}",
#                 "Content-Length": str(len(pdf_content)),
#                 "Access-Control-Allow-Origin": "*",
#                 "Access-Control-Allow-Credentials": "true"
#             }
#         )
        
#     except HTTPException:
#         # Re-raise HTTP exceptions
#         raise
#     except Exception as e:
#         logger.error(f"PDF download error: {str(e)}")
#         import traceback
#         logger.error(traceback.format_exc())
#         raise HTTPException(
#             status_code=500, 
#             detail=f"Error downloading PDF: {str(e)}"
#         )
    
# @app.get("/api/reports/{report_id}/debug")
# async def debug_report(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Debug endpoint to check report status"""
#     try:
#         # Get report metadata
#         report = await db.reports.find_one({"id": report_id})
#         if not report:
#             return {"error": "Report not found"}
        
#         # Get PDF file info
#         pdf_file = await db.report_files.find_one({"report_id": report_id})
        
#         return {
#             "report_found": bool(report),
#             "report_data": {
#                 "id": report.get("id"),
#                 "title": report.get("title"),
#                 "department": report.get("department"),
#                 "created_at": report.get("created_at"),
#                 "status": report.get("status")
#             },
#             "pdf_file_found": bool(pdf_file),
#             "pdf_file_data": {
#                 "has_content": bool(pdf_file and pdf_file.get("pdf_content")),
#                 "content_length": len(pdf_file.get("pdf_content", "")) if pdf_file else 0,
#                 "created_at": pdf_file.get("created_at") if pdf_file else None
#             } if pdf_file else None,
#             "user_access": report["department"] in current_user["departments"] if report else False
#         }
#     except Exception as e:
#         return {"error": str(e)}

# @app.get("/api/reports/{report_id}/preview")
# async def preview_report(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get report preview and analysis data"""
#     report = await db.reports.find_one({"id": report_id})
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     if report["department"] not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied")
    
#     return {
#         "report": serialize_doc(report),
#         "analysis": report.get("analysis_data", {})
#     }

# # ============================================================================
# # CORS PREFLIGHT HANDLERS
# # ============================================================================

# @app.options("/api/reports/upload-csv")
# async def options_upload_csv():
#     """Handle CORS preflight for CSV upload"""
#     # Remove this line: from fastapi.responses import JSONResponse
#     return JSONResponse(
#         content={"message": "OK"},
#         headers={
#             "Access-Control-Allow-Origin": "*",
#             "Access-Control-Allow-Methods": "POST, OPTIONS",
#             "Access-Control-Allow-Headers": "*",
#             "Access-Control-Allow-Credentials": "true"
#         }
#     )

# @app.options("/api/reports/download/{report_id}")
# async def options_download_report():
#     """Handle CORS preflight for download"""
#     # Remove this line: from fastapi.responses import JSONResponse
#     return JSONResponse(
#         content={"message": "OK"},
#         headers={
#             "Access-Control-Allow-Origin": "*",
#             "Access-Control-Allow-Methods": "GET, OPTIONS",
#             "Access-Control-Allow-Headers": "*",
#             "Access-Control-Allow-Credentials": "true"
#         }
#     )
# # ============================================================================
# # DASHBOARD & KPI ENDPOINTS
# # ============================================================================

# @app.get("/api/dashboard/stats")
# async def get_dashboard_stats(
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get overall dashboard statistics"""
#     total_reports = await db.reports.count_documents({
#         "department": {"$in": current_user["departments"]}
#     })
    
#     active_alerts = await db.alerts.count_documents({
#         "department": {"$in": current_user["departments"]},
#         "acknowledged": False
#     })
    
#     recent_activities = await db.activities.find({
#         "user_id": current_user["id"]
#     }).sort("timestamp", -1).limit(5).to_list(length=5)
    
#     recent_activities = [serialize_doc(activity) for activity in recent_activities]
    
#     return {
#         "total_reports": total_reports,
#         "active_alerts": active_alerts,
#         "departments": len(current_user["departments"]),
#         "data_sources": 23,
#         "recent_activity": recent_activities
#     }

# @app.get("/api/dashboard/kpis/{department}")
# async def get_department_kpis(
#     department: Department,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Get KPIs for a specific department"""
#     if department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this department")
    
#     data = generate_mock_kpi_data(department)
#     return {
#         "department": department,
#         "kpis": data["kpis"],
#         "chart_data": data["chart_data"],
#         "summary": data["summary"],
#         "last_updated": datetime.utcnow().isoformat()
#     }

# @app.get("/api/dashboard/activity")
# async def get_recent_activity(
#     limit: int = 10,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get recent activity log"""
#     activities = await db.activities.find({
#         "user_id": current_user["id"]
#     }).sort("timestamp", -1).limit(limit).to_list(length=limit)
    
#     activities = [serialize_doc(activity) for activity in activities]
    
#     total_activities = await db.activities.count_documents({
#         "user_id": current_user["id"]
#     })
    
#     return {
#         "activities": activities,
#         "total": total_activities
#     }

# # ============================================================================
# # REPORT MANAGEMENT ENDPOINTS
# # ============================================================================

# @app.post("/api/reports/generate")
# async def generate_report(
#     report_data: ReportGenerate,
#     background_tasks: BackgroundTasks,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Generate a new report"""
#     if report_data.department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this department")
    
#     report_id = str(uuid.uuid4())
    
#     report = {
#         "id": report_id,
#         "title": report_data.title,
#         "department": report_data.department,
#         "report_type": report_data.report_type,
#         "file_url": f"/reports/{report_id}.{report_data.report_type}",
#         "size": "2.4 MB",
#         "status": "completed",
#         "created_by": current_user["id"],
#         "created_by_name": current_user["name"],
#         "created_at": datetime.utcnow(),
#         "date_range": report_data.date_range,
#         "frequency": report_data.frequency,
#         "scheduled": report_data.schedule
#     }
    
#     await db.reports.insert_one(report)
    
#     # Add to activity log
#     activity = {
#         "id": str(uuid.uuid4()),
#         "action": f"Report Generated: {report_data.title}",
#         "user_id": current_user["id"],
#         "user_name": current_user["name"],
#         "timestamp": datetime.utcnow(),
#         "type": "report_generated",
#         "department": report_data.department
#     }
    
#     await db.activities.insert_one(activity)
    
#     return serialize_doc(report)

# @app.get("/api/reports")
# async def get_reports(
#     department: Optional[Department] = None,
#     limit: int = 50,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get list of reports"""
#     query = {"department": {"$in": current_user["departments"]}}
    
#     if department:
#         if department not in current_user["departments"]:
#             raise HTTPException(status_code=403, detail="Access denied to this department")
#         query["department"] = department
    
#     reports = await db.reports.find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
#     reports = [serialize_doc(report) for report in reports]
    
#     total = await db.reports.count_documents(query)
    
#     return {
#         "reports": reports,
#         "total": total
#     }

# @app.get("/api/reports/{report_id}")
# async def get_report(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get specific report details"""
#     report = await db.reports.find_one({"id": report_id})
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     if report["department"] not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this report")
    
#     return serialize_doc(report)

# @app.delete("/api/reports/{report_id}")
# async def delete_report(
#     report_id: str,
#     current_user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER])),
#     db=Depends(get_database)
# ):
#     """Delete a report (Admin/Manager only)"""
#     report = await db.reports.find_one({"id": report_id})
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     await db.reports.delete_one({"id": report_id})
    
#     # Also delete related comments
#     await db.comments.delete_many({"report_id": report_id})
    
#     return {"message": "Report deleted successfully", "report_id": report_id}

# # ============================================================================
# # NLP QUERY ENGINE ENDPOINTS
# # ============================================================================

# @app.post("/api/query", response_model=QueryResponse)
# async def process_query(
#     query_data: NLPQuery,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Process natural language query using LLaMA Agent"""
#     if query_data.department and query_data.department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this department")
    
#     try:
#         # Get LLaMA agent
#         agent = get_llama_agent()
        
#         # Prepare context
#         context = {
#             "department": query_data.department.value if query_data.department else None,
#             "user_role": current_user["role"],
#             "query_context": query_data.context or {}
#         }
        
#         # Add department data if specified
#         if query_data.department:
#             dept_data = generate_mock_kpi_data(query_data.department)
#             context["kpis"] = dept_data["kpis"]
#             context["chart_data"] = dept_data["chart_data"]
        
#         # Process with LLaMA agent
#         result = agent.process_query(query_data.query, context)
        
#         # Log activity
#         activity = {
#             "id": str(uuid.uuid4()),
#             "action": f"LLaMA Query: {query_data.query[:50]}...",
#             "user_id": current_user["id"],
#             "user_name": current_user["name"],
#             "timestamp": datetime.utcnow(),
#             "type": "llama_query_processed",
#             "department": query_data.department.value if query_data.department else None
#         }
        
#         await db.activities.insert_one(activity)
        
#         return {
#             "query": query_data.query,
#             "answer": result["answer"],
#             "insights": result.get("insights", []),
#             "chart_data": result.get("chart_data"),
#             "recommendations": result.get("recommendations", [])
#         }
        
#     except Exception as e:
#         logger.error(f"Query processing error: {str(e)}")
#         raise HTTPException(status_code=500, detail="Error processing query")

# # ============================================================================
# # AI ANALYSIS ENDPOINTS
# # ============================================================================

# @app.post("/api/analytics/llama-analysis")
# async def llama_comprehensive_analysis(
#     request_data: dict,
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Comprehensive department analysis using LLaMA Agent
#     """
#     department = request_data.get("department")
    
#     if department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied")
    
#     try:
#         # Get analysis agent
#         analysis_agent = get_analysis_agent()
        
#         # Get department data
#         dept_data = generate_mock_kpi_data(department)
        
#         # Perform comprehensive analysis
#         result = analysis_agent.analyze_department_performance(
#             department=department,
#             kpis=dept_data["kpis"],
#             chart_data=dept_data["chart_data"]
#         )
        
#         return {
#             "department": department,
#             "analysis": result,
#             "generated_at": datetime.utcnow().isoformat()
#         }
        
#     except Exception as e:
#         logger.error(f"Comprehensive analysis error: {str(e)}")
#         raise HTTPException(status_code=500, detail="Analysis error")

# # ============================================================================
# # MAIN ENTRY POINT
# # ============================================================================

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

















# //////////////////////////////////// OLD BACKEND /////////////////////////////


# # ============================================================================
# # AUTONOMOUS REPORT GENERATOR - BACKEND API WITH MONGODB
# # Framework: FastAPI (Python)
# # Database: MongoDB Atlas
# # Features: JWT Auth, AI Analysis, Report Generation, NLP Queries, Alerts
# # ============================================================================
# # Add after existing imports
# from ai_models.llama_agent import get_llama_agent
# from ai_models.analysis_agent import get_analysis_agent
# from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, BackgroundTasks
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, EmailStr, Field
# from typing import Optional, List, Dict, Any
# from datetime import datetime, timedelta
# from passlib.context import CryptContext
# import jwt
# import json
# from enum import Enum
# import pandas as pd
# from io import StringIO
# import uuid
# import os
# from motor.motor_asyncio import AsyncIOMotorClient
# from bson import ObjectId
# from pymongo import ReturnDocument



# import io
# import base64
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib import colors
# from reportlab.lib.units import inch
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# import tempfile
# import uuid

# # ============================================================================
# # LIFESPAN & APP INITIALIZATION
# # ============================================================================

# from contextlib import asynccontextmanager
# from dotenv import load_dotenv

# load_dotenv()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup: Initialize MongoDB connection
#     print("✅ Initializing Backend API with MongoDB...")
    
#     # Initialize MongoDB connection
#     app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
#     app.mongodb = app.mongodb_client[os.getenv("MONGODB_DB_NAME", "report_generator")]
    
#     # Create indexes
#     await create_indexes(app.mongodb)
    
#     # Create default admin user if not exists
#     admin_user = await app.mongodb.users.find_one({"email": "admin@company.com"})
#     if not admin_user:
#         admin_id = str(uuid.uuid4())
#         admin_user = {
#             "id": admin_id,
#             "email": "admin@company.com",
#             "password": get_password_hash("admin123"),
#             "name": "Admin User",
#             "role": UserRole.ADMIN,
#             "departments": [Department.FINANCE, Department.HR, Department.SALES, 
#                            Department.OPERATIONS, Department.COMPLIANCE],
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow()
#         }
#         await app.mongodb.users.insert_one(admin_user)
#         print("📧 Default admin created: admin@company.com / admin123")
    
#     # Create sample alerts if none exist
#     alerts_count = await app.mongodb.alerts.count_documents({})
#     if alerts_count == 0:
#         sample_alerts = []
#         for i in range(4):
#             alert_id = str(uuid.uuid4())
#             sample_alerts.append({
#                 "id": alert_id,
#                 "type": ["warning", "info", "success"][i % 3],
#                 "department": [Department.FINANCE, Department.HR, Department.SALES, Department.OPERATIONS][i],
#                 "message": f"Sample alert message {i+1}",
#                 "priority": [AlertPriority.HIGH, AlertPriority.MEDIUM, AlertPriority.LOW][i % 3],
#                 "created_at": datetime.utcnow(),
#                 "acknowledged": False,
#                 "created_by": admin_id
#             })
#         await app.mongodb.alerts.insert_many(sample_alerts)
    
#     print("🚀 Server running at http://localhost:8000")
#     print("📚 API docs available at http://localhost:8000/docs")
    
#     yield  # Server is running
    
#     # Cleanup: Close MongoDB connection
#     print("Shutting down...")
#     app.mongodb_client.close()

# # Initialize FastAPI with lifespan
# app = FastAPI(
#     title="Autonomous Report Generator API",
#     description="Enterprise AI-powered reporting system with MongoDB",
#     version="1.0.0",
#     lifespan=lifespan
# )

# # CORS Configuration
# cors_origins = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173", 
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "http://localhost:8080",
#     "http://127.0.0.1:8080",
#     "*"  # For development only - remove in production
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=cors_origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
#     allow_headers=["*"],
#     expose_headers=["*"]
# )

# # Security Configuration
# SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# security = HTTPBearer()

# # MongoDB Configuration
# MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
# DB_NAME = os.getenv("MONGODB_DB_NAME", "report_generator")

# # ============================================================================
# # ENUMS & CONSTANTS
# # ============================================================================

# class UserRole(str, Enum):
#     ADMIN = "admin"
#     MANAGER = "manager"
#     ANALYST = "analyst"
#     VIEWER = "viewer"

# class Department(str, Enum):
#     FINANCE = "finance"
#     HR = "hr"
#     SALES = "sales"
#     OPERATIONS = "operations"
#     COMPLIANCE = "compliance"

# class ReportType(str, Enum):
#     PDF = "pdf"
#     PPT = "ppt"
#     EXCEL = "excel"

# class ReportFrequency(str, Enum):
#     DAILY = "daily"
#     WEEKLY = "weekly"
#     MONTHLY = "monthly"

# class AlertPriority(str, Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"

# # ============================================================================
# # PYDANTIC MODELS
# # ============================================================================

# class UserRegister(BaseModel):
#     email: EmailStr
#     password: str
#     name: str
#     role: UserRole
#     departments: List[Department]

# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# class Token(BaseModel):
#     access_token: str
#     token_type: str
#     user: Dict[str, Any]

# class User(BaseModel):
#     id: str
#     email: EmailStr
#     name: str
#     role: UserRole
#     departments: List[Department]
#     created_at: datetime

# class ReportGenerate(BaseModel):
#     title: str
#     department: Department
#     report_type: ReportType
#     date_range: Dict[str, str]
#     frequency: Optional[ReportFrequency] = None
#     schedule: Optional[bool] = False

# class Report(BaseModel):
#     id: str
#     title: str
#     department: Department
#     report_type: ReportType
#     file_url: str
#     size: str
#     status: str
#     created_by: str
#     created_at: datetime

# class NLPQuery(BaseModel):
#     query: str
#     department: Optional[Department] = None
#     context: Optional[Dict[str, Any]] = None

# class QueryResponse(BaseModel):
#     query: str
#     answer: str
#     insights: List[str]
#     chart_data: Optional[List[Dict[str, Any]]] = None
#     recommendations: Optional[List[str]] = None

# class Alert(BaseModel):
#     id: str
#     type: str
#     department: Department
#     message: str
#     priority: AlertPriority
#     created_at: datetime
#     acknowledged: bool = False

# class CommentCreate(BaseModel):
#     report_id: str
#     content: str
#     mentioned_users: Optional[List[str]] = []

# class Comment(BaseModel):
#     id: str
#     report_id: str
#     user_id: str
#     user_name: str
#     content: str
#     mentioned_users: List[str]
#     created_at: datetime
#     replies: List[Dict[str, Any]] = []

# class UserSettings(BaseModel):
#     language: str = "english"
#     theme: str = "light"
#     report_format: ReportType = ReportType.PDF
#     notifications: Dict[str, bool] = {
#         "email": True,
#         "slack": False,
#         "teams": False
#     }

# class KPIData(BaseModel):
#     department: Department
#     kpis: List[Dict[str, Any]]
#     chart_data: List[Dict[str, Any]]
#     summary: str

# # ============================================================================
# # DATABASE UTILITIES
# # ============================================================================

# async def create_indexes(db):
#     """Create database indexes for better performance"""
#     # Users collection indexes
#     await db.users.create_index("email", unique=True)
#     await db.users.create_index("role")
#     await db.users.create_index("departments")
    
#     # Reports collection indexes
#     await db.reports.create_index("department")
#     await db.reports.create_index("created_by")
#     await db.reports.create_index("created_at")
#     await db.reports.create_index([("department", 1), ("created_at", -1)])
    
#     # Alerts collection indexes
#     await db.alerts.create_index("department")
#     await db.alerts.create_index("priority")
#     await db.alerts.create_index("acknowledged")
#     await db.alerts.create_index("created_at")
    
#     # Comments collection indexes
#     await db.comments.create_index("report_id")
#     await db.comments.create_index("user_id")
#     await db.comments.create_index("created_at")
    
#     # Activities collection indexes
#     await db.activities.create_index("user_id")
#     await db.activities.create_index("timestamp")
    
#     print("✅ Database indexes created")

# def serialize_doc(doc):
#     """Convert MongoDB document to JSON serializable format"""
#     if doc and '_id' in doc:
#         doc['id'] = str(doc['_id'])
#         del doc['_id']
#     return doc

# async def get_database():
#     """Dependency to get database instance"""
#     return app.mongodb

# # ============================================================================
# # AUTHENTICATION UTILITIES
# # ============================================================================

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)

# def create_access_token(data: dict) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def decode_token(token: str) -> dict:
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token has expired")
#     except jwt.JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db=Depends(get_database)
# ) -> dict:
#     token = credentials.credentials
#     payload = decode_token(token)
#     user_id = payload.get("sub")
    
#     user = await db.users.find_one({"id": user_id})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     return serialize_doc(user)

# def check_role(required_roles: List[UserRole]):
#     async def role_checker(current_user: dict = Depends(get_current_user)):
#         if current_user["role"] not in required_roles:
#             raise HTTPException(status_code=403, detail="Insufficient permissions")
#         return current_user
#     return role_checker

# # ============================================================================
# # AI INTEGRATION FUNCTIONS
# # ============================================================================

# def analyze_with_ai(query: str, data: Any) -> Dict[str, Any]:
#     """Mock AI analysis function"""
#     insights = [
#         "Sales performance increased by 22% compared to previous quarter",
#         "Technology sector showed strongest growth at 28%",
#         "Customer retention improved by 15% through loyalty programs"
#     ]
    
#     recommendations = [
#         "Increase marketing budget in high-performing regions by 12%",
#         "Focus on customer retention strategies in underperforming segments",
#         "Expand product line in technology sector based on demand trends"
#     ]
    
#     return {
#         "insights": insights,
#         "recommendations": recommendations,
#         "confidence": 0.92
#     }

# def detect_anomalies(data: pd.DataFrame) -> List[Dict[str, Any]]:
#     """Anomaly detection using ML"""
#     anomalies = []
#     if len(data) > 0:
#         anomalies.append({
#             "type": "spike",
#             "metric": "expenses",
#             "value": "+15%",
#             "severity": "medium",
#             "description": "Unusual increase in marketing expenses detected"
#         })
#     return anomalies

# def generate_executive_summary(department: Department, data: Dict) -> str:
#     """Generate AI-powered executive summary"""
#     summaries = {
#         Department.FINANCE: "Q2 financial performance exceeded expectations with 12.5% revenue growth. Operating margins improved to 25% through strategic cost optimization. Cash flow remains strong with $2.4M total revenue.",
#         Department.HR: "Workforce expansion on track with 23 new hires. Attrition rate decreased to 8.2%, below industry average. Employee satisfaction scores improved to 87% following new wellness initiatives.",
#         Department.SALES: "Outstanding quarter with 156 deals closed, representing 22% growth. Average deal size increased to $27K. Sales pipeline robust at $4.2M with 34% conversion rate.",
#         Department.OPERATIONS: "Operational efficiency reached 94% with significant reduction in equipment downtime. Order volume increased 18% while maintaining 96% on-time delivery rate.",
#         Department.COMPLIANCE: "All regulatory requirements met with 12 successful audits. Issue resolution rate at 89%. Risk assessment remains at Low level with proactive monitoring in place."
#     }
#     return summaries.get(department, "Performance metrics within expected parameters.")

# def process_nlp_query(query: str, department: Optional[Department]) -> Dict[str, Any]:
#     """Process natural language queries using AI"""
#     query_lower = query.lower()
    
#     if "sales" in query_lower or "revenue" in query_lower:
#         return {
#             "answer": "Sales performance for Q2 shows 22% growth with 156 deals closed. Revenue reached $2.4M with strong pipeline of $4.2M.",
#             "chart_data": [
#                 {"month": "Jan", "sales": 540},
#                 {"month": "Feb", "sales": 675},
#                 {"month": "Mar", "sales": 756},
#                 {"month": "Apr", "sales": 594},
#                 {"month": "May", "sales": 810},
#                 {"month": "Jun", "sales": 837}
#             ],
#             "insights": [
#                 "Technology sector led growth with 28% increase",
#                 "Average deal size increased from $25K to $27K",
#                 "Conversion rate improved to 34%"
#             ],
#             "recommendations": [
#                 "Invest in high-performing sales channels",
#                 "Expand sales team in technology vertical"
#             ]
#         }
#     elif "hr" in query_lower or "employee" in query_lower or "attrition" in query_lower:
#         return {
#             "answer": "HR metrics show positive trends with attrition decreasing to 8.2% and employee satisfaction at 87%.",
#             "chart_data": [
#                 {"month": "Jan", "hires": 5, "exits": 3},
#                 {"month": "Feb", "hires": 8, "exits": 2},
#                 {"month": "Mar", "hires": 6, "exits": 4},
#                 {"month": "Apr", "hires": 7, "exits": 3},
#                 {"month": "May", "hires": 9, "exits": 5},
#                 {"month": "Jun", "hires": 4, "exits": 3}
#             ],
#             "insights": [
#                 "Net workforce growth of 5.2%",
#                 "Wellness programs contributed to improved satisfaction",
#                 "Retention in key departments above 95%"
#             ],
#             "recommendations": [
#                 "Continue investment in employee wellness",
#                 "Implement mentorship programs for new hires"
#             ]
#         }
#     else:
#         return {
#             "answer": "Based on current data analysis, overall business metrics show positive growth across departments with 12% average improvement.",
#             "insights": [
#                 "Revenue growth trending upward",
#                 "Operational efficiency at peak levels",
#                 "Customer satisfaction improving"
#             ],
#             "recommendations": [
#                 "Maintain current strategic initiatives",
#                 "Monitor emerging market trends"
#             ]
#         }

# # ============================================================================
# # MOCK DATA GENERATOR
# # ============================================================================

# def generate_mock_kpi_data(department: Department):
#     kpi_mapping = {
#         Department.FINANCE: {
#             "kpis": [
#                 {"label": "Total Revenue", "value": "$2.4M", "change": "+12.5%", "positive": True},
#                 {"label": "Expenses", "value": "$1.8M", "change": "+8.2%", "positive": False},
#                 {"label": "Net Profit", "value": "$600K", "change": "+18.3%", "positive": True},
#                 {"label": "Profit Margin", "value": "25%", "change": "+2.1%", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "revenue": 180, "expenses": 140},
#                 {"month": "Feb", "revenue": 200, "expenses": 150},
#                 {"month": "Mar", "revenue": 220, "expenses": 160},
#                 {"month": "Apr", "revenue": 240, "expenses": 180},
#                 {"month": "May", "revenue": 260, "expenses": 190},
#                 {"month": "Jun", "revenue": 280, "expenses": 200}
#             ],
#             "summary": "Q2 revenue grew by 12.5% with controlled expense management. Profit margins improved across all divisions."
#         },
#         Department.HR: {
#             "kpis": [
#                 {"label": "Total Employees", "value": "342", "change": "+5.2%", "positive": True},
#                 {"label": "Attrition Rate", "value": "8.2%", "change": "-1.3%", "positive": True},
#                 {"label": "New Hires", "value": "23", "change": "+15%", "positive": True},
#                 {"label": "Satisfaction", "value": "87%", "change": "+3%", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "hires": 5, "exits": 3},
#                 {"month": "Feb", "hires": 8, "exits": 2},
#                 {"month": "Mar", "hires": 6, "exits": 4},
#                 {"month": "Apr", "hires": 7, "exits": 3},
#                 {"month": "May", "hires": 9, "exits": 5},
#                 {"month": "Jun", "hires": 4, "exits": 3}
#             ],
#             "summary": "Workforce grew steadily with reduced attrition. Employee satisfaction improved through new wellness programs."
#         },
#         Department.SALES: {
#             "kpis": [
#                 {"label": "Total Deals", "value": "156", "change": "+22%", "positive": True},
#                 {"label": "Conversion Rate", "value": "34%", "change": "+5%", "positive": True},
#                 {"label": "Pipeline Value", "value": "$4.2M", "change": "+28%", "positive": True},
#                 {"label": "Avg Deal Size", "value": "$27K", "change": "+8%", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "deals": 20, "value": 540},
#                 {"month": "Feb", "deals": 25, "value": 675},
#                 {"month": "Mar", "deals": 28, "value": 756},
#                 {"month": "Apr", "deals": 22, "value": 594},
#                 {"month": "May", "deals": 30, "value": 810},
#                 {"month": "Jun", "deals": 31, "value": 837}
#             ],
#             "summary": "Outstanding sales performance with 22% growth in closed deals. Pipeline value reached all-time high."
#         },
#         Department.OPERATIONS: {
#             "kpis": [
#                 {"label": "Efficiency", "value": "94%", "change": "+2%", "positive": True},
#                 {"label": "Downtime", "value": "2.3h", "change": "-15%", "positive": True},
#                 {"label": "Orders", "value": "1,234", "change": "+18%", "positive": True},
#                 {"label": "On-Time", "value": "96%", "change": "+3%", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "efficiency": 91, "downtime": 3.2},
#                 {"month": "Feb", "efficiency": 92, "downtime": 2.8},
#                 {"month": "Mar", "efficiency": 93, "downtime": 2.5},
#                 {"month": "Apr", "efficiency": 94, "downtime": 2.3},
#                 {"month": "May", "efficiency": 94, "downtime": 2.1},
#                 {"month": "Jun", "efficiency": 95, "downtime": 1.9}
#             ],
#             "summary": "Operational efficiency improved with reduced equipment downtime. On-time delivery exceeds target."
#         },
#         Department.COMPLIANCE: {
#             "kpis": [
#                 {"label": "Audits", "value": "12", "change": "0%", "positive": True},
#                 {"label": "Open Issues", "value": "3", "change": "-40%", "positive": True},
#                 {"label": "Resolved", "value": "89%", "change": "+12%", "positive": True},
#                 {"label": "Risk Level", "value": "Low", "change": "Stable", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "audits": 2, "issues": 5},
#                 {"month": "Feb", "audits": 2, "issues": 4},
#                 {"month": "Mar", "audits": 2, "issues": 6},
#                 {"month": "Apr", "audits": 2, "issues": 5},
#                 {"month": "May", "audits": 2, "issues": 4},
#                 {"month": "Jun", "audits": 2, "issues": 3}
#             ],
#             "summary": "Compliance metrics remain strong with 89% issue resolution rate. All audits passed successfully."
#         }
#     }
#     return kpi_mapping.get(department, kpi_mapping[Department.FINANCE])

# # ============================================================================
# # API ENDPOINTS
# # ============================================================================

# @app.get("/")
# async def root():
#     return {
#         "service": "Autonomous Report Generator API with MongoDB",
#         "status": "operational",
#         "version": "1.0.0",
#         "timestamp": datetime.utcnow().isoformat()
#     }

# # ============================================================================
# # AUTHENTICATION ENDPOINTS
# # ============================================================================

# @app.post("/api/auth/register", response_model=Token)
# async def register(user_data: UserRegister, db=Depends(get_database)):
#     """Register a new user"""
#     # Check if user exists
#     existing_user = await db.users.find_one({"email": user_data.email})
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Create new user
#     user_id = str(uuid.uuid4())
#     hashed_password = get_password_hash(user_data.password)
    
#     user = {
#         "id": user_id,
#         "email": user_data.email,
#         "password": hashed_password,
#         "name": user_data.name,
#         "role": user_data.role,
#         "departments": user_data.departments,
#         "created_at": datetime.utcnow(),
#         "updated_at": datetime.utcnow()
#     }
    
#     await db.users.insert_one(user)
    
#     # Create access token
#     access_token = create_access_token({"sub": user_id})
    
#     # Return token and user info
#     user_response = {k: v for k, v in user.items() if k != "password"}
#     user_response = serialize_doc(user_response)
    
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": user_response
#     }

# @app.post("/api/auth/login", response_model=Token)
# async def login(credentials: UserLogin, db=Depends(get_database)):
#     """Login with email and password"""
#     # Find user by email
#     user = await db.users.find_one({"email": credentials.email})
    
#     if not user or not verify_password(credentials.password, user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
    
#     # Create access token
#     access_token = create_access_token({"sub": user["id"]})
    
#     # Return token and user info
#     user_response = {k: v for k, v in user.items() if k != "password"}
#     user_response = serialize_doc(user_response)
    
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "user": user_response
#     }

# @app.get("/api/auth/me")
# async def get_current_user_info(current_user: dict = Depends(get_current_user)):
#     """Get current user information"""
#     return {k: v for k, v in current_user.items() if k != "password"}

# # ============================================================================
# # DASHBOARD & KPI ENDPOINTS
# # ============================================================================

# @app.get("/api/dashboard/stats")
# async def get_dashboard_stats(
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get overall dashboard statistics"""
#     total_reports = await db.reports.count_documents({
#         "department": {"$in": current_user["departments"]}
#     })
    
#     active_alerts = await db.alerts.count_documents({
#         "department": {"$in": current_user["departments"]},
#         "acknowledged": False
#     })
    
#     recent_activities = await db.activities.find({
#         "user_id": current_user["id"]
#     }).sort("timestamp", -1).limit(5).to_list(length=5)
    
#     recent_activities = [serialize_doc(activity) for activity in recent_activities]
    
#     return {
#         "total_reports": total_reports,
#         "active_alerts": active_alerts,
#         "departments": len(current_user["departments"]),
#         "data_sources": 23,
#         "recent_activity": recent_activities
#     }

# @app.get("/api/dashboard/kpis/{department}")
# async def get_department_kpis(
#     department: Department,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Get KPIs for a specific department"""
#     if department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this department")
    
#     data = generate_mock_kpi_data(department)
#     return {
#         "department": department,
#         "kpis": data["kpis"],
#         "chart_data": data["chart_data"],
#         "summary": data["summary"],
#         "last_updated": datetime.utcnow().isoformat()
#     }

# @app.get("/api/dashboard/activity")
# async def get_recent_activity(
#     limit: int = 10,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get recent activity log"""
#     activities = await db.activities.find({
#         "user_id": current_user["id"]
#     }).sort("timestamp", -1).limit(limit).to_list(length=limit)
    
#     activities = [serialize_doc(activity) for activity in activities]
    
#     total_activities = await db.activities.count_documents({
#         "user_id": current_user["id"]
#     })
    
#     return {
#         "activities": activities,
#         "total": total_activities
#     }

# # ============================================================================
# # REPORT MANAGEMENT ENDPOINTS
# # ============================================================================

# @app.post("/api/reports/generate")
# async def generate_report(
#     report_data: ReportGenerate,
#     background_tasks: BackgroundTasks,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Generate a new report"""
#     if report_data.department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this department")
    
#     report_id = str(uuid.uuid4())
    
#     report = {
#         "id": report_id,
#         "title": report_data.title,
#         "department": report_data.department,
#         "report_type": report_data.report_type,
#         "file_url": f"/reports/{report_id}.{report_data.report_type}",
#         "size": "2.4 MB",
#         "status": "completed",
#         "created_by": current_user["id"],
#         "created_by_name": current_user["name"],
#         "created_at": datetime.utcnow(),
#         "date_range": report_data.date_range,
#         "frequency": report_data.frequency,
#         "scheduled": report_data.schedule
#     }
    
#     await db.reports.insert_one(report)
    
#     # Add to activity log
#     activity = {
#         "id": str(uuid.uuid4()),
#         "action": f"Report Generated: {report_data.title}",
#         "user_id": current_user["id"],
#         "user_name": current_user["name"],
#         "timestamp": datetime.utcnow(),
#         "type": "report_generated",
#         "department": report_data.department
#     }
    
#     await db.activities.insert_one(activity)
    
#     # If scheduled, set up background task (mock)
    
#     # if report_data.schedule:
#     #     # In production, use Celery, Airflow, or APScheduler
#     #     pass
    
#     return serialize_doc(report)

# @app.get("/api/reports")
# async def get_reports(
#     department: Optional[Department] = None,
#     limit: int = 50,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get list of reports"""
#     query = {"department": {"$in": current_user["departments"]}}
    
#     if department:
#         if department not in current_user["departments"]:
#             raise HTTPException(status_code=403, detail="Access denied to this department")
#         query["department"] = department
    
#     reports = await db.reports.find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
#     reports = [serialize_doc(report) for report in reports]
    
#     total = await db.reports.count_documents(query)
    
#     return {
#         "reports": reports,
#         "total": total
#     }

# @app.get("/api/reports/{report_id}")
# async def get_report(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get specific report details"""
#     report = await db.reports.find_one({"id": report_id})
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     if report["department"] not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this report")
    
#     return serialize_doc(report)

# @app.delete("/api/reports/{report_id}")
# async def delete_report(
#     report_id: str,
#     current_user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER])),
#     db=Depends(get_database)
# ):
#     """Delete a report (Admin/Manager only)"""
#     report = await db.reports.find_one({"id": report_id})
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     await db.reports.delete_one({"id": report_id})
    
#     # Also delete related comments
#     await db.comments.delete_many({"report_id": report_id})
    
#     return {"message": "Report deleted successfully", "report_id": report_id}

# @app.get("/api/reports/{report_id}/download")
# async def download_report(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Download report file"""
#     report = await db.reports.find_one({"id": report_id})
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     if report["department"] not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this report")
    
#     # In production, return actual file from S3/storage
#     return {
#         "download_url": report["file_url"],
#         "filename": f"{report['title']}.{report['report_type']}",
#         "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
#     }

# # ============================================================================
# # NLP QUERY ENGINE ENDPOINTS
# # ============================================================================
# @app.post("/api/query", response_model=QueryResponse)
# async def process_query(
#     query_data: NLPQuery,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Process natural language query using LLaMA Agent"""
#     if query_data.department and query_data.department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this department")
    
#     try:
#         # Get LLaMA agent
#         agent = get_llama_agent()
        
#         # Prepare context
#         context = {
#             "department": query_data.department,
#             "user_role": current_user["role"],
#             "query_context": query_data.context or {}
#         }
        
#         # Add department data if specified
#         if query_data.department:
#             dept_data = generate_mock_kpi_data(query_data.department)
#             context["kpis"] = dept_data["kpis"]
#             context["chart_data"] = dept_data["chart_data"]
        
#         # Process with LLaMA agent
#         result = agent.process_query(query_data.query, context)
        
#         # Log activity
#         await activities_collection.insert_one({
#             "action": f"LLaMA Query: {query_data.query[:50]}...",
#             "user": current_user["name"],
#             "timestamp": datetime.utcnow(),
#             "type": "llama_query_processed"
#         })
        
#         return {
#             "query": query_data.query,
#             "answer": result["answer"],
#             "insights": result.get("insights", []),
#             "chart_data": result.get("chart_data"),
#             "recommendations": result.get("recommendations", [])
#         }
        
#     except Exception as e:
#         logger.error(f"Query processing error: {str(e)}")
#         raise HTTPException(status_code=500, detail="Error processing query")
# # @app.post("/api/query", response_model=QueryResponse)
# # async def process_query(
# #     query_data: NLPQuery,
# #     current_user: dict = Depends(get_current_user),
# #     db=Depends(get_database)
# # ):
# #     """Process natural language query and return insights"""
# #     # Check department access if specified
# #     if query_data.department and query_data.department not in current_user["departments"]:
# #         raise HTTPException(status_code=403, detail="Access denied to this department")
    
# #     # Process query with AI
# #     result = process_nlp_query(query_data.query, query_data.department)
    
# #     # Log activity
# #     activity = {
# #         "id": str(uuid.uuid4()),
# #         "action": f"Query Processed: {query_data.query[:50]}...",
# #         "user_id": current_user["id"],
# #         "user_name": current_user["name"],
# #         "timestamp": datetime.utcnow(),
# #         "type": "query_processed",
# #         "department": query_data.department
# #     }
    
# #     await db.activities.insert_one(activity)
    
# #     return {
# #         "query": query_data.query,
# #         "answer": result["answer"],
# #         "insights": result.get("insights", []),
# #         "chart_data": result.get("chart_data"),
# #         "recommendations": result.get("recommendations")
# #     }

# @app.post("/api/query/voice")
# async def process_voice_query(
#     audio_file: UploadFile = File(...),
#     department: Optional[Department] = None,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Process voice query"""
#     # Mock voice-to-text conversion
#     transcribed_text = "What was the Q2 sales growth?"
    
#     # Process as normal query
#     result = process_nlp_query(transcribed_text, department)
    
#     return {
#         "transcription": transcribed_text,
#         "query": transcribed_text,
#         "answer": result["answer"],
#         "insights": result.get("insights", []),
#         "chart_data": result.get("chart_data"),
#         "recommendations": result.get("recommendations")
#     }

# # ============================================================================
# # ALERTS & NOTIFICATIONS ENDPOINTS
# # ============================================================================

# @app.get("/api/alerts")
# async def get_alerts(
#     acknowledged: Optional[bool] = None,
#     priority: Optional[AlertPriority] = None,
#     limit: int = 50,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get alerts"""
#     query = {"department": {"$in": current_user["departments"]}}
    
#     # Apply filters
#     if acknowledged is not None:
#         query["acknowledged"] = acknowledged
    
#     if priority:
#         query["priority"] = priority
    
#     alerts = await db.alerts.find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
#     alerts = [serialize_doc(alert) for alert in alerts]
    
#     total = await db.alerts.count_documents(query)
#     unacknowledged = await db.alerts.count_documents({
#         "department": {"$in": current_user["departments"]},
#         "acknowledged": False
#     })
    
#     return {
#         "alerts": alerts,
#         "total": total,
#         "unacknowledged": unacknowledged
#     }

# @app.post("/api/alerts/{alert_id}/acknowledge")
# async def acknowledge_alert(
#     alert_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Acknowledge an alert"""
#     alert = await db.alerts.find_one({"id": alert_id})
    
#     if not alert:
#         raise HTTPException(status_code=404, detail="Alert not found")
    
#     if alert["department"] not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this alert")
    
#     updated_alert = await db.alerts.find_one_and_update(
#         {"id": alert_id},
#         {
#             "$set": {
#                 "acknowledged": True,
#                 "acknowledged_by": current_user["name"],
#                 "acknowledged_at": datetime.utcnow()
#             }
#         },
#         return_document=ReturnDocument.AFTER
#     )
    
#     return {"message": "Alert acknowledged", "alert": serialize_doc(updated_alert)}

# @app.post("/api/alerts/create")
# async def create_alert(
#     alert_data: dict,
#     current_user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER])),
#     db=Depends(get_database)
# ):
#     """Create a new alert (Admin/Manager only)"""
#     alert_id = str(uuid.uuid4())
    
#     alert = {
#         "id": alert_id,
#         "type": alert_data.get("type", "info"),
#         "department": alert_data["department"],
#         "message": alert_data["message"],
#         "priority": alert_data.get("priority", AlertPriority.MEDIUM),
#         "created_at": datetime.utcnow(),
#         "acknowledged": False,
#         "created_by": current_user["id"]
#     }
    
#     await db.alerts.insert_one(alert)
    
#     # In production, send notifications via email/Slack/Teams
#     # await send_notification(alert)
    
#     return serialize_doc(alert)

# # ============================================================================
# # COMMENTS & COLLABORATION ENDPOINTS
# # ============================================================================

# @app.post("/api/comments", response_model=Comment)
# async def create_comment(
#     comment_data: CommentCreate,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Add a comment to a report"""
#     report = await db.reports.find_one({"id": comment_data.report_id})
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     if report["department"] not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this report")
    
#     comment_id = str(uuid.uuid4())
    
#     comment = {
#         "id": comment_id,
#         "report_id": comment_data.report_id,
#         "user_id": current_user["id"],
#         "user_name": current_user["name"],
#         "content": comment_data.content,
#         "mentioned_users": comment_data.mentioned_users,
#         "created_at": datetime.utcnow(),
#         "replies": []
#     }
    
#     await db.comments.insert_one(comment)
    
#     # Send notifications to mentioned users (mock)
#     # In production, send email/Slack notifications to @mentioned users
    
#     return serialize_doc(comment)

# @app.get("/api/comments/{report_id}")
# async def get_comments(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get all comments for a report"""
#     report = await db.reports.find_one({"id": report_id})
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     if report["department"] not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this report")
    
#     comments = await db.comments.find({"report_id": report_id}).sort("created_at", 1).to_list(length=None)
#     comments = [serialize_doc(comment) for comment in comments]
    
#     return {
#         "comments": comments,
#         "total": len(comments)
#     }

# @app.post("/api/comments/{comment_id}/reply")
# async def reply_to_comment(
#     comment_id: str,
#     reply_data: dict,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Reply to a comment"""
#     comment = await db.comments.find_one({"id": comment_id})
    
#     if not comment:
#         raise HTTPException(status_code=404, detail="Comment not found")
    
#     reply = {
#         "id": str(uuid.uuid4()),
#         "user_id": current_user["id"],
#         "user_name": current_user["name"],
#         "content": reply_data["content"],
#         "created_at": datetime.utcnow()
#     }
    
#     updated_comment = await db.comments.find_one_and_update(
#         {"id": comment_id},
#         {"$push": {"replies": reply}},
#         return_document=ReturnDocument.AFTER
#     )
    
#     return {"message": "Reply added", "reply": reply, "comment": serialize_doc(updated_comment)}

# @app.delete("/api/comments/{comment_id}")
# async def delete_comment(
#     comment_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Delete a comment"""
#     comment = await db.comments.find_one({"id": comment_id})
    
#     if not comment:
#         raise HTTPException(status_code=404, detail="Comment not found")
    
#     # Only allow deletion if user is comment author or admin
#     if comment["user_id"] != current_user["id"] and current_user["role"] != UserRole.ADMIN:
#         raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
#     await db.comments.delete_one({"id": comment_id})
    
#     return {"message": "Comment deleted successfully"}

# # ============================================================================
# # SETTINGS & PREFERENCES ENDPOINTS
# # ============================================================================

# @app.get("/api/settings")
# async def get_user_settings(
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get user settings"""
#     settings = await db.settings.find_one({"user_id": current_user["id"]})
    
#     if not settings:
#         # Return default settings
#         return {
#             "language": "english",
#             "theme": "light",
#             "report_format": "pdf",
#             "notifications": {
#                 "email": True,
#                 "slack": False,
#                 "teams": False
#             }
#         }
    
#     return serialize_doc(settings)

# @app.put("/api/settings")
# async def update_user_settings(
#     settings: UserSettings,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Update user settings"""
#     user_id = current_user["id"]
    
#     settings_dict = settings.dict()
#     settings_dict["user_id"] = user_id
#     settings_dict["updated_at"] = datetime.utcnow()
    
#     # Upsert settings
#     await db.settings.update_one(
#         {"user_id": user_id},
#         {"$set": settings_dict},
#         upsert=True
#     )
    
#     updated_settings = await db.settings.find_one({"user_id": user_id})
    
#     return {"message": "Settings updated successfully", "settings": serialize_doc(updated_settings)}

# @app.post("/api/settings/integrations/{service}")
# async def setup_integration(
#     service: str,
#     integration_data: dict,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Setup integration with external services (Slack, Teams, Email)"""
#     user_id = current_user["id"]
    
#     settings = await db.settings.find_one({"user_id": user_id})
#     if not settings:
#         settings = UserSettings().dict()
#         settings["user_id"] = user_id
#         await db.settings.insert_one(settings)
    
#     update_data = {}
    
#     # Validate and store integration credentials
#     if service == "slack":
#         update_data["notifications.slack"] = True
#         update_data["slack_webhook"] = integration_data.get("webhook_url")
#     elif service == "teams":
#         update_data["notifications.teams"] = True
#         update_data["teams_webhook"] = integration_data.get("webhook_url")
#     elif service == "email":
#         update_data["notifications.email"] = True
#         update_data["email_address"] = integration_data.get("email")
#     else:
#         raise HTTPException(status_code=400, detail="Invalid service")
    
#     update_data["updated_at"] = datetime.utcnow()
    
#     await db.settings.update_one(
#         {"user_id": user_id},
#         {"$set": update_data}
#     )
    
#     return {
#         "message": f"{service.capitalize()} integration configured successfully",
#         "service": service
#     }

# # ============================================================================
# # DATA INGESTION ENDPOINTS
# # ============================================================================

# @app.post("/api/data/upload")
# async def upload_data(
#     file: UploadFile = File(...),
#     department: Department = None,
#     current_user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER])),
#     db=Depends(get_database)
# ):
#     """Upload CSV/Excel data for processing"""
#     if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
#         raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
#     try:
#         # Read file content
#         content = await file.read()
        
#         # Parse based on file type
#         if file.filename.endswith('.csv'):
#             df = pd.read_csv(StringIO(content.decode('utf-8')))
#         else:
#             df = pd.read_excel(content)
        
#         # Basic data validation and cleaning
#         df = df.dropna(how='all')  # Remove empty rows
        
#         # Store processed data
#         data_id = str(uuid.uuid4())
        
#         data_record = {
#             "id": data_id,
#             "filename": file.filename,
#             "department": department,
#             "uploaded_by": current_user["id"],
#             "uploaded_at": datetime.utcnow(),
#             "rows": len(df),
#             "columns": list(df.columns),
#             "preview": df.head(5).to_dict('records'),
#             "processed": False
#         }
        
#         await db.data_uploads.insert_one(data_record)
        
#         # Log activity
#         activity = {
#             "id": str(uuid.uuid4()),
#             "action": f"Data Uploaded: {file.filename}",
#             "user_id": current_user["id"],
#             "user_name": current_user["name"],
#             "timestamp": datetime.utcnow(),
#             "type": "data_upload",
#             "department": department
#         }
        
#         await db.activities.insert_one(activity)
        
#         return {
#             "message": "Data uploaded successfully",
#             "data_id": data_id,
#             "rows": len(df),
#             "columns": list(df.columns),
#             "preview": df.head(5).to_dict('records')
#         }
    
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

# @app.get("/api/data/sources")
# async def get_data_sources(
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get list of connected data sources"""
#     # Mock data sources
#     sources = [
#         {"id": "1", "name": "PostgreSQL - Main DB", "type": "database", "status": "connected"},
#         {"id": "2", "name": "Salesforce CRM", "type": "api", "status": "connected"},
#         {"id": "3", "name": "SAP ERP", "type": "api", "status": "connected"},
#         {"id": "4", "name": "MongoDB - Analytics", "type": "database", "status": "connected"},
#         {"id": "5", "name": "Google Sheets", "type": "spreadsheet", "status": "connected"}
#     ]
    
#     return {"sources": sources, "total": len(sources)}

# # ============================================================================
# # ANALYTICS & INSIGHTS ENDPOINTS
# # ============================================================================

# # @app.post("/api/analytics/forecast")
# # async def generate_forecast(
# #     forecast_data: dict,
# #     current_user: dict = Depends(get_current_user)
# # ):
# #     """Generate forecasting predictions using ML"""
# #     department = forecast_data.get("department")
# #     metric = forecast_data.get("metric")
# #     periods = forecast_data.get("periods", 6)
    
# #     if department not in current_user["departments"]:
# #         raise HTTPException(status_code=403, detail="Access denied to this department")
    
# #     # Mock forecast data
# #     forecast = []
# #     base_value = 200
    
# #     for i in range(periods):
# #         forecast.append({
# #             "period": f"Month {i+1}",
# #             "predicted_value": base_value + (i * 20) + (i * 5),
# #             "lower_bound": base_value + (i * 15),
# #             "upper_bound": base_value + (i * 25),
# #             "confidence": 0.85 - (i * 0.05)
# #         })
    
# #     return {
# #         "department": department,
# #         "metric": metric,
# #         "forecast": forecast,
# #         "model": "Prophet",
# #         "accuracy": 0.87
# #     }
# @app.post("/api/analytics/llama-analysis")
# async def llama_comprehensive_analysis(
#     request_data: dict,
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Comprehensive department analysis using LLaMA Agent
#     """
#     department = request_data.get("department")
    
#     if department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied")
    
#     try:
#         # Get analysis agent
#         analysis_agent = get_analysis_agent()
        
#         # Get department data
#         dept_data = generate_mock_kpi_data(department)
        
#         # Perform comprehensive analysis
#         result = analysis_agent.analyze_department_performance(
#             department=department,
#             kpis=dept_data["kpis"],
#             chart_data=dept_data["chart_data"]
#         )
        
#         return {
#             "department": department,
#             "analysis": result,
#             "generated_at": datetime.utcnow().isoformat()
#         }
        
#     except Exception as e:
#         logger.error(f"Comprehensive analysis error: {str(e)}")
#         raise HTTPException(status_code=500, detail="Analysis error")
# @app.get("/api/analytics/anomalies/{department}")
# async def detect_department_anomalies(
#     department: Department,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Detect anomalies in department data"""
#     if department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this department")
    
#     # Get department data
#     dept_data = generate_mock_kpi_data(department)
    
#     # Mock anomaly detection
#     anomalies = [
#         {
#             "id": str(uuid.uuid4()),
#             "metric": "expenses",
#             "type": "spike",
#             "severity": "medium",
#             "description": "Unusual 15% increase in expenses detected",
#             "detected_at": datetime.utcnow().isoformat(),
#             "value": "+15%",
#             "expected_range": "5-10%"
#         }
#     ]
    
#     return {
#         "department": department,
#         "anomalies": anomalies,
#         "total": len(anomalies),
#         "last_checked": datetime.utcnow().isoformat()
#     }

# @app.post("/api/analytics/recommendations")
# async def generate_recommendations(
#     request_data: dict,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Generate AI-powered recommendations"""
#     department = request_data.get("department")
    
#     if department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this department")
    
#     # Mock recommendations using AI
#     recommendations = [
#         {
#             "id": str(uuid.uuid4()),
#             "title": "Optimize Marketing Spend",
#             "description": "Based on ROI analysis, reduce marketing budget in underperforming channels by 12% and reallocate to high-performing digital channels.",
#             "priority": "high",
#             "potential_impact": "+$120K annual savings",
#             "confidence": 0.89
#         },
#         {
#             "id": str(uuid.uuid4()),
#             "title": "Improve Employee Retention",
#             "description": "Implement mentorship programs and flexible work arrangements to reduce attrition rate from 8.2% to 6%.",
#             "priority": "medium",
#             "potential_impact": "-2.2% attrition rate",
#             "confidence": 0.82
#         },
#         {
#             "id": str(uuid.uuid4()),
#             "title": "Expand Technology Sector",
#             "description": "Technology sector shows 28% growth. Consider expanding sales team and product offerings in this vertical.",
#             "priority": "high",
#             "potential_impact": "+$500K revenue potential",
#             "confidence": 0.91
#         }
#     ]
    
#     return {
#         "department": department,
#         "recommendations": recommendations,
#         "generated_at": datetime.utcnow().isoformat()
#     }

# # ============================================================================
# # SCHEDULING & AUTOMATION ENDPOINTS
# # ============================================================================

# @app.post("/api/schedule/report")
# async def schedule_report(
#     schedule_data: dict,
#     current_user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER])),
#     db=Depends(get_database)
# ):
#     """Schedule automated report generation"""
#     schedule_id = str(uuid.uuid4())
    
#     schedule = {
#         "id": schedule_id,
#         "report_title": schedule_data["title"],
#         "department": schedule_data["department"],
#         "frequency": schedule_data["frequency"],
#         "report_type": schedule_data["report_type"],
#         "recipients": schedule_data.get("recipients", []),
#         "delivery_channels": schedule_data.get("channels", ["email"]),
#         "next_run": datetime.utcnow(),
#         "created_by": current_user["id"],
#         "active": True,
#         "created_at": datetime.utcnow()
#     }
    
#     await db.schedules.insert_one(schedule)
    
#     # In production, use Celery, APScheduler, or Airflow
#     # scheduler.add_job(generate_scheduled_report, trigger='cron', args=[schedule])
    
#     return {
#         "message": "Report scheduled successfully",
#         "schedule": serialize_doc(schedule)
#     }

# @app.get("/api/schedule/list")
# async def get_scheduled_reports(
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get list of scheduled reports"""
#     schedules = await db.schedules.find({
#         "created_by": current_user["id"]
#     }).sort("created_at", -1).to_list(length=None)
    
#     schedules = [serialize_doc(schedule) for schedule in schedules]
    
#     return {"schedules": schedules, "total": len(schedules)}

# @app.delete("/api/schedule/{schedule_id}")
# async def cancel_scheduled_report(
#     schedule_id: str,
#     current_user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER])),
#     db=Depends(get_database)
# ):
#     """Cancel a scheduled report"""
#     result = await db.schedules.delete_one({"id": schedule_id})
    
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Scheduled report not found")
    
#     return {"message": "Scheduled report cancelled", "schedule_id": schedule_id}

# # ============================================================================
# # ADMIN ENDPOINTS
# # ============================================================================

# @app.get("/api/admin/users")
# async def get_all_users(
#     current_user: dict = Depends(check_role([UserRole.ADMIN])),
#     db=Depends(get_database)
# ):
#     """Get all users (Admin only)"""
#     users = await db.users.find({}).to_list(length=None)
#     users = [{k: v for k, v in serialize_doc(user).items() if k != "password"} for user in users]
    
#     return {"users": users, "total": len(users)}

# @app.put("/api/admin/users/{user_id}/role")
# async def update_user_role(
#     user_id: str,
#     role_data: dict,
#     current_user: dict = Depends(check_role([UserRole.ADMIN])),
#     db=Depends(get_database)
# ):
#     """Update user role (Admin only)"""
#     user = await db.users.find_one({"id": user_id})
    
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     updated_user = await db.users.find_one_and_update(
#         {"id": user_id},
#         {
#             "$set": {
#                 "role": role_data["role"],
#                 "updated_at": datetime.utcnow()
#             }
#         },
#         return_document=ReturnDocument.AFTER
#     )
    
#     user_response = {k: v for k, v in serialize_doc(updated_user).items() if k != "password"}
    
#     return {"message": "User role updated", "user": user_response}

# @app.delete("/api/admin/users/{user_id}")
# async def delete_user(
#     user_id: str,
#     current_user: dict = Depends(check_role([UserRole.ADMIN])),
#     db=Depends(get_database)
# ):
#     """Delete user (Admin only)"""
#     user = await db.users.find_one({"id": user_id})
    
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     await db.users.delete_one({"id": user_id})
    
#     # Also delete user's settings, activities, etc.
#     await db.settings.delete_one({"user_id": user_id})
#     await db.activities.delete_many({"user_id": user_id})
    
#     return {"message": "User deleted successfully"}

# # ============================================================================
# # NOTIFICATION SERVICES (Helper Functions)
# # ============================================================================

# async def send_email_notification(recipient: str, subject: str, body: str):
#     """Send email notification using SMTP"""
#     # In production, use SMTP library or SendGrid/AWS SES
#     print(f"Sending email to {recipient}: {subject}")
#     pass

# async def send_slack_notification(webhook_url: str, message: str):
#     """Send Slack notification"""
#     # In production, use requests library to post to Slack webhook
#     print(f"Sending Slack message: {message}")
#     pass

# async def send_teams_notification(webhook_url: str, message: str):
#     """Send Microsoft Teams notification"""
#     # In production, use requests library to post to Teams webhook
#     print(f"Sending Teams message: {message}")
#     pass





# # //////////////////////////////////////////////////////



# # ============================================================================
# # NEW CSV PROCESSING & PDF GENERATION ENDPOINTS
# # ============================================================================

# @app.post("/api/reports/upload-csv")

# async def upload_csv_analysis(
#     file: UploadFile = File(...),
#     department: Department = None,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Upload CSV for AI analysis and report generation"""
#     try:
#         if not file.filename.endswith('.csv'):
#             raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
#         # Read and parse CSV
#         content = await file.read()
#         csv_text = content.decode('utf-8')
#         df = pd.read_csv(io.StringIO(csv_text))
        
#         # Basic data validation
#         if df.empty:
#             raise HTTPException(status_code=400, detail="CSV file is empty")
        
#         # Convert DataFrame to list of dictionaries for AI processing
#         data_records = df.to_dict('records')
        
#         # Get AI agents
#         llama_agent = get_llama_agent()
#         analysis_agent = get_analysis_agent()
        
#         # Prepare context for AI analysis
#         context = {
#             "department": department,
#             "data_preview": data_records[:5],  # First 5 records for context
#             "columns": list(df.columns),
#             "total_records": len(df),
#             "data_summary": {
#                 "columns": list(df.columns),
#                 "total_rows": len(df),
#                 "data_types": df.dtypes.to_dict()
#             }
#         }
        
#         # Generate AI analysis
#         analysis_result = analysis_agent.analyze_department_performance(
#             department=department,
#             kpis=[{"label": col, "value": "Analyzing...", "change": "0%", "positive": True} for col in df.columns[:4]],
#             chart_data=data_records[:10]  # Use first 10 records for chart data
#         )
        
#         # Generate PDF report
#         pdf_report = await generate_pdf_report(
#             department=department,
#             filename=file.filename,
#             data_preview=data_records[:10],
#             analysis_result=analysis_result,
#             user_name=current_user["name"]
#         )
        
#         # Store report in database
#         report_id = str(uuid.uuid4())
#         report_data = {
#             "id": report_id,
#             "title": f"AI Analysis - {file.filename}",
#             "department": department,
#             "report_type": ReportType.PDF,
#             "file_url": f"/api/reports/download/{report_id}",
#             "size": f"{(len(content) / 1024 / 1024):.1f} MB",
#             "status": "completed",
#             "created_by": current_user["id"],
#             "created_by_name": current_user["name"],
#             "created_at": datetime.utcnow(),
#             "source": "csv_upload",
#             "original_filename": file.filename,
#             "analysis_data": analysis_result
#         }
        
#         await db.reports.insert_one(report_data)
        
#         # Store PDF file (in production, use cloud storage)
#         await db.report_files.insert_one({
#             "report_id": report_id,
#             "pdf_content": base64.b64encode(pdf_report).decode('utf-8'),
#             "created_at": datetime.utcnow()
#         })
        
#         # Log activity
#         activity = {
#             "id": str(uuid.uuid4()),
#             "action": f"CSV Analysis Report Generated: {file.filename}",
#             "user_id": current_user["id"],
#             "user_name": current_user["name"],
#             "timestamp": datetime.utcnow(),
#             "type": "csv_analysis",
#             "department": department
#         }
#         await db.activities.insert_one(activity)
        
#         return {
#             "message": "CSV analyzed and report generated successfully",
#             "report_id": report_id,
#             "analysis": analysis_result,
#             "data_preview": {
#                 "columns": list(df.columns),
#                 "first_five_rows": data_records[:5],
#                 "total_rows": len(df)
#             }
#         }
        
#     except Exception as e:
#         logger.error(f"CSV processing error: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

# async def generate_pdf_report(department: str, filename: str, data_preview: List[Dict], 
#                             analysis_result: Dict, user_name: str) -> bytes:
#     """Generate PDF report from AI analysis"""
#     try:
#         # Create a buffer for PDF
#         buffer = io.BytesIO()
        
#         # Create PDF document
#         doc = SimpleDocTemplate(buffer, pagesize=letter, 
#                               topMargin=0.5*inch, bottomMargin=0.5*inch,
#                               leftMargin=0.5*inch, rightMargin=0.5*inch)
        
#         # Story to hold PDF elements
#         story = []
#         styles = getSampleStyleSheet()
        
#         # Title
#         title_style = ParagraphStyle(
#             'CustomTitle',
#             parent=styles['Heading1'],
#             fontSize=18,
#             spaceAfter=30,
#             textColor=colors.HexColor('#1E40AF')
#         )
#         title = Paragraph(f"AI Analysis Report - {department.title()} Department", title_style)
#         story.append(title)
        
#         # File info
#         info_style = ParagraphStyle(
#             'InfoStyle',
#             parent=styles['Normal'],
#             fontSize=10,
#             textColor=colors.gray
#         )
#         story.append(Paragraph(f"<b>File:</b> {filename}", info_style))
#         story.append(Paragraph(f"<b>Generated by:</b> {user_name}", info_style))
#         story.append(Paragraph(f"<b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}", info_style))
#         story.append(Spacer(1, 20))
        
#         # Executive Summary
#         story.append(Paragraph("<b>Executive Summary</b>", styles['Heading2']))
#         summary_text = analysis_result.get('summary', 'No summary available.')
#         story.append(Paragraph(summary_text, styles['Normal']))
#         story.append(Spacer(1, 15))
        
#         # Key Insights
#         story.append(Paragraph("<b>Key Insights</b>", styles['Heading2']))
#         insights = analysis_result.get('insights', [])
#         for insight in insights:
#             story.append(Paragraph(f"• {insight}", styles['Normal']))
#         story.append(Spacer(1, 15))
        
#         # Recommendations
#         story.append(Paragraph("<b>Recommendations</b>", styles['Heading2']))
#         recommendations = analysis_result.get('recommendations', [])
#         for rec in recommendations:
#             story.append(Paragraph(f"• {rec}", styles['Normal']))
#         story.append(Spacer(1, 15))
        
#         # Data Preview
#         if data_preview and len(data_preview) > 0:
#             story.append(Paragraph("<b>Data Preview (First 10 Rows)</b>", styles['Heading2']))
            
#             # Create table data
#             table_data = [list(data_preview[0].keys())]  # Headers
#             for row in data_preview[:10]:
#                 table_data.append([str(val) for val in row.values()])
            
#             # Create table
#             table = Table(table_data, repeatRows=1)
#             table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, 0), 10),
#                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                 ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#                 ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                 ('FONTSIZE', (0, 1), (-1, -1), 8),
#                 ('GRID', (0, 0), (-1, -1), 1, colors.black)
#             ]))
#             story.append(table)
#             story.append(Spacer(1, 15))
        
#         # Trends Analysis
#         trends = analysis_result.get('trends', {})
#         if trends:
#             story.append(Paragraph("<b>Trend Analysis</b>", styles['Heading2']))
#             trend_text = f"Overall Trend: {trends.get('trend', 'N/A')} | Confidence: {trends.get('confidence', 'N/A')}"
#             story.append(Paragraph(trend_text, styles['Normal']))
#             story.append(Paragraph(f"Pattern: {trends.get('pattern', 'N/A')}", styles['Normal']))
#             story.append(Paragraph(f"Prediction: {trends.get('prediction', 'N/A')}", styles['Normal']))
#             story.append(Spacer(1, 15))
        
#         # Anomalies
#         anomalies = analysis_result.get('anomalies', [])
#         if anomalies:
#             story.append(Paragraph("<b>Detected Anomalies</b>", styles['Heading2']))
#             for anomaly in anomalies[:5]:  # Show first 5 anomalies
#                 story.append(Paragraph(f"• {anomaly.get('description', 'N/A')} (Severity: {anomaly.get('severity', 'N/A')})", styles['Normal']))
        
#         # Build PDF
#         doc.build(story)
        
#         # Get PDF bytes
#         pdf_bytes = buffer.getvalue()
#         buffer.close()
        
#         return pdf_bytes
        
#     except Exception as e:
#         logger.error(f"PDF generation error: {str(e)}")
#         # Return a simple error PDF
#         return generate_error_pdf(str(e))

# def generate_error_pdf(error_message: str) -> bytes:
#     """Generate a simple error PDF"""
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     story = []
#     styles = getSampleStyleSheet()
    
#     story.append(Paragraph("Error Generating Report", styles['Heading1']))
#     story.append(Spacer(1, 20))
#     story.append(Paragraph(f"Error: {error_message}", styles['Normal']))
    
#     doc.build(story)
#     pdf_bytes = buffer.getvalue()
#     buffer.close()
#     return pdf_bytes

# @app.get("/api/reports/download/{report_id}")
# async def download_report_pdf(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Download generated PDF report"""
#     try:
#         # Get report metadata
#         report = await db.reports.find_one({"id": report_id})
#         if not report:
#             raise HTTPException(status_code=404, detail="Report not found")
        
#         if report["department"] not in current_user["departments"]:
#             raise HTTPException(status_code=403, detail="Access denied")
        
#         # Get PDF content
#         pdf_file = await db.report_files.find_one({"report_id": report_id})
#         if not pdf_file:
#             raise HTTPException(status_code=404, detail="PDF file not found")
        
#         # Decode PDF content
#         pdf_content = base64.b64decode(pdf_file["pdf_content"])
        
#         # Return PDF file
#         from fastapi.responses import Response
#         return Response(
#             content=pdf_content,
#             media_type="application/pdf",
#             headers={
#                 "Content-Disposition": f"attachment; filename={report['title']}.pdf",
#                 "Content-Length": str(len(pdf_content))
#             }
#         )
        
#     except Exception as e:
#         logger.error(f"PDF download error: {str(e)}")
#         raise HTTPException(status_code=500, detail="Error downloading PDF")

# @app.get("/api/reports/{report_id}/preview")
# async def preview_report(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get report preview and analysis data"""
#     report = await db.reports.find_one({"id": report_id})
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     if report["department"] not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied")
    
#     return {
#         "report": serialize_doc(report),
#         "analysis": report.get("analysis_data", {})
#     }

# # Update the database indexes function
# async def create_indexes(db):
#     """Create database indexes for better performance"""
#     # Existing indexes...
#     await db.users.create_index("email", unique=True)
#     await db.users.create_index("role")
#     await db.users.create_index("departments")
    
#     await db.reports.create_index("department")
#     await db.reports.create_index("created_by")
#     await db.reports.create_index("created_at")
#     await db.reports.create_index([("department", 1), ("created_at", -1)])
    
#     await db.alerts.create_index("department")
#     await db.alerts.create_index("priority")
#     await db.alerts.create_index("acknowledged")
#     await db.alerts.create_index("created_at")
    
#     await db.comments.create_index("report_id")
#     await db.comments.create_index("user_id")
#     await db.comments.create_index("created_at")
    
#     await db.activities.create_index("user_id")
#     await db.activities.create_index("timestamp")
    
#     # New indexes for report files
#     await db.report_files.create_index("report_id", unique=True)
#     await db.report_files.create_index("created_at")
    
#     # New collection for data uploads
#     await db.data_uploads.create_index("uploaded_by")
#     await db.data_uploads.create_index("department")
#     await db.data_uploads.create_index("uploaded_at")
    
#     print("✅ Database indexes created")





# # ============================================================================
# # MAIN ENTRY POINT
# # ============================================================================

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 

 











# ============================================================================
# AUTONOMOUS REPORT GENERATOR - BACKEND API WITH MONGODB
# Framework: FastAPI (Python)
# Database: MongoDB Atlas
# Features: JWT Auth, AI Analysis, Report Generation, NLP Queries, Alerts
# ============================================================================

# import os
# from typing import Optional, List, Dict, Any
# from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, BackgroundTasks, Request, Form
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, EmailStr, Field
# from datetime import datetime, timedelta
# from passlib.context import CryptContext
# import jwt
# import json
# from enum import Enum
# import pandas as pd
# from io import StringIO
# import uuid
# import io
# import base64
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib import colors
# from reportlab.lib.units import inch
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# import tempfile
# import logging

# # AI Agents
# from ai_models.llama_agent import get_llama_agent
# from ai_models.analysis_agent import get_analysis_agent

# # MongoDB
# from motor.motor_asyncio import AsyncIOMotorClient
# from bson import ObjectId
# from pymongo import ReturnDocument
# from fastapi.responses import JSONResponse

# # ============================================================================
# # LOGGING CONFIGURATION
# # ============================================================================

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # ============================================================================
# # LIFESPAN & APP INITIALIZATION
# # ============================================================================

# from contextlib import asynccontextmanager
# from dotenv import load_dotenv

# load_dotenv()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup: Initialize MongoDB connection
#     print("✅ Initializing Backend API with MongoDB...")
    
#     # Initialize MongoDB connection
#     app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
#     app.mongodb = app.mongodb_client[os.getenv("MONGODB_DB_NAME", "report_generator")]
    
#     # Create indexes
#     await create_indexes(app.mongodb)
    
#     # Create default admin user if not exists
#     admin_user = await app.mongodb.users.find_one({"email": "admin@company.com"})
#     if not admin_user:
#         admin_id = str(uuid.uuid4())
#         admin_user = {
#             "id": admin_id,
#             "email": "admin@company.com",
#             "password": get_password_hash("admin123"),
#             "name": "Admin User",
#             "role": UserRole.ADMIN,
#             "departments": [Department.FINANCE, Department.HR, Department.SALES, 
#                            Department.OPERATIONS, Department.COMPLIANCE],
#             "created_at": datetime.utcnow(),
#             "updated_at": datetime.utcnow()
#         }
#         await app.mongodb.users.insert_one(admin_user)
#         print("📧 Default admin created: admin@company.com / admin123")
    
#     # Create sample alerts if none exist
#     alerts_count = await app.mongodb.alerts.count_documents({})
#     if alerts_count == 0:
#         sample_alerts = []
#         for i in range(4):
#             alert_id = str(uuid.uuid4())
#             sample_alerts.append({
#                 "id": alert_id,
#                 "type": ["warning", "info", "success"][i % 3],
#                 "department": [Department.FINANCE, Department.HR, Department.SALES, Department.OPERATIONS][i],
#                 "message": f"Sample alert message {i+1}",
#                 "priority": [AlertPriority.HIGH, AlertPriority.MEDIUM, AlertPriority.LOW][i % 3],
#                 "created_at": datetime.utcnow(),
#                 "acknowledged": False,
#                 "created_by": admin_id
#             })
#         await app.mongodb.alerts.insert_many(sample_alerts)
    
#     print("🚀 Server running at http://localhost:8000")
#     print("📚 API docs available at http://localhost:8000/docs")
    
#     yield  # Server is running
    
#     # Cleanup: Close MongoDB connection
#     print("Shutting down...")
#     app.mongodb_client.close()

# # Initialize FastAPI with lifespan
# app = FastAPI(
#     title="Autonomous Report Generator API",
#     description="Enterprise AI-powered reporting system with MongoDB",
#     version="1.0.0",
#     lifespan=lifespan
# )

# # ============================================================================
# # CORS CONFIGURATION
# # ============================================================================

# cors_origins = [
#     "https://ai-autonomous-report-generator-hypr.vercel.app",
#     "http://localhost:5173",
#     "http://127.0.0.1:5173", 
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "http://localhost:8080",
#     "http://127.0.0.1:8080",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=cors_origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
#     allow_headers=["*"],
#     expose_headers=["*"]
# )

# # ============================================================================
# # SECURITY CONFIGURATION
# # ============================================================================

# SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days for development
# REFRESH_TOKEN_EXPIRE_DAYS = 30

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# security = HTTPBearer()

# # MongoDB Configuration
# MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
# DB_NAME = os.getenv("MONGODB_DB_NAME", "report_generator")

# # ============================================================================
# # ENUMS & CONSTANTS
# # ============================================================================

# class UserRole(str, Enum):
#     ADMIN = "admin"
#     MANAGER = "manager"
#     ANALYST = "analyst"
#     VIEWER = "viewer"

# class Department(str, Enum):
#     FINANCE = "finance"
#     HR = "hr"
#     SALES = "sales"
#     OPERATIONS = "operations"
#     COMPLIANCE = "compliance"

# class ReportType(str, Enum):
#     PDF = "pdf"
#     PPT = "ppt"
#     EXCEL = "excel"

# class ReportFrequency(str, Enum):
#     DAILY = "daily"
#     WEEKLY = "weekly"
#     MONTHLY = "monthly"

# class AlertPriority(str, Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"

# # ============================================================================
# # PYDANTIC MODELS
# # ============================================================================

# class UserRegister(BaseModel):
#     email: EmailStr
#     password: str
#     name: str
#     role: UserRole
#     departments: List[Department]

# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# class Token(BaseModel):
#     access_token: str
#     refresh_token: str
#     token_type: str
#     expires_in: int
#     user: Dict[str, Any]

# class TokenRefresh(BaseModel):
#     refresh_token: str

# class User(BaseModel):
#     id: str
#     email: EmailStr
#     name: str
#     role: UserRole
#     departments: List[Department]
#     created_at: datetime

# class ReportGenerate(BaseModel):
#     title: str
#     department: Department
#     report_type: ReportType
#     date_range: Dict[str, str]
#     frequency: Optional[ReportFrequency] = None
#     schedule: Optional[bool] = False

# class Report(BaseModel):
#     id: str
#     title: str
#     department: Department
#     report_type: ReportType
#     file_url: str
#     size: str
#     status: str
#     created_by: str
#     created_at: datetime

# class NLPQuery(BaseModel):
#     query: str
#     department: Optional[Department] = None
#     context: Optional[Dict[str, Any]] = None

# class QueryResponse(BaseModel):
#     query: str
#     answer: str
#     insights: List[str]
#     chart_data: Optional[List[Dict[str, Any]]] = None
#     recommendations: Optional[List[str]] = None

# class Alert(BaseModel):
#     id: str
#     type: str
#     department: Department
#     message: str
#     priority: AlertPriority
#     created_at: datetime
#     acknowledged: bool = False

# class CommentCreate(BaseModel):
#     report_id: str
#     content: str
#     mentioned_users: Optional[List[str]] = []

# class Comment(BaseModel):
#     id: str
#     report_id: str
#     user_id: str
#     user_name: str
#     content: str
#     mentioned_users: List[str]
#     created_at: datetime
#     replies: List[Dict[str, Any]] = []

# class UserSettings(BaseModel):
#     language: str = "english"
#     theme: str = "light"
#     report_format: ReportType = ReportType.PDF
#     notifications: Dict[str, bool] = {
#         "email": True,
#         "slack": False,
#         "teams": False
#     }

# class KPIData(BaseModel):
#     department: Department
#     kpis: List[Dict[str, Any]]
#     chart_data: List[Dict[str, Any]]
#     summary: str

# # ============================================================================
# # DATABASE UTILITIES
# # ============================================================================

# async def create_indexes(db):
#     """Create database indexes for better performance"""
#     # Users collection indexes
#     await db.users.create_index("email", unique=True)
#     await db.users.create_index("role")
#     await db.users.create_index("departments")
    
#     # Reports collection indexes
#     await db.reports.create_index("department")
#     await db.reports.create_index("created_by")
#     await db.reports.create_index("created_at")
#     await db.reports.create_index([("department", 1), ("created_at", -1)])
    
#     # Alerts collection indexes
#     await db.alerts.create_index("department")
#     await db.alerts.create_index("priority")
#     await db.alerts.create_index("acknowledged")
#     await db.alerts.create_index("created_at")
    
#     # Comments collection indexes
#     await db.comments.create_index("report_id")
#     await db.comments.create_index("user_id")
#     await db.comments.create_index("created_at")
    
#     # Activities collection indexes
#     await db.activities.create_index("user_id")
#     await db.activities.create_index("timestamp")
    
#     # New indexes for report files
#     await db.report_files.create_index("report_id", unique=True)
#     await db.report_files.create_index("created_at")
    
#     # New collection for data uploads
#     await db.data_uploads.create_index("uploaded_by")
#     await db.data_uploads.create_index("department")
#     await db.data_uploads.create_index("uploaded_at")
    
#     print("✅ Database indexes created")

# def serialize_doc(doc):
#     """Convert MongoDB document to JSON serializable format"""
#     if doc and '_id' in doc:
#         doc['id'] = str(doc['_id'])
#         del doc['_id']
#     return doc

# async def get_database():
#     """Dependency to get database instance"""
#     return app.mongodb

# # ============================================================================
# # AUTHENTICATION UTILITIES
# # ============================================================================

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)

# def create_access_token(data: dict) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire, "type": "access"})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def create_refresh_token(data: dict) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
#     to_encode.update({"exp": expire, "type": "refresh"})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def decode_token(token: str) -> dict:
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(
#             status_code=401, 
#             detail="Token has expired",
#             headers={"WWW-Authenticate": "Bearer error='token_expired'"}
#         )
#     except jwt.InvalidTokenError:
#         raise HTTPException(
#             status_code=401, 
#             detail="Invalid token",
#             headers={"WWW-Authenticate": "Bearer error='invalid_token'"}
#         )
#     except Exception:
#         raise HTTPException(
#             status_code=401, 
#             detail="Could not validate credentials",
#             headers={"WWW-Authenticate": "Bearer"}
#         )

# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db=Depends(get_database)
# ) -> dict:
#     token = credentials.credentials
#     payload = decode_token(token)
    
#     # Check token type
#     if payload.get("type") != "access":
#         raise HTTPException(status_code=401, detail="Invalid token type")
    
#     user_id = payload.get("sub")
#     user = await db.users.find_one({"id": user_id})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     return serialize_doc(user)

# def check_role(required_roles: List[UserRole]):
#     async def role_checker(current_user: dict = Depends(get_current_user)):
#         if current_user["role"] not in required_roles:
#             raise HTTPException(status_code=403, detail="Insufficient permissions")
#         return current_user
#     return role_checker

# # ============================================================================
# # TOKEN REFRESH MIDDLEWARE
# # ============================================================================

# @app.middleware("http")
# async def token_refresh_middleware(request: Request, call_next):
#     # Skip for auth endpoints and OPTIONS requests
#     if request.url.path.startswith("/api/auth/") or request.method == "OPTIONS":
#         return await call_next(request)
    
#     response = await call_next(request)
    
#     # Check if response is 401 due to token expiry
#     if response.status_code == 401:
#         try:
#             # Check if it's a token expiry error
#             response_body = b""
#             async for chunk in response.body_iterator:
#                 response_body += chunk
            
#             response_body_str = response_body.decode()
#             if "token_expired" in response_body_str.lower() or "expired" in response_body_str.lower():
#                 # Create a new response with token expired header
#                 from fastapi.responses import JSONResponse
#                 return JSONResponse(
#                     status_code=401,
#                     content={"detail": "Token expired", "code": "token_expired"},
#                     headers={"X-Token-Expired": "true"}
#                 )
#         except:
#             pass
    
#     return response

# # ============================================================================
# # CORS EXCEPTION HANDLING MIDDLEWARE
# # ============================================================================

# @app.middleware("http")
# async def catch_exceptions_middleware(request: Request, call_next):
#     try:
#         response = await call_next(request)
        
#         # Ensure CORS headers are added to all responses
#         origin = request.headers.get('origin')
#         if origin and origin in cors_origins:
#             response.headers["Access-Control-Allow-Origin"] = origin
#         elif "*" in cors_origins:
#             response.headers["Access-Control-Allow-Origin"] = "*"
            
#         response.headers["Access-Control-Allow-Credentials"] = "true"
#         response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
#         response.headers["Access-Control-Allow-Headers"] = "*"
        
#         return response
        
#     except Exception as exc:
#         # Handle exceptions and still add CORS headers
#         import traceback
#         logger.error(f"Unhandled exception: {str(exc)}")
#         logger.error(traceback.format_exc())
        
#         # Use JSONResponse instead of Response
#         response = JSONResponse(
#             status_code=500,
#             content={"detail": "Internal server error", "error": str(exc)}
#         )
        
#         origin = request.headers.get('origin')
#         if origin and origin in cors_origins:
#             response.headers["Access-Control-Allow-Origin"] = origin
#         elif "*" in cors_origins:
#             response.headers["Access-Control-Allow-Origin"] = "*"
            
#         response.headers["Access-Control-Allow-Credentials"] = "true"
#         response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
#         response.headers["Access-Control-Allow-Headers"] = "*"
        
#         return response

# # ============================================================================
# # AI INTEGRATION FUNCTIONS
# # ============================================================================

# def analyze_with_ai(query: str, data: Any) -> Dict[str, Any]:
#     """Mock AI analysis function"""
#     insights = [
#         "Sales performance increased by 22% compared to previous quarter",
#         "Technology sector showed strongest growth at 28%",
#         "Customer retention improved by 15% through loyalty programs"
#     ]
    
#     recommendations = [
#         "Increase marketing budget in high-performing regions by 12%",
#         "Focus on customer retention strategies in underperforming segments",
#         "Expand product line in technology sector based on demand trends"
#     ]
    
#     return {
#         "insights": insights,
#         "recommendations": recommendations,
#         "confidence": 0.92
#     }

# def detect_anomalies(data: pd.DataFrame) -> List[Dict[str, Any]]:
#     """Anomaly detection using ML"""
#     anomalies = []
#     if len(data) > 0:
#         anomalies.append({
#             "type": "spike",
#             "metric": "expenses",
#             "value": "+15%",
#             "severity": "medium",
#             "description": "Unusual increase in marketing expenses detected"
#         })
#     return anomalies

# def generate_executive_summary(department: Department, data: Dict) -> str:
#     """Generate AI-powered executive summary"""
#     summaries = {
#         Department.FINANCE: "Q2 financial performance exceeded expectations with 12.5% revenue growth. Operating margins improved to 25% through strategic cost optimization. Cash flow remains strong with $2.4M total revenue.",
#         Department.HR: "Workforce expansion on track with 23 new hires. Attrition rate decreased to 8.2%, below industry average. Employee satisfaction scores improved to 87% following new wellness initiatives.",
#         Department.SALES: "Outstanding quarter with 156 deals closed, representing 22% growth. Average deal size increased to $27K. Sales pipeline robust at $4.2M with 34% conversion rate.",
#         Department.OPERATIONS: "Operational efficiency reached 94% with significant reduction in equipment downtime. Order volume increased 18% while maintaining 96% on-time delivery rate.",
#         Department.COMPLIANCE: "All regulatory requirements met with 12 successful audits. Issue resolution rate at 89%. Risk assessment remains at Low level with proactive monitoring in place."
#     }
#     return summaries.get(department, "Performance metrics within expected parameters.")

# def process_nlp_query(query: str, department: Optional[Department]) -> Dict[str, Any]:
#     """Process natural language queries using AI"""
#     query_lower = query.lower()
    
#     if "sales" in query_lower or "revenue" in query_lower:
#         return {
#             "answer": "Sales performance for Q2 shows 22% growth with 156 deals closed. Revenue reached $2.4M with strong pipeline of $4.2M.",
#             "chart_data": [
#                 {"month": "Jan", "sales": 540},
#                 {"month": "Feb", "sales": 675},
#                 {"month": "Mar", "sales": 756},
#                 {"month": "Apr", "sales": 594},
#                 {"month": "May", "sales": 810},
#                 {"month": "Jun", "sales": 837}
#             ],
#             "insights": [
#                 "Technology sector led growth with 28% increase",
#                 "Average deal size increased from $25K to $27K",
#                 "Conversion rate improved to 34%"
#             ],
#             "recommendations": [
#                 "Invest in high-performing sales channels",
#                 "Expand sales team in technology vertical"
#             ]
#         }
#     elif "hr" in query_lower or "employee" in query_lower or "attrition" in query_lower:
#         return {
#             "answer": "HR metrics show positive trends with attrition decreasing to 8.2% and employee satisfaction at 87%.",
#             "chart_data": [
#                 {"month": "Jan", "hires": 5, "exits": 3},
#                 {"month": "Feb", "hires": 8, "exits": 2},
#                 {"month": "Mar", "hires": 6, "exits": 4},
#                 {"month": "Apr", "hires": 7, "exits": 3},
#                 {"month": "May", "hires": 9, "exits": 5},
#                 {"month": "Jun", "hires": 4, "exits": 3}
#             ],
#             "insights": [
#                 "Net workforce growth of 5.2%",
#                 "Wellness programs contributed to improved satisfaction",
#                 "Retention in key departments above 95%"
#             ],
#             "recommendations": [
#                 "Continue investment in employee wellness",
#                 "Implement mentorship programs for new hires"
#             ]
#         }
#     else:
#         return {
#             "answer": "Based on current data analysis, overall business metrics show positive growth across departments with 12% average improvement.",
#             "insights": [
#                 "Revenue growth trending upward",
#                 "Operational efficiency at peak levels",
#                 "Customer satisfaction improving"
#             ],
#             "recommendations": [
#                 "Maintain current strategic initiatives",
#                 "Monitor emerging market trends"
#             ]
#         }

# # ============================================================================
# # MOCK DATA GENERATOR
# # ============================================================================

# def generate_mock_kpi_data(department: Department):
#     kpi_mapping = {
#         Department.FINANCE: {
#             "kpis": [
#                 {"label": "Total Revenue", "value": "$2.4M", "change": "+12.5%", "positive": True},
#                 {"label": "Expenses", "value": "$1.8M", "change": "+8.2%", "positive": False},
#                 {"label": "Net Profit", "value": "$600K", "change": "+18.3%", "positive": True},
#                 {"label": "Profit Margin", "value": "25%", "change": "+2.1%", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "revenue": 180, "expenses": 140},
#                 {"month": "Feb", "revenue": 200, "expenses": 150},
#                 {"month": "Mar", "revenue": 220, "expenses": 160},
#                 {"month": "Apr", "revenue": 240, "expenses": 180},
#                 {"month": "May", "revenue": 260, "expenses": 190},
#                 {"month": "Jun", "revenue": 280, "expenses": 200}
#             ],
#             "summary": "Q2 revenue grew by 12.5% with controlled expense management. Profit margins improved across all divisions."
#         },
#         Department.HR: {
#             "kpis": [
#                 {"label": "Total Employees", "value": "342", "change": "+5.2%", "positive": True},
#                 {"label": "Attrition Rate", "value": "8.2%", "change": "-1.3%", "positive": True},
#                 {"label": "New Hires", "value": "23", "change": "+15%", "positive": True},
#                 {"label": "Satisfaction", "value": "87%", "change": "+3%", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "hires": 5, "exits": 3},
#                 {"month": "Feb", "hires": 8, "exits": 2},
#                 {"month": "Mar", "hires": 6, "exits": 4},
#                 {"month": "Apr", "hires": 7, "exits": 3},
#                 {"month": "May", "hires": 9, "exits": 5},
#                 {"month": "Jun", "hires": 4, "exits": 3}
#             ],
#             "summary": "Workforce grew steadily with reduced attrition. Employee satisfaction improved through new wellness programs."
#         },
#         Department.SALES: {
#             "kpis": [
#                 {"label": "Total Deals", "value": "156", "change": "+22%", "positive": True},
#                 {"label": "Conversion Rate", "value": "34%", "change": "+5%", "positive": True},
#                 {"label": "Pipeline Value", "value": "$4.2M", "change": "+28%", "positive": True},
#                 {"label": "Avg Deal Size", "value": "$27K", "change": "+8%", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "deals": 20, "value": 540},
#                 {"month": "Feb", "deals": 25, "value": 675},
#                 {"month": "Mar", "deals": 28, "value": 756},
#                 {"month": "Apr", "deals": 22, "value": 594},
#                 {"month": "May", "deals": 30, "value": 810},
#                 {"month": "Jun", "deals": 31, "value": 837}
#             ],
#             "summary": "Outstanding sales performance with 22% growth in closed deals. Pipeline value reached all-time high."
#         },
#         Department.OPERATIONS: {
#             "kpis": [
#                 {"label": "Efficiency", "value": "94%", "change": "+2%", "positive": True},
#                 {"label": "Downtime", "value": "2.3h", "change": "-15%", "positive": True},
#                 {"label": "Orders", "value": "1,234", "change": "+18%", "positive": True},
#                 {"label": "On-Time", "value": "96%", "change": "+3%", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "efficiency": 91, "downtime": 3.2},
#                 {"month": "Feb", "efficiency": 92, "downtime": 2.8},
#                 {"month": "Mar", "efficiency": 93, "downtime": 2.5},
#                 {"month": "Apr", "efficiency": 94, "downtime": 2.3},
#                 {"month": "May", "efficiency": 94, "downtime": 2.1},
#                 {"month": "Jun", "efficiency": 95, "downtime": 1.9}
#             ],
#             "summary": "Operational efficiency improved with reduced equipment downtime. On-time delivery exceeds target."
#         },
#         Department.COMPLIANCE: {
#             "kpis": [
#                 {"label": "Audits", "value": "12", "change": "0%", "positive": True},
#                 {"label": "Open Issues", "value": "3", "change": "-40%", "positive": True},
#                 {"label": "Resolved", "value": "89%", "change": "+12%", "positive": True},
#                 {"label": "Risk Level", "value": "Low", "change": "Stable", "positive": True}
#             ],
#             "chart_data": [
#                 {"month": "Jan", "audits": 2, "issues": 5},
#                 {"month": "Feb", "audits": 2, "issues": 4},
#                 {"month": "Mar", "audits": 2, "issues": 6},
#                 {"month": "Apr", "audits": 2, "issues": 5},
#                 {"month": "May", "audits": 2, "issues": 4},
#                 {"month": "Jun", "audits": 2, "issues": 3}
#             ],
#             "summary": "Compliance metrics remain strong with 89% issue resolution rate. All audits passed successfully."
#         }
#     }
#     return kpi_mapping.get(department, kpi_mapping[Department.FINANCE])

# # ============================================================================
# # PDF GENERATION FUNCTIONS
# # ============================================================================

# async def generate_pdf_report(department: str, filename: str, data_preview: List[Dict], 
#                             analysis_result: Dict, user_name: str) -> bytes:
#     """Generate PDF report from AI analysis"""
#     try:
#         # Create a buffer for PDF
#         buffer = io.BytesIO()
        
#         # Create PDF document
#         doc = SimpleDocTemplate(buffer, pagesize=letter, 
#                               topMargin=0.5*inch, bottomMargin=0.5*inch,
#                               leftMargin=0.5*inch, rightMargin=0.5*inch)
        
#         # Story to hold PDF elements
#         story = []
#         styles = getSampleStyleSheet()
        
#         # Custom styles
#         title_style = ParagraphStyle(
#             'CustomTitle',
#             parent=styles['Heading1'],
#             fontSize=18,
#             spaceAfter=30,
#             textColor=colors.HexColor('#1E40AF'),
#             alignment=1  # Center alignment
#         )
        
#         heading_style = ParagraphStyle(
#             'CustomHeading',
#             parent=styles['Heading2'],
#             fontSize=14,
#             spaceAfter=12,
#             spaceBefore=20,
#             textColor=colors.HexColor('#2D3748')
#         )
        
#         normal_style = ParagraphStyle(
#             'CustomNormal',
#             parent=styles['Normal'],
#             fontSize=10,
#             spaceAfter=6,
#             textColor=colors.HexColor('#4A5568')
#         )
        
#         bullet_style = ParagraphStyle(
#             'CustomBullet',
#             parent=styles['Normal'],
#             fontSize=10,
#             spaceAfter=4,
#             leftIndent=20,
#             textColor=colors.HexColor('#4A5568')
#         )
        
#         # Title
#         dept_display = department.title() if department else "Unknown"
#         title = Paragraph(f"AI Analysis Report - {dept_display} Department", title_style)
#         story.append(title)
        
#         # File info
#         info_style = ParagraphStyle(
#             'InfoStyle',
#             parent=styles['Normal'],
#             fontSize=9,
#             textColor=colors.gray,
#             alignment=1
#         )
#         story.append(Paragraph(f"<b>File:</b> {filename}", info_style))
#         story.append(Paragraph(f"<b>Generated by:</b> {user_name}", info_style))
#         story.append(Paragraph(f"<b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC", info_style))
#         story.append(Spacer(1, 25))
        
#         # Executive Summary
#         story.append(Paragraph("Executive Summary", heading_style))
#         summary_text = analysis_result.get('summary', 'No summary available.')
#         # Clean summary text - remove markdown and fix formatting
#         summary_text = clean_text_for_pdf(summary_text)
#         story.append(Paragraph(summary_text, normal_style))
#         story.append(Spacer(1, 15))
        
#         # Key Insights
#         story.append(Paragraph("Key Insights", heading_style))
#         insights = analysis_result.get('insights', [])
#         if insights:
#             for insight in insights:
#                 # Clean each insight text
#                 clean_insight = clean_text_for_pdf(insight)
#                 story.append(Paragraph(f"• {clean_insight}", bullet_style))
#         else:
#             story.append(Paragraph("No specific insights generated.", normal_style))
#         story.append(Spacer(1, 15))
        
#         # Recommendations
#         story.append(Paragraph("Actionable Recommendations", heading_style))
#         recommendations = analysis_result.get('recommendations', [])
#         if recommendations:
#             for rec in recommendations:
#                 # Clean each recommendation text
#                 clean_rec = clean_text_for_pdf(rec)
#                 story.append(Paragraph(f"• {clean_rec}", bullet_style))
#         else:
#             story.append(Paragraph("No specific recommendations generated.", normal_style))
#         story.append(Spacer(1, 15))
        
#         # Data Overview
#         story.append(Paragraph("Data Overview", heading_style))
#         if data_preview and len(data_preview) > 0:
#             data_info = f"Dataset contains {len(data_preview)} sample rows with {len(data_preview[0]) if data_preview else 0} columns."
#             story.append(Paragraph(data_info, normal_style))
#             story.append(Spacer(1, 10))
        
#         # Trends Analysis
#         trends = analysis_result.get('trends', {})
#         if trends and trends.get('trend') != 'unknown':
#             story.append(Paragraph("Trend Analysis", heading_style))
            
#             trend_info = []
#             if trends.get('trend'):
#                 trend_info.append(f"<b>Overall Trend:</b> {trends['trend'].title()}")
#             if trends.get('confidence'):
#                 trend_info.append(f"<b>Confidence Level:</b> {trends['confidence'].title()}")
#             if trends.get('pattern'):
#                 clean_pattern = clean_text_for_pdf(trends['pattern'])
#                 trend_info.append(f"<b>Pattern:</b> {clean_pattern}")
#             if trends.get('prediction'):
#                 clean_prediction = clean_text_for_pdf(trends['prediction'])
#                 trend_info.append(f"<b>Prediction:</b> {clean_prediction}")
#             if trends.get('reasoning'):
#                 clean_reasoning = clean_text_for_pdf(trends['reasoning'])
#                 trend_info.append(f"<b>Reasoning:</b> {clean_reasoning}")
            
#             for info in trend_info:
#                 story.append(Paragraph(info, normal_style))
#             story.append(Spacer(1, 15))
        
#         # Anomalies
#         anomalies = analysis_result.get('anomalies', [])
#         if anomalies:
#             story.append(Paragraph("Detected Anomalies", heading_style))
#             for i, anomaly in enumerate(anomalies[:5], 1):  # Show first 5 anomalies
#                 desc = clean_text_for_pdf(anomaly.get('description', 'N/A'))
#                 severity = anomaly.get('severity', 'N/A').title()
#                 anomaly_type = anomaly.get('type', 'N/A').title()
                
#                 anomaly_text = f"<b>Anomaly {i}:</b> {desc} | <b>Type:</b> {anomaly_type} | <b>Severity:</b> {severity}"
#                 story.append(Paragraph(anomaly_text, bullet_style))
#             story.append(Spacer(1, 15))
        
#         # Data Preview Table
#         if data_preview and len(data_preview) > 0:
#             story.append(Paragraph("Data Preview (First 10 Rows)", heading_style))
            
#             # Create table data
#             headers = list(data_preview[0].keys())
#             table_data = [headers]
            
#             for row in data_preview[:10]:
#                 # Clean and truncate cell values
#                 clean_row = []
#                 for val in row.values():
#                     clean_val = str(val)
#                     # Remove any markdown formatting
#                     clean_val = clean_val.replace('*', '').replace('_', '').replace('#', '')
#                     # Truncate long values
#                     if len(clean_val) > 30:
#                         clean_val = clean_val[:27] + '...'
#                     clean_row.append(clean_val)
#                 table_data.append(clean_row)
            
#             # Create table
#             if len(table_data) > 1:
#                 table = Table(table_data, repeatRows=1)
#                 table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 9),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
#                     ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F7FAFC')),
#                     ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                     ('FONTSIZE', (0, 1), (-1, -1), 8),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
#                     ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')])
#                 ]))
#                 story.append(table)
#                 story.append(Spacer(1, 15))
        
#         # Footer with generation info
#         story.append(Spacer(1, 20))
#         footer_style = ParagraphStyle(
#             'FooterStyle',
#             parent=styles['Normal'],
#             fontSize=8,
#             textColor=colors.gray,
#             alignment=1
#         )
#         story.append(Paragraph("Generated by AI-Powered Report Generator", footer_style))
#         story.append(Paragraph("Confidential - For Internal Use Only", footer_style))
        
#         # Build PDF
#         doc.build(story)
        
#         # Get PDF bytes
#         pdf_bytes = buffer.getvalue()
#         buffer.close()
        
#         return pdf_bytes
        
#     except Exception as e:
#         logger.error(f"PDF generation error: {str(e)}")
#         # Return a simple error PDF
#         return generate_error_pdf(str(e))
    
# def clean_text_for_pdf(text: str) -> str:
#     """Clean text for PDF formatting - remove markdown and fix common issues"""
#     if not text:
#         return ""
    
#     # Remove markdown formatting
#     clean_text = text.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
    
#     # Remove excessive newlines and spaces
#     clean_text = ' '.join(clean_text.split())
    
#     # Fix common AI response artifacts
#     clean_text = clean_text.replace('•', '-')  # Replace bullet points with dashes
#     clean_text = clean_text.replace('```', '')  # Remove code blocks
#     clean_text = clean_text.replace('`', '')    # Remove inline code
    
#     # Ensure proper sentence capitalization
#     if clean_text and clean_text[0].islower():
#         clean_text = clean_text[0].upper() + clean_text[1:]
    
#     return clean_text

# def generate_error_pdf(error_message: str) -> bytes:
#     """Generate a simple error PDF"""
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     story = []
#     styles = getSampleStyleSheet()
    
#     # Title
#     title_style = ParagraphStyle(
#         'ErrorTitle',
#         parent=styles['Heading1'],
#         fontSize=16,
#         spaceAfter=20,
#         textColor=colors.red,
#         alignment=1
#     )
#     story.append(Paragraph("Report Generation Error", title_style))
#     story.append(Spacer(1, 20))
    
#     # Error message
#     normal_style = ParagraphStyle(
#         'ErrorNormal',
#         parent=styles['Normal'],
#         fontSize=12,
#         spaceAfter=12,
#         textColor=colors.darkred,
#         alignment=1
#     )
#     story.append(Paragraph("We encountered an issue while generating your report:", normal_style))
#     story.append(Spacer(1, 10))
#     story.append(Paragraph(error_message, normal_style))
#     story.append(Spacer(1, 20))
    
#     # Contact info
#     contact_style = ParagraphStyle(
#         'ContactStyle',
#         parent=styles['Normal'],
#         fontSize=10,
#         textColor=colors.gray,
#         alignment=1
#     )
#     story.append(Paragraph("Please try again or contact support if the issue persists.", contact_style))
    
#     doc.build(story)
#     pdf_bytes = buffer.getvalue()
#     buffer.close()
#     return pdf_bytes

# # ============================================================================
# # API ENDPOINTS
# # ============================================================================

# @app.get("/")
# async def root():
#     return {
#         "service": "Autonomous Report Generator API with MongoDB",
#         "status": "operational",
#         "version": "1.0.0",
#         "timestamp": datetime.utcnow().isoformat()
#     }

# # ============================================================================
# # AUTHENTICATION ENDPOINTS
# # ============================================================================

# @app.post("/api/auth/register", response_model=Token)
# async def register(user_data: UserRegister, db=Depends(get_database)):
#     """Register a new user"""
#     # Check if user exists
#     existing_user = await db.users.find_one({"email": user_data.email})
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Create new user
#     user_id = str(uuid.uuid4())
#     hashed_password = get_password_hash(user_data.password)
    
#     user = {
#         "id": user_id,
#         "email": user_data.email,
#         "password": hashed_password,
#         "name": user_data.name,
#         "role": user_data.role,
#         "departments": user_data.departments,
#         "created_at": datetime.utcnow(),
#         "updated_at": datetime.utcnow()
#     }
    
#     await db.users.insert_one(user)
    
#     # Create tokens
#     access_token = create_access_token({"sub": user_id})
#     refresh_token = create_refresh_token({"sub": user_id})
    
#     # Store refresh token
#     await db.users.update_one(
#         {"id": user_id},
#         {"$set": {"refresh_token": refresh_token, "updated_at": datetime.utcnow()}}
#     )
    
#     # Return token and user info
#     user_response = {k: v for k, v in user.items() if k not in ["password", "refresh_token"]}
#     user_response = serialize_doc(user_response)
    
#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#         "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
#         "user": user_response
#     }

# @app.post("/api/auth/login", response_model=Token)
# async def login(credentials: UserLogin, db=Depends(get_database)):
#     """Login with email and password"""
#     # Find user by email
#     user = await db.users.find_one({"email": credentials.email})
    
#     if not user or not verify_password(credentials.password, user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
    
#     # Create tokens
#     access_token = create_access_token({"sub": user["id"]})
#     refresh_token = create_refresh_token({"sub": user["id"]})
    
#     # Store refresh token
#     await db.users.update_one(
#         {"id": user["id"]},
#         {"$set": {"refresh_token": refresh_token, "updated_at": datetime.utcnow()}}
#     )
    
#     # Return tokens and user info
#     user_response = {k: v for k, v in user.items() if k not in ["password", "refresh_token"]}
#     user_response = serialize_doc(user_response)
    
#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#         "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
#         "user": user_response
#     }

# @app.post("/api/auth/refresh", response_model=Token)
# async def refresh_token(
#     refresh_data: TokenRefresh,
#     db=Depends(get_database)
# ):
#     """Refresh access token using refresh token"""
#     try:
#         # Verify refresh token
#         payload = jwt.decode(refresh_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
#         if payload.get("type") != "refresh":
#             raise HTTPException(status_code=401, detail="Invalid token type")
        
#         user_id = payload.get("sub")
#         user = await db.users.find_one({"id": user_id})
        
#         if not user:
#             raise HTTPException(status_code=401, detail="User not found")
        
#         # Verify refresh token matches stored one
#         if user.get("refresh_token") != refresh_data.refresh_token:
#             raise HTTPException(status_code=401, detail="Invalid refresh token")
        
#         # Create new tokens
#         access_token = create_access_token({"sub": user_id})
#         new_refresh_token = create_refresh_token({"sub": user_id})
        
#         # Update stored refresh token
#         await db.users.update_one(
#             {"id": user_id},
#             {"$set": {"refresh_token": new_refresh_token, "updated_at": datetime.utcnow()}}
#         )
        
#         # Return user info without password
#         user_response = {k: v for k, v in user.items() if k not in ["password", "refresh_token"]}
#         user_response = serialize_doc(user_response)
        
#         return {
#             "access_token": access_token,
#             "refresh_token": new_refresh_token,
#             "token_type": "bearer",
#             "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
#             "user": user_response
#         }
        
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Refresh token expired")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Invalid refresh token")

# @app.get("/api/auth/me")
# async def get_current_user_info(current_user: dict = Depends(get_current_user)):
#     """Get current user information"""
#     return {k: v for k, v in current_user.items() if k not in ["password", "refresh_token"]}

# # ============================================================================
# # CSV UPLOAD & ANALYSIS ENDPOINTS
# # ============================================================================

# @app.post("/api/reports/upload-csv")
# async def upload_csv_analysis(
#     file: UploadFile = File(...),
#     department: str = Form(None),
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Upload CSV for AI analysis and report generation"""
#     try:
#         logger.info(f"Upload received: {file.filename}, department: {department}")
        
#         if not file.filename.endswith('.csv'):
#             raise HTTPException(
#                 status_code=400, 
#                 detail="Only CSV files are supported"
#             )
        
#         # Validate department
#         if not department:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Department is required"
#             )
        
#         try:
#             # Convert string to Department enum
#             department_enum = Department(department.lower())
#         except ValueError:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Invalid department: {department}. Must be one of: {[d.value for d in Department]}"
#             )
        
#         # Check if user has access to this department
#         if department_enum not in current_user["departments"]:
#             raise HTTPException(
#                 status_code=403,
#                 detail=f"Access denied to {department} department"
#             )
        
#         # Read and parse CSV
#         content = await file.read()
#         logger.info(f"File size: {len(content)} bytes")
        
#         try:
#             csv_text = content.decode('utf-8')
#             df = pd.read_csv(io.StringIO(csv_text))
#             logger.info(f"CSV parsed successfully: {len(df)} rows, {len(df.columns)} columns")
#         except Exception as csv_error:
#             raise HTTPException(
#                 status_code=400, 
#                 detail=f"Invalid CSV file: {str(csv_error)}"
#             )
        
#         # Basic data validation
#         if df.empty:
#             raise HTTPException(status_code=400, detail="CSV file is empty")
        
#         if len(df.columns) == 0:
#             raise HTTPException(status_code=400, detail="CSV file has no columns")
        
#         # Convert DataFrame to list of dictionaries for AI processing
#         data_records = df.to_dict('records')
        
#         # Get AI agents
#         try:
#             llama_agent = get_llama_agent()
#             analysis_agent = get_analysis_agent()
#             logger.info("AI agents initialized successfully")
#         except Exception as agent_error:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"AI service unavailable: {str(agent_error)}"
#             )
        
#         # Prepare context for AI analysis
#         context = {
#             "department": department_enum.value,
#             "data_preview": data_records[:5],  # First 5 records for context
#             "columns": list(df.columns),
#             "total_records": len(df),
#             "data_summary": {
#                 "columns": list(df.columns),
#                 "total_rows": len(df),
#                 "data_types": df.dtypes.to_dict()
#             }
#         }
        
#         # Generate AI analysis with error handling
#         try:
#             analysis_result = analysis_agent.analyze_department_performance(
#                 department=department_enum.value,
#                 kpis=[{"label": col, "value": "Analyzing...", "change": "0%", "positive": True} for col in df.columns[:4]],
#                 chart_data=data_records[:10]  # Use first 10 records for chart data
#             )
#             logger.info("AI analysis completed successfully")
#         except Exception as analysis_error:
#             logger.error(f"AI analysis failed: {str(analysis_error)}")
#             # Provide fallback analysis
#             analysis_result = {
#                 "summary": f"Basic analysis of {len(df)} records from {file.filename} in {department} department",
#                 "insights": [
#                     f"Data loaded successfully with {len(df)} rows and {len(df.columns)} columns",
#                     "AI analysis encountered issues but data is ready for review"
#                 ],
#                 "recommendations": [
#                     "Review data quality and structure",
#                     "Consider manual analysis for specific insights"
#                 ],
#                 "trends": {
#                     "trend": "unknown", 
#                     "pattern": "Analysis limited due to technical issues",
#                     "prediction": "Further analysis required",
#                     "confidence": "low",
#                     "reasoning": "AI analysis encountered technical difficulties"
#                 },
#                 "anomalies": []
#             }
        
#         # Generate PDF report
#         try:
#             pdf_report = await generate_pdf_report(
#                 department=department_enum.value,  # Use string value, not enum
#                 filename=file.filename,
#                 data_preview=data_records[:10],
#                 analysis_result=analysis_result,
#                 user_name=current_user["name"]
#             )
#             logger.info("PDF report generated successfully")
#         except Exception as pdf_error:
#             logger.error(f"PDF generation failed: {str(pdf_error)}")
#             # Generate a simple error PDF instead of failing completely
#             pdf_report = generate_error_pdf(f"PDF generation issue: {str(pdf_error)}")
        
#         # Store report in database
#         report_id = str(uuid.uuid4())
#         report_data = {
#             "id": report_id,
#             "title": f"AI Analysis - {file.filename}",
#             "department": department_enum.value,
#             "report_type": ReportType.PDF.value,
#             "file_url": f"/api/reports/download/{report_id}",
#             "size": f"{(len(content) / 1024 / 1024):.1f} MB",
#             "status": "completed",
#             "created_by": current_user["id"],
#             "created_by_name": current_user["name"],
#             "created_at": datetime.utcnow(),
#             "source": "csv_upload",
#             "original_filename": file.filename,
#             "analysis_data": analysis_result
#         }
        
#         await db.reports.insert_one(report_data)
        
#         # Store PDF file
#         await db.report_files.insert_one({
#             "report_id": report_id,
#             "pdf_content": base64.b64encode(pdf_report).decode('utf-8'),
#             "created_at": datetime.utcnow()
#         })
        
#         # Log activity
#         activity = {
#             "id": str(uuid.uuid4()),
#             "action": f"CSV Analysis Report Generated: {file.filename}",
#             "user_id": current_user["id"],
#             "user_name": current_user["name"],
#             "timestamp": datetime.utcnow(),
#             "type": "csv_analysis",
#             "department": department_enum.value
#         }
#         await db.activities.insert_one(activity)
        
#         return {
#             "message": "CSV analyzed and report generated successfully",
#             "report_id": report_id,
#             "analysis": analysis_result,
#             "data_preview": {
#                 "columns": list(df.columns),
#                 "first_five_rows": data_records[:5],
#                 "total_rows": len(df)
#             }
#         }
        
#     except HTTPException:
#         # Re-raise HTTP exceptions
#         raise
#     except Exception as e:
#         logger.error(f"Unexpected error in upload_csv_analysis: {str(e)}")
#         import traceback
#         logger.error(traceback.format_exc())
#         raise HTTPException(
#             status_code=500, 
#             detail=f"Internal server error: {str(e)}"
#         )

# @app.get("/api/reports/download/{report_id}")
# async def download_report_pdf(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Download generated PDF report"""
#     try:
#         logger.info(f"Download request for report: {report_id}")
        
#         # Get report metadata
#         report = await db.reports.find_one({"id": report_id})
#         if not report:
#             logger.error(f"Report not found: {report_id}")
#             raise HTTPException(status_code=404, detail="Report not found")
        
#         logger.info(f"Found report: {report['title']} for department: {report['department']}")
        
#         # Check user access
#         user_departments = [d.value if isinstance(d, Department) else d for d in current_user["departments"]]
#         if report["department"] not in user_departments:
#             logger.error(f"Access denied: User {current_user['id']} cannot access {report['department']}")
#             raise HTTPException(status_code=403, detail="Access denied to this report")
        
#         # Get PDF content
#         pdf_file = await db.report_files.find_one({"report_id": report_id})
#         if not pdf_file:
#             logger.error(f"PDF file not found for report: {report_id}")
#             raise HTTPException(status_code=404, detail="PDF file not found")
        
#         logger.info(f"PDF file found, size: {len(pdf_file['pdf_content'])} bytes")
        
#         # Decode PDF content
#         try:
#             pdf_content = base64.b64decode(pdf_file["pdf_content"])
#             logger.info(f"PDF decoded successfully, size: {len(pdf_content)} bytes")
#         except Exception as decode_error:
#             logger.error(f"PDF decode error: {str(decode_error)}")
#             raise HTTPException(status_code=500, detail="Corrupted PDF file")
        
#         # Validate PDF content
#         if len(pdf_content) == 0:
#             logger.error("PDF content is empty")
#             raise HTTPException(status_code=500, detail="Empty PDF file")
        
#         # Return PDF file
#         from fastapi.responses import Response
#         filename = f"{report['title']}.pdf".replace(" ", "_")
        
#         logger.info(f"Returning PDF file: {filename}")
        
#         return Response(
#             content=pdf_content,
#             media_type="application/pdf",
#             headers={
#                 "Content-Disposition": f"attachment; filename={filename}",
#                 "Content-Length": str(len(pdf_content)),
#                 "Access-Control-Allow-Origin": "*",
#                 "Access-Control-Allow-Credentials": "true"
#             }
#         )
        
#     except HTTPException:
#         # Re-raise HTTP exceptions
#         raise
#     except Exception as e:
#         logger.error(f"PDF download error: {str(e)}")
#         import traceback
#         logger.error(traceback.format_exc())
#         raise HTTPException(
#             status_code=500, 
#             detail=f"Error downloading PDF: {str(e)}"
#         )
    
# @app.get("/api/reports/{report_id}/debug")
# async def debug_report(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Debug endpoint to check report status"""
#     try:
#         # Get report metadata
#         report = await db.reports.find_one({"id": report_id})
#         if not report:
#             return {"error": "Report not found"}
        
#         # Get PDF file info
#         pdf_file = await db.report_files.find_one({"report_id": report_id})
        
#         return {
#             "report_found": bool(report),
#             "report_data": {
#                 "id": report.get("id"),
#                 "title": report.get("title"),
#                 "department": report.get("department"),
#                 "created_at": report.get("created_at"),
#                 "status": report.get("status")
#             },
#             "pdf_file_found": bool(pdf_file),
#             "pdf_file_data": {
#                 "has_content": bool(pdf_file and pdf_file.get("pdf_content")),
#                 "content_length": len(pdf_file.get("pdf_content", "")) if pdf_file else 0,
#                 "created_at": pdf_file.get("created_at") if pdf_file else None
#             } if pdf_file else None,
#             "user_access": report["department"] in current_user["departments"] if report else False
#         }
#     except Exception as e:
#         return {"error": str(e)}

# @app.get("/api/reports/{report_id}/preview")
# async def preview_report(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get report preview and analysis data"""
#     report = await db.reports.find_one({"id": report_id})
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     if report["department"] not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied")
    
#     return {
#         "report": serialize_doc(report),
#         "analysis": report.get("analysis_data", {})
#     }

# # ============================================================================
# # CORS PREFLIGHT HANDLERS
# # ============================================================================

# @app.options("/api/reports/upload-csv")
# async def options_upload_csv():
#     """Handle CORS preflight for CSV upload"""
#     return JSONResponse(
#         content={"message": "OK"},
#         headers={
#             "Access-Control-Allow-Origin": "*",
#             "Access-Control-Allow-Methods": "POST, OPTIONS",
#             "Access-Control-Allow-Headers": "*",
#             "Access-Control-Allow-Credentials": "true"
#         }
#     )

# @app.options("/api/reports/download/{report_id}")
# async def options_download_report():
#     """Handle CORS preflight for download"""
#     return JSONResponse(
#         content={"message": "OK"},
#         headers={
#             "Access-Control-Allow-Origin": "*",
#             "Access-Control-Allow-Methods": "GET, OPTIONS",
#             "Access-Control-Allow-Headers": "*",
#             "Access-Control-Allow-Credentials": "true"
#         }
#     )

# # ============================================================================
# # DASHBOARD & KPI ENDPOINTS
# # ============================================================================

# @app.get("/api/dashboard/stats")
# async def get_dashboard_stats(
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get overall dashboard statistics"""
#     total_reports = await db.reports.count_documents({
#         "department": {"$in": current_user["departments"]}
#     })
    
#     active_alerts = await db.alerts.count_documents({
#         "department": {"$in": current_user["departments"]},
#         "acknowledged": False
#     })
    
#     recent_activities = await db.activities.find({
#         "user_id": current_user["id"]
#     }).sort("timestamp", -1).limit(5).to_list(length=5)
    
#     recent_activities = [serialize_doc(activity) for activity in recent_activities]
    
#     return {
#         "total_reports": total_reports,
#         "active_alerts": active_alerts,
#         "departments": len(current_user["departments"]),
#         "data_sources": 23,
#         "recent_activity": recent_activities
#     }

# @app.get("/api/dashboard/kpis/{department}")
# async def get_department_kpis(
#     department: Department,
#     current_user: dict = Depends(get_current_user)
# ):
#     """Get KPIs for a specific department"""
#     if department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this department")
    
#     data = generate_mock_kpi_data(department)
#     return {
#         "department": department,
#         "kpis": data["kpis"],
#         "chart_data": data["chart_data"],
#         "summary": data["summary"],
#         "last_updated": datetime.utcnow().isoformat()
#     }

# @app.get("/api/dashboard/activity")
# async def get_recent_activity(
#     limit: int = 10,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get recent activity log"""
#     activities = await db.activities.find({
#         "user_id": current_user["id"]
#     }).sort("timestamp", -1).limit(limit).to_list(length=limit)
    
#     activities = [serialize_doc(activity) for activity in activities]
    
#     total_activities = await db.activities.count_documents({
#         "user_id": current_user["id"]
#     })
    
#     return {
#         "activities": activities,
#         "total": total_activities
#     }

# # ============================================================================
# # REPORT MANAGEMENT ENDPOINTS
# # ============================================================================

# @app.post("/api/reports/generate")
# async def generate_report(
#     report_data: ReportGenerate,
#     background_tasks: BackgroundTasks,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Generate a new report"""
#     if report_data.department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this department")
    
#     report_id = str(uuid.uuid4())
    
#     report = {
#         "id": report_id,
#         "title": report_data.title,
#         "department": report_data.department,
#         "report_type": report_data.report_type,
#         "file_url": f"/reports/{report_id}.{report_data.report_type}",
#         "size": "2.4 MB",
#         "status": "completed",
#         "created_by": current_user["id"],
#         "created_by_name": current_user["name"],
#         "created_at": datetime.utcnow(),
#         "date_range": report_data.date_range,
#         "frequency": report_data.frequency,
#         "scheduled": report_data.schedule
#     }
    
#     await db.reports.insert_one(report)
    
#     # Add to activity log
#     activity = {
#         "id": str(uuid.uuid4()),
#         "action": f"Report Generated: {report_data.title}",
#         "user_id": current_user["id"],
#         "user_name": current_user["name"],
#         "timestamp": datetime.utcnow(),
#         "type": "report_generated",
#         "department": report_data.department
#     }
    
#     await db.activities.insert_one(activity)
    
#     return serialize_doc(report)

# @app.get("/api/reports")
# async def get_reports(
#     department: Optional[Department] = None,
#     limit: int = 50,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get list of reports"""
#     query = {"department": {"$in": current_user["departments"]}}
    
#     if department:
#         if department not in current_user["departments"]:
#             raise HTTPException(status_code=403, detail="Access denied to this department")
#         query["department"] = department
    
#     reports = await db.reports.find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
#     reports = [serialize_doc(report) for report in reports]
    
#     total = await db.reports.count_documents(query)
    
#     return {
#         "reports": reports,
#         "total": total
#     }

# @app.get("/api/reports/{report_id}")
# async def get_report(
#     report_id: str,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Get specific report details"""
#     report = await db.reports.find_one({"id": report_id})
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     if report["department"] not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this report")
    
#     return serialize_doc(report)

# @app.delete("/api/reports/{report_id}")
# async def delete_report(
#     report_id: str,
#     current_user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER])),
#     db=Depends(get_database)
# ):
#     """Delete a report (Admin/Manager only)"""
#     report = await db.reports.find_one({"id": report_id})
    
#     if not report:
#         raise HTTPException(status_code=404, detail="Report not found")
    
#     await db.reports.delete_one({"id": report_id})
    
#     # Also delete related comments
#     await db.comments.delete_many({"report_id": report_id})
    
#     return {"message": "Report deleted successfully", "report_id": report_id}

# # ============================================================================
# # NLP QUERY ENGINE ENDPOINTS
# # ============================================================================

# @app.post("/api/query", response_model=QueryResponse)
# async def process_query(
#     query_data: NLPQuery,
#     current_user: dict = Depends(get_current_user),
#     db=Depends(get_database)
# ):
#     """Process natural language query using LLaMA Agent"""
#     if query_data.department and query_data.department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied to this department")
    
#     try:
#         # Get LLaMA agent
#         agent = get_llama_agent()
        
#         # Prepare context
#         context = {
#             "department": query_data.department.value if query_data.department else None,
#             "user_role": current_user["role"],
#             "query_context": query_data.context or {}
#         }
        
#         # Add department data if specified
#         if query_data.department:
#             dept_data = generate_mock_kpi_data(query_data.department)
#             context["kpis"] = dept_data["kpis"]
#             context["chart_data"] = dept_data["chart_data"]
        
#         # Process with LLaMA agent
#         result = agent.process_query(query_data.query, context)
        
#         # Log activity
#         activity = {
#             "id": str(uuid.uuid4()),
#             "action": f"LLaMA Query: {query_data.query[:50]}...",
#             "user_id": current_user["id"],
#             "user_name": current_user["name"],
#             "timestamp": datetime.utcnow(),
#             "type": "llama_query_processed",
#             "department": query_data.department.value if query_data.department else None
#         }
        
#         await db.activities.insert_one(activity)
        
#         return {
#             "query": query_data.query,
#             "answer": result["answer"],
#             "insights": result.get("insights", []),
#             "chart_data": result.get("chart_data"),
#             "recommendations": result.get("recommendations", [])
#         }
        
#     except Exception as e:
#         logger.error(f"Query processing error: {str(e)}")
#         raise HTTPException(status_code=500, detail="Error processing query")

# # ============================================================================
# # AI ANALYSIS ENDPOINTS
# # ============================================================================

# @app.post("/api/analytics/llama-analysis")
# async def llama_comprehensive_analysis(
#     request_data: dict,
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Comprehensive department analysis using LLaMA Agent
#     """
#     department = request_data.get("department")
    
#     if department not in current_user["departments"]:
#         raise HTTPException(status_code=403, detail="Access denied")
    
#     try:
#         # Get analysis agent
#         analysis_agent = get_analysis_agent()
        
#         # Get department data
#         dept_data = generate_mock_kpi_data(department)
        
#         # Perform comprehensive analysis
#         result = analysis_agent.analyze_department_performance(
#             department=department,
#             kpis=dept_data["kpis"],
#             chart_data=dept_data["chart_data"]
#         )
        
#         return {
#             "department": department,
#             "analysis": result,
#             "generated_at": datetime.utcnow().isoformat()
#         }
        
#     except Exception as e:
#         logger.error(f"Comprehensive analysis error: {str(e)}")
#         raise HTTPException(status_code=500, detail="Analysis error")

# # ============================================================================
# # MAIN ENTRY POINT
# # ============================================================================

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
























import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, BackgroundTasks, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import json
from enum import Enum
import pandas as pd
from io import StringIO
import uuid
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import tempfile
import logging

# AI Agents
try:
    from ai_models.llama_agent import get_llama_agent
    from ai_models.analysis_agent import get_analysis_agent
except ImportError:
    # Fallback mock agents if real ones aren't available
    def get_llama_agent():
        class MockLlamaAgent:
            def process_query(self, query, context):
                return {
                    "answer": "Mock AI response: " + query[:50],
                    "insights": ["Mock insight 1", "Mock insight 2"],
                    "chart_data": None,
                    "recommendations": ["Mock recommendation"]
                }
        return MockLlamaAgent()
    
    def get_analysis_agent():
        class MockAnalysisAgent:
            def analyze_department_performance(self, department, kpis, chart_data):
                return {
                    "summary": f"Mock analysis for {department}",
                    "insights": ["Performance is stable", "Good growth observed"],
                    "recommendations": ["Continue current strategy"],
                    "trends": {"trend": "positive"},
                    "anomalies": []
                }
        return MockAnalysisAgent()

# MongoDB
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pymongo import ReturnDocument
from fastapi.responses import JSONResponse, Response

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# LIFESPAN & APP INITIALIZATION
# ============================================================================

from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MongoDB connection
    print("✅ Initializing Backend API with MongoDB...")
    
    # Initialize MongoDB connection
    app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    app.mongodb = app.mongodb_client[os.getenv("MONGODB_DB_NAME", "report_generator")]
    
    # Create indexes
    await create_indexes(app.mongodb)
    
    # Create default admin user if not exists
    admin_user = await app.mongodb.users.find_one({"email": "admin@company.com"})
    if not admin_user:
        admin_id = str(uuid.uuid4())
        admin_user = {
            "id": admin_id,
            "email": "admin@company.com",
            "password": get_password_hash("admin123"),
            "name": "Admin User",
            "role": UserRole.ADMIN,
            "departments": [Department.FINANCE, Department.HR, Department.SALES, 
                           Department.OPERATIONS, Department.COMPLIANCE],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await app.mongodb.users.insert_one(admin_user)
        print("📧 Default admin created: admin@company.com / admin123")
    
    # Create sample alerts if none exist
    alerts_count = await app.mongodb.alerts.count_documents({})
    if alerts_count == 0:
        sample_alerts = []
        for i in range(4):
            alert_id = str(uuid.uuid4())
            sample_alerts.append({
                "id": alert_id,
                "type": ["warning", "info", "success"][i % 3],
                "department": [Department.FINANCE, Department.HR, Department.SALES, Department.OPERATIONS][i],
                "message": f"Sample alert message {i+1}",
                "priority": [AlertPriority.HIGH, AlertPriority.MEDIUM, AlertPriority.LOW][i % 3],
                "created_at": datetime.utcnow(),
                "acknowledged": False,
                "created_by": admin_id
            })
        await app.mongodb.alerts.insert_many(sample_alerts)
    
    print("🚀 Server running at http://localhost:8000")
    print("📚 API docs available at http://localhost:8000/docs")
    
    yield  # Server is running
    
    # Cleanup: Close MongoDB connection
    print("Shutting down...")
    app.mongodb_client.close()

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Autonomous Report Generator API",
    description="Enterprise AI-powered reporting system with MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================================
# CORS CONFIGURATION
# ============================================================================

cors_origins = [
    "https://ai-autonomous-report-generator-hypr.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With", "*"],
    expose_headers=["*"]
)

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365  # 1 year for development & testing
REFRESH_TOKEN_EXPIRE_DAYS = 365

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "report_generator")

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"

class Department(str, Enum):
    FINANCE = "finance"
    HR = "hr"
    SALES = "sales"
    OPERATIONS = "operations"
    COMPLIANCE = "compliance"

class ReportType(str, Enum):
    PDF = "pdf"
    PPT = "ppt"
    EXCEL = "excel"

class ReportFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class AlertPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: UserRole
    departments: List[Department]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]

class TokenRefresh(BaseModel):
    refresh_token: str

class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: UserRole
    departments: List[Department]
    created_at: datetime

class ReportGenerate(BaseModel):
    title: str
    department: Department
    report_type: ReportType
    date_range: Dict[str, str]
    frequency: Optional[ReportFrequency] = None
    schedule: Optional[bool] = False

class Report(BaseModel):
    id: str
    title: str
    department: Department
    report_type: ReportType
    file_url: str
    size: str
    status: str
    created_by: str
    created_at: datetime

class NLPQuery(BaseModel):
    query: str
    department: Optional[Department] = None
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    query: str
    answer: str
    insights: List[str]
    chart_data: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None

class Alert(BaseModel):
    id: str
    type: str
    department: Department
    message: str
    priority: AlertPriority
    created_at: datetime
    acknowledged: bool = False

class CommentCreate(BaseModel):
    report_id: str
    content: str
    mentioned_users: Optional[List[str]] = []

class Comment(BaseModel):
    id: str
    report_id: str
    user_id: str
    user_name: str
    content: str
    mentioned_users: List[str]
    created_at: datetime
    replies: List[Dict[str, Any]] = []

class UserSettings(BaseModel):
    language: str = "english"
    theme: str = "light"
    report_format: ReportType = ReportType.PDF
    notifications: Dict[str, bool] = {
        "email": True,
        "slack": False,
        "teams": False
    }

class KPIData(BaseModel):
    department: Department
    kpis: List[Dict[str, Any]]
    chart_data: List[Dict[str, Any]]
    summary: str

# ============================================================================
# DATABASE UTILITIES
# ============================================================================

async def create_indexes(db):
    """Create database indexes for better performance"""
    # Users collection indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("role")
    await db.users.create_index("departments")
    
    # Reports collection indexes
    await db.reports.create_index("department")
    await db.reports.create_index("created_by")
    await db.reports.create_index("created_at")
    await db.reports.create_index([("department", 1), ("created_at", -1)])
    
    # Alerts collection indexes
    await db.alerts.create_index("department")
    await db.alerts.create_index("priority")
    await db.alerts.create_index("acknowledged")
    await db.alerts.create_index("created_at")
    
    # Comments collection indexes
    await db.comments.create_index("report_id")
    await db.comments.create_index("user_id")
    await db.comments.create_index("created_at")
    
    # Activities collection indexes
    await db.activities.create_index("user_id")
    await db.activities.create_index("timestamp")
    
    # New indexes for report files
    await db.report_files.create_index("report_id", unique=True)
    await db.report_files.create_index("created_at")
    
    # New collection for data uploads
    await db.data_uploads.create_index("uploaded_by")
    await db.data_uploads.create_index("department")
    await db.data_uploads.create_index("uploaded_at")
    
    print("✅ Database indexes created")

def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc and '_id' in doc:
        doc['id'] = str(doc['_id'])
        del doc['_id']
    
    # Convert ObjectId to string
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
    
    return doc

async def get_database():
    """Dependency to get database instance"""
    return app.mongodb

# ============================================================================
# AUTHENTICATION UTILITIES
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, 
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401, 
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception:
        raise HTTPException(
            status_code=401, 
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_database)
) -> dict:
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        # Check token type
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        user = None
        
        if db is not None and user_id:
            try:
                user = await db.users.find_one({"id": user_id})
                if not user:
                    user = await db.users.find_one({"email": user_id})
                if not user and ObjectId.is_valid(user_id):
                    user = await db.users.find_one({"_id": ObjectId(user_id)})
            except Exception as db_err:
                logger.warning(f"Database lookup warning in get_current_user: {db_err}")

        # Fallback to payload metadata if database record is missing
        if not user:
            dept_payload = payload.get("departments", ["finance", "hr", "sales", "operations", "compliance"])
            # Ensure departments are Department enums or strings matching Department enum values
            departments = []
            for d in dept_payload:
                try:
                    departments.append(Department(d.lower() if isinstance(d, str) else d))
                except ValueError:
                    pass
            if not departments:
                departments = [Department.FINANCE, Department.HR, Department.SALES, Department.OPERATIONS, Department.COMPLIANCE]

            user = {
                "id": user_id or "default-user-id",
                "email": payload.get("email", "user@company.com"),
                "name": payload.get("name", "Report Generator User"),
                "role": payload.get("role", "analyst"),
                "departments": departments,
                "created_at": datetime.utcnow()
            }
            return user

        return serialize_doc(user)
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def check_role(required_roles: List[UserRole]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# ============================================================================
# TOKEN REFRESH MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def add_token_refresh_header(request: Request, call_next):
    """Add token refresh header to responses for frontend handling"""
    response = await call_next(request)
    
    # If it's a 401 error, add the token refresh header
    if response.status_code == 401:
        response.headers["X-Token-Refresh"] = "true"
    
    return response

# ============================================================================
# CORS EXCEPTION HANDLING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        # Add CORS headers to request for preflight
        if request.method == "OPTIONS":
            return JSONResponse(
                content={"message": "OK"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, Origin, X-Requested-With, *"
                }
            )
        
        response = await call_next(request)
        
        # Ensure CORS headers are added to all responses
        origin = request.headers.get('origin')
        if origin and origin in cors_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
        elif "*" in cors_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
            
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Origin, X-Requested-With, *"
        
        return response
        
    except Exception as exc:
        # Handle exceptions and still add CORS headers
        import traceback
        logger.error(f"Unhandled exception: {str(exc)}")
        logger.error(traceback.format_exc())
        
        # Use JSONResponse instead of Response
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)}
        )
        
        origin = request.headers.get('origin')
        if origin and origin in cors_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
        elif "*" in cors_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
            
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Origin, X-Requested-With, *"
        
        return response

# ============================================================================
# AI INTEGRATION FUNCTIONS
# ============================================================================

def analyze_with_ai(query: str, data: Any) -> Dict[str, Any]:
    """Mock AI analysis function"""
    insights = [
        "Sales performance increased by 22% compared to previous quarter",
        "Technology sector showed strongest growth at 28%",
        "Customer retention improved by 15% through loyalty programs"
    ]
    
    recommendations = [
        "Increase marketing budget in high-performing regions by 12%",
        "Focus on customer retention strategies in underperforming segments",
        "Expand product line in technology sector based on demand trends"
    ]
    
    return {
        "insights": insights,
        "recommendations": recommendations,
        "confidence": 0.92
    }

def detect_anomalies(data: pd.DataFrame) -> List[Dict[str, Any]]:
    """Anomaly detection using ML"""
    anomalies = []
    if len(data) > 0:
        anomalies.append({
            "type": "spike",
            "metric": "expenses",
            "value": "+15%",
            "severity": "medium",
            "description": "Unusual increase in marketing expenses detected"
        })
    return anomalies

def generate_executive_summary(department: Department, data: Dict) -> str:
    """Generate AI-powered executive summary"""
    summaries = {
        Department.FINANCE: "Q2 financial performance exceeded expectations with 12.5% revenue growth. Operating margins improved to 25% through strategic cost optimization. Cash flow remains strong with $2.4M total revenue.",
        Department.HR: "Workforce expansion on track with 23 new hires. Attrition rate decreased to 8.2%, below industry average. Employee satisfaction scores improved to 87% following new wellness initiatives.",
        Department.SALES: "Outstanding quarter with 156 deals closed, representing 22% growth. Average deal size increased to $27K. Sales pipeline robust at $4.2M with 34% conversion rate.",
        Department.OPERATIONS: "Operational efficiency reached 94% with significant reduction in equipment downtime. Order volume increased 18% while maintaining 96% on-time delivery rate.",
        Department.COMPLIANCE: "All regulatory requirements met with 12 successful audits. Issue resolution rate at 89%. Risk assessment remains at Low level with proactive monitoring in place."
    }
    return summaries.get(department, "Performance metrics within expected parameters.")

def process_nlp_query(query: str, department: Optional[Department]) -> Dict[str, Any]:
    """Process natural language queries using AI"""
    query_lower = query.lower()
    
    if "sales" in query_lower or "revenue" in query_lower:
        return {
            "answer": "Sales performance for Q2 shows 22% growth with 156 deals closed. Revenue reached $2.4M with strong pipeline of $4.2M.",
            "chart_data": [
                {"month": "Jan", "sales": 540},
                {"month": "Feb", "sales": 675},
                {"month": "Mar", "sales": 756},
                {"month": "Apr", "sales": 594},
                {"month": "May", "sales": 810},
                {"month": "Jun", "sales": 837}
            ],
            "insights": [
                "Technology sector led growth with 28% increase",
                "Average deal size increased from $25K to $27K",
                "Conversion rate improved to 34%"
            ],
            "recommendations": [
                "Invest in high-performing sales channels",
                "Expand sales team in technology vertical"
            ]
        }
    elif "hr" in query_lower or "employee" in query_lower or "attrition" in query_lower:
        return {
            "answer": "HR metrics show positive trends with attrition decreasing to 8.2% and employee satisfaction at 87%.",
            "chart_data": [
                {"month": "Jan", "hires": 5, "exits": 3},
                {"month": "Feb", "hires": 8, "exits": 2},
                {"month": "Mar", "hires": 6, "exits": 4},
                {"month": "Apr", "hires": 7, "exits": 3},
                {"month": "May", "hires": 9, "exits": 5},
                {"month": "Jun", "hires": 4, "exits": 3}
            ],
            "insights": [
                "Net workforce growth of 5.2%",
                "Wellness programs contributed to improved satisfaction",
                "Retention in key departments above 95%"
            ],
            "recommendations": [
                "Continue investment in employee wellness",
                "Implement mentorship programs for new hires"
            ]
        }
    else:
        return {
            "answer": "Based on current data analysis, overall business metrics show positive growth across departments with 12% average improvement.",
            "insights": [
                "Revenue growth trending upward",
                "Operational efficiency at peak levels",
                "Customer satisfaction improving"
            ],
            "recommendations": [
                "Maintain current strategic initiatives",
                "Monitor emerging market trends"
            ]
        }

# ============================================================================
# MOCK DATA GENERATOR
# ============================================================================

def generate_mock_kpi_data(department: Department):
    kpi_mapping = {
        Department.FINANCE: {
            "kpis": [
                {"label": "Total Revenue", "value": "$2.4M", "change": "+12.5%", "positive": True},
                {"label": "Expenses", "value": "$1.8M", "change": "+8.2%", "positive": False},
                {"label": "Net Profit", "value": "$600K", "change": "+18.3%", "positive": True},
                {"label": "Profit Margin", "value": "25%", "change": "+2.1%", "positive": True}
            ],
            "chart_data": [
                {"month": "Jan", "revenue": 180, "expenses": 140},
                {"month": "Feb", "revenue": 200, "expenses": 150},
                {"month": "Mar", "revenue": 220, "expenses": 160},
                {"month": "Apr", "revenue": 240, "expenses": 180},
                {"month": "May", "revenue": 260, "expenses": 190},
                {"month": "Jun", "revenue": 280, "expenses": 200}
            ],
            "summary": "Q2 revenue grew by 12.5% with controlled expense management. Profit margins improved across all divisions."
        },
        Department.HR: {
            "kpis": [
                {"label": "Total Employees", "value": "342", "change": "+5.2%", "positive": True},
                {"label": "Attrition Rate", "value": "8.2%", "change": "-1.3%", "positive": True},
                {"label": "New Hires", "value": "23", "change": "+15%", "positive": True},
                {"label": "Satisfaction", "value": "87%", "change": "+3%", "positive": True}
            ],
            "chart_data": [
                {"month": "Jan", "hires": 5, "exits": 3},
                {"month": "Feb", "hires": 8, "exits": 2},
                {"month": "Mar", "hires": 6, "exits": 4},
                {"month": "Apr", "hires": 7, "exits": 3},
                {"month": "May", "hires": 9, "exits": 5},
                {"month": "Jun", "hires": 4, "exits": 3}
            ],
            "summary": "Workforce grew steadily with reduced attrition. Employee satisfaction improved through new wellness programs."
        },
        Department.SALES: {
            "kpis": [
                {"label": "Total Deals", "value": "156", "change": "+22%", "positive": True},
                {"label": "Conversion Rate", "value": "34%", "change": "+5%", "positive": True},
                {"label": "Pipeline Value", "value": "$4.2M", "change": "+28%", "positive": True},
                {"label": "Avg Deal Size", "value": "$27K", "change": "+8%", "positive": True}
            ],
            "chart_data": [
                {"month": "Jan", "deals": 20, "value": 540},
                {"month": "Feb", "deals": 25, "value": 675},
                {"month": "Mar", "deals": 28, "value": 756},
                {"month": "Apr", "deals": 22, "value": 594},
                {"month": "May", "deals": 30, "value": 810},
                {"month": "Jun", "deals": 31, "value": 837}
            ],
            "summary": "Outstanding sales performance with 22% growth in closed deals. Pipeline value reached all-time high."
        },
        Department.OPERATIONS: {
            "kpis": [
                {"label": "Efficiency", "value": "94%", "change": "+2%", "positive": True},
                {"label": "Downtime", "value": "2.3h", "change": "-15%", "positive": True},
                {"label": "Orders", "value": "1,234", "change": "+18%", "positive": True},
                {"label": "On-Time", "value": "96%", "change": "+3%", "positive": True}
            ],
            "chart_data": [
                {"month": "Jan", "efficiency": 91, "downtime": 3.2},
                {"month": "Feb", "efficiency": 92, "downtime": 2.8},
                {"month": "Mar", "efficiency": 93, "downtime": 2.5},
                {"month": "Apr", "efficiency": 94, "downtime": 2.3},
                {"month": "May", "efficiency": 94, "downtime": 2.1},
                {"month": "Jun", "efficiency": 95, "downtime": 1.9}
            ],
            "summary": "Operational efficiency improved with reduced equipment downtime. On-time delivery exceeds target."
        },
        Department.COMPLIANCE: {
            "kpis": [
                {"label": "Audits", "value": "12", "change": "0%", "positive": True},
                {"label": "Open Issues", "value": "3", "change": "-40%", "positive": True},
                {"label": "Resolved", "value": "89%", "change": "+12%", "positive": True},
                {"label": "Risk Level", "value": "Low", "change": "Stable", "positive": True}
            ],
            "chart_data": [
                {"month": "Jan", "audits": 2, "issues": 5},
                {"month": "Feb", "audits": 2, "issues": 4},
                {"month": "Mar", "audits": 2, "issues": 6},
                {"month": "Apr", "audits": 2, "issues": 5},
                {"month": "May", "audits": 2, "issues": 4},
                {"month": "Jun", "audits": 2, "issues": 3}
            ],
            "summary": "Compliance metrics remain strong with 89% issue resolution rate. All audits passed successfully."
        }
    }
    return kpi_mapping.get(department, kpi_mapping[Department.FINANCE])

# ============================================================================
# PDF GENERATION FUNCTIONS
# ============================================================================

async def generate_pdf_report(department: str, filename: str, data_preview: List[Dict], 
                            analysis_result: Dict, user_name: str) -> bytes:
    """Generate PDF report from AI analysis"""
    try:
        # Create a buffer for PDF
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                              topMargin=0.5*inch, bottomMargin=0.5*inch,
                              leftMargin=0.5*inch, rightMargin=0.5*inch)
        
        # Story to hold PDF elements
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#1E40AF'),
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#2D3748')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.HexColor('#4A5568')
        )
        
        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            leftIndent=20,
            textColor=colors.HexColor('#4A5568')
        )
        
        # Title
        dept_display = department.title() if department else "Unknown"
        title = Paragraph(f"AI Analysis Report - {dept_display} Department", title_style)
        story.append(title)
        
        # File info
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            alignment=1
        )
        story.append(Paragraph(f"<b>File:</b> {filename}", info_style))
        story.append(Paragraph(f"<b>Generated by:</b> {user_name}", info_style))
        story.append(Paragraph(f"<b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC", info_style))
        story.append(Spacer(1, 25))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        summary_text = analysis_result.get('summary', 'No summary available.')
        # Clean summary text - remove markdown and fix formatting
        summary_text = clean_text_for_pdf(summary_text)
        story.append(Paragraph(summary_text, normal_style))
        story.append(Spacer(1, 15))
        
        # Key Insights
        story.append(Paragraph("Key Insights", heading_style))
        insights = analysis_result.get('insights', [])
        if insights:
            for insight in insights:
                # Clean each insight text
                clean_insight = clean_text_for_pdf(insight)
                story.append(Paragraph(f"• {clean_insight}", bullet_style))
        else:
            story.append(Paragraph("No specific insights generated.", normal_style))
        story.append(Spacer(1, 15))
        
        # Recommendations
        story.append(Paragraph("Actionable Recommendations", heading_style))
        recommendations = analysis_result.get('recommendations', [])
        if recommendations:
            for rec in recommendations:
                # Clean each recommendation text
                clean_rec = clean_text_for_pdf(rec)
                story.append(Paragraph(f"• {clean_rec}", bullet_style))
        else:
            story.append(Paragraph("No specific recommendations generated.", normal_style))
        story.append(Spacer(1, 15))
        
        # Data Overview
        story.append(Paragraph("Data Overview", heading_style))
        if data_preview and len(data_preview) > 0:
            data_info = f"Dataset contains {len(data_preview)} sample rows with {len(data_preview[0]) if data_preview else 0} columns."
            story.append(Paragraph(data_info, normal_style))
            story.append(Spacer(1, 10))
        
        # Trends Analysis
        trends = analysis_result.get('trends', {})
        if trends and trends.get('trend') != 'unknown':
            story.append(Paragraph("Trend Analysis", heading_style))
            
            trend_info = []
            if trends.get('trend'):
                trend_info.append(f"<b>Overall Trend:</b> {trends['trend'].title()}")
            if trends.get('confidence'):
                trend_info.append(f"<b>Confidence Level:</b> {trends['confidence'].title()}")
            if trends.get('pattern'):
                clean_pattern = clean_text_for_pdf(trends['pattern'])
                trend_info.append(f"<b>Pattern:</b> {clean_pattern}")
            if trends.get('prediction'):
                clean_prediction = clean_text_for_pdf(trends['prediction'])
                trend_info.append(f"<b>Prediction:</b> {clean_prediction}")
            if trends.get('reasoning'):
                clean_reasoning = clean_text_for_pdf(trends['reasoning'])
                trend_info.append(f"<b>Reasoning:</b> {clean_reasoning}")
            
            for info in trend_info:
                story.append(Paragraph(info, normal_style))
            story.append(Spacer(1, 15))
        
        # Anomalies
        anomalies = analysis_result.get('anomalies', [])
        if anomalies:
            story.append(Paragraph("Detected Anomalies", heading_style))
            for i, anomaly in enumerate(anomalies[:5], 1):  # Show first 5 anomalies
                desc = clean_text_for_pdf(anomaly.get('description', 'N/A'))
                severity = anomaly.get('severity', 'N/A').title()
                anomaly_type = anomaly.get('type', 'N/A').title()
                
                anomaly_text = f"<b>Anomaly {i}:</b> {desc} | <b>Type:</b> {anomaly_type} | <b>Severity:</b> {severity}"
                story.append(Paragraph(anomaly_text, bullet_style))
            story.append(Spacer(1, 15))
        
        # Data Preview Table
        if data_preview and len(data_preview) > 0:
            story.append(Paragraph("Data Preview (First 10 Rows)", heading_style))
            
            # Create table data
            headers = list(data_preview[0].keys())
            table_data = [headers]
            
            for row in data_preview[:10]:
                # Clean and truncate cell values
                clean_row = []
                for val in row.values():
                    clean_val = str(val)
                    # Remove any markdown formatting
                    clean_val = clean_val.replace('*', '').replace('_', '').replace('#', '')
                    # Truncate long values
                    if len(clean_val) > 30:
                        clean_val = clean_val[:27] + '...'
                    clean_row.append(clean_val)
                table_data.append(clean_row)
            
            # Create table
            if len(table_data) > 1:
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F7FAFC')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')])
                ]))
                story.append(table)
                story.append(Spacer(1, 15))
        
        # Footer with generation info
        story.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=1
        )
        story.append(Paragraph("Generated by AI-Powered Report Generator", footer_style))
        story.append(Paragraph("Confidential - For Internal Use Only", footer_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        # Return a simple error PDF
        return generate_error_pdf(str(e))
    
def clean_text_for_pdf(text: str) -> str:
    """Clean text for PDF formatting - remove markdown and fix common issues"""
    if not text:
        return ""
    
    # Remove markdown formatting
    clean_text = text.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
    
    # Remove excessive newlines and spaces
    clean_text = ' '.join(clean_text.split())
    
    # Fix common AI response artifacts
    clean_text = clean_text.replace('•', '-')  # Replace bullet points with dashes
    clean_text = clean_text.replace('```', '')  # Remove code blocks
    clean_text = clean_text.replace('`', '')    # Remove inline code
    
    # Ensure proper sentence capitalization
    if clean_text and clean_text[0].islower():
        clean_text = clean_text[0].upper() + clean_text[1:]
    
    return clean_text

def generate_error_pdf(error_message: str) -> bytes:
    """Generate a simple error PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'ErrorTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        textColor=colors.red,
        alignment=1
    )
    story.append(Paragraph("Report Generation Error", title_style))
    story.append(Spacer(1, 20))
    
    # Error message
    normal_style = ParagraphStyle(
        'ErrorNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        textColor=colors.darkred,
        alignment=1
    )
    story.append(Paragraph("We encountered an issue while generating your report:", normal_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(error_message, normal_style))
    story.append(Spacer(1, 20))
    
    # Contact info
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        alignment=1
    )
    story.append(Paragraph("Please try again or contact support if the issue persists.", contact_style))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "Autonomous Report Generator API with MongoDB",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/register", response_model=Token)
async def register(user_data: UserRegister, db=Depends(get_database)):
    """Register a new user"""
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    
    user = {
        "id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "name": user_data.name,
        "role": user_data.role,
        "departments": user_data.departments,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.users.insert_one(user)
    
    # Create tokens
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    
    # Store refresh token
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"refresh_token": refresh_token, "updated_at": datetime.utcnow()}}
    )
    
    # Return token and user info
    user_response = {k: v for k, v in user.items() if k not in ["password", "refresh_token"]}
    user_response = serialize_doc(user_response)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user_response
    }

@app.post("/api/auth/login", response_model=Token)
async def login(credentials: UserLogin, db=Depends(get_database)):
    """Login with email and password"""
    # Find user by email
    user = await db.users.find_one({"email": credentials.email})
    
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create tokens with rich payload metadata
    payload_data = {
        "sub": user["id"],
        "email": user["email"],
        "name": user.get("name", "User"),
        "role": user.get("role", "analyst"),
        "departments": [d.value if hasattr(d, "value") else d for d in user.get("departments", [])]
    }
    access_token = create_access_token(payload_data)
    refresh_token = create_refresh_token({"sub": user["id"]})
    
    # Store refresh token
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"refresh_token": refresh_token, "updated_at": datetime.utcnow()}}
    )
    
    # Return tokens and user info
    user_response = {k: v for k, v in user.items() if k not in ["password", "refresh_token"]}
    user_response = serialize_doc(user_response)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user_response
    }

@app.post("/api/auth/refresh", response_model=Token)
async def refresh_token(
    refresh_data: TokenRefresh,
    db=Depends(get_database)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = jwt.decode(refresh_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        user = await db.users.find_one({"id": user_id})
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Verify refresh token matches stored one
        if user.get("refresh_token") != refresh_data.refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Create new tokens
        access_token = create_access_token({"sub": user_id})
        new_refresh_token = create_refresh_token({"sub": user_id})
        
        # Update stored refresh token
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"refresh_token": new_refresh_token, "updated_at": datetime.utcnow()}}
        )
        
        # Return user info without password
        user_response = {k: v for k, v in user.items() if k not in ["password", "refresh_token"]}
        user_response = serialize_doc(user_response)
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user_response
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {k: v for k, v in current_user.items() if k not in ["password", "refresh_token"]}

# ============================================================================
# CSV UPLOAD & ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/api/reports/upload-csv")
async def upload_csv_analysis(
    file: UploadFile = File(...),
    department: str = Form(None),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Upload CSV for AI analysis and report generation"""
    try:
        logger.info(f"Upload received: {file.filename}, department: {department}")
        
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400, 
                detail="Only CSV files are supported"
            )
        
        # Validate department
        if not department:
            raise HTTPException(
                status_code=400,
                detail="Department is required"
            )
        
        try:
            # Convert string to Department enum
            department_enum = Department(department.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid department: {department}. Must be one of: {[d.value for d in Department]}"
            )
        
        # Check if user has access to this department
        if department_enum not in current_user["departments"]:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied to {department} department"
            )
        
        # Read and parse CSV
        content = await file.read()
        logger.info(f"File size: {len(content)} bytes")
        
        try:
            csv_text = content.decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_text))
            logger.info(f"CSV parsed successfully: {len(df)} rows, {len(df.columns)} columns")
        except Exception as csv_error:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid CSV file: {str(csv_error)}"
            )
        
        # Basic data validation
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        if len(df.columns) == 0:
            raise HTTPException(status_code=400, detail="CSV file has no columns")
        
        # Convert DataFrame to list of dictionaries for AI processing
        data_records = df.to_dict('records')
        
        # Get AI agents
        try:
            llama_agent = get_llama_agent()
            analysis_agent = get_analysis_agent()
            logger.info("AI agents initialized successfully")
        except Exception as agent_error:
            logger.warning(f"AI agent initialization failed, using mock agents: {str(agent_error)}")
            # Use mock agents as fallback
            llama_agent = get_llama_agent()
            analysis_agent = get_analysis_agent()
        
        # Prepare context for AI analysis
        context = {
            "department": department_enum.value,
            "data_preview": data_records[:5],  # First 5 records for context
            "columns": list(df.columns),
            "total_records": len(df),
            "data_summary": {
                "columns": list(df.columns),
                "total_rows": len(df),
                "data_types": df.dtypes.to_dict()
            }
        }
        
        # Generate AI analysis with error handling
        try:
            analysis_result = analysis_agent.analyze_department_performance(
                department=department_enum.value,
                kpis=[{"label": col, "value": "Analyzing...", "change": "0%", "positive": True} for col in df.columns[:4]],
                chart_data=data_records[:10]  # Use first 10 records for chart data
            )
            logger.info("AI analysis completed successfully")
        except Exception as analysis_error:
            logger.error(f"AI analysis failed: {str(analysis_error)}")
            # Provide fallback analysis
            analysis_result = {
                "summary": f"Basic analysis of {len(df)} records from {file.filename} in {department} department",
                "insights": [
                    f"Data loaded successfully with {len(df)} rows and {len(df.columns)} columns",
                    "AI analysis encountered issues but data is ready for review"
                ],
                "recommendations": [
                    "Review data quality and structure",
                    "Consider manual analysis for specific insights"
                ],
                "trends": {
                    "trend": "unknown", 
                    "pattern": "Analysis limited due to technical issues",
                    "prediction": "Further analysis required",
                    "confidence": "low",
                    "reasoning": "AI analysis encountered technical difficulties"
                },
                "anomalies": []
            }
        
        # Generate PDF report
        try:
            pdf_report = await generate_pdf_report(
                department=department_enum.value,  # Use string value, not enum
                filename=file.filename,
                data_preview=data_records[:10],
                analysis_result=analysis_result,
                user_name=current_user["name"]
            )
            logger.info("PDF report generated successfully")
        except Exception as pdf_error:
            logger.error(f"PDF generation failed: {str(pdf_error)}")
            # Generate a simple error PDF instead of failing completely
            pdf_report = generate_error_pdf(f"PDF generation issue: {str(pdf_error)}")
        
        # Store report in database
        report_id = str(uuid.uuid4())
        report_data = {
            "id": report_id,
            "title": f"AI Analysis - {file.filename}",
            "department": department_enum.value,
            "report_type": ReportType.PDF.value,
            "file_url": f"/api/reports/download/{report_id}",
            "size": f"{(len(content) / 1024 / 1024):.1f} MB",
            "status": "completed",
            "created_by": current_user["id"],
            "created_by_name": current_user["name"],
            "created_at": datetime.utcnow(),
            "source": "csv_upload",
            "original_filename": file.filename,
            "analysis_data": analysis_result
        }
        
        await db.reports.insert_one(report_data)
        
        # Store PDF file
        await db.report_files.insert_one({
            "report_id": report_id,
            "pdf_content": base64.b64encode(pdf_report).decode('utf-8'),
            "created_at": datetime.utcnow()
        })
        
        # Log activity
        activity = {
            "id": str(uuid.uuid4()),
            "action": f"CSV Analysis Report Generated: {file.filename}",
            "user_id": current_user["id"],
            "user_name": current_user["name"],
            "timestamp": datetime.utcnow(),
            "type": "csv_analysis",
            "department": department_enum.value
        }
        await db.activities.insert_one(activity)
        
        return {
            "message": "CSV analyzed and report generated successfully",
            "report_id": report_id,
            "analysis": analysis_result,
            "data_preview": {
                "columns": list(df.columns),
                "first_five_rows": data_records[:5],
                "total_rows": len(df)
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_csv_analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/reports/download/{report_id}")
async def download_report_pdf(
    report_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Download generated PDF report"""
    try:
        logger.info(f"Download request for report: {report_id}")
        
        # Get report metadata
        report = await db.reports.find_one({"id": report_id})
        if not report:
            logger.error(f"Report not found: {report_id}")
            raise HTTPException(status_code=404, detail="Report not found")
        
        logger.info(f"Found report: {report['title']} for department: {report['department']}")
        
        # Check user access
        user_departments = [d.value if isinstance(d, Department) else d for d in current_user["departments"]]
        if report["department"] not in user_departments:
            logger.error(f"Access denied: User {current_user['id']} cannot access {report['department']}")
            raise HTTPException(status_code=403, detail="Access denied to this report")
        
        # Get PDF content
        pdf_file = await db.report_files.find_one({"report_id": report_id})
        if not pdf_file:
            logger.error(f"PDF file not found for report: {report_id}")
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        logger.info(f"PDF file found, size: {len(pdf_file['pdf_content'])} bytes")
        
        # Decode PDF content
        try:
            pdf_content = base64.b64decode(pdf_file["pdf_content"])
            logger.info(f"PDF decoded successfully, size: {len(pdf_content)} bytes")
        except Exception as decode_error:
            logger.error(f"PDF decode error: {str(decode_error)}")
            raise HTTPException(status_code=500, detail="Corrupted PDF file")
        
        # Validate PDF content
        if len(pdf_content) == 0:
            logger.error("PDF content is empty")
            raise HTTPException(status_code=500, detail="Empty PDF file")
        
        # Return PDF file
        from fastapi.responses import Response
        filename = f"{report['title']}.pdf".replace(" ", "_")
        
        logger.info(f"Returning PDF file: {filename}")
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_content)),
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"PDF download error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Error downloading PDF: {str(e)}"
        )
    
@app.get("/api/reports/{report_id}/debug")
async def debug_report(
    report_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Debug endpoint to check report status"""
    try:
        # Get report metadata
        report = await db.reports.find_one({"id": report_id})
        if not report:
            return {"error": "Report not found"}
        
        # Get PDF file info
        pdf_file = await db.report_files.find_one({"report_id": report_id})
        
        return {
            "report_found": bool(report),
            "report_data": {
                "id": report.get("id"),
                "title": report.get("title"),
                "department": report.get("department"),
                "created_at": report.get("created_at"),
                "status": report.get("status")
            },
            "pdf_file_found": bool(pdf_file),
            "pdf_file_data": {
                "has_content": bool(pdf_file and pdf_file.get("pdf_content")),
                "content_length": len(pdf_file.get("pdf_content", "")) if pdf_file else 0,
                "created_at": pdf_file.get("created_at") if pdf_file else None
            } if pdf_file else None,
            "user_access": report["department"] in current_user["departments"] if report else False
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/reports/{report_id}/preview")
async def preview_report(
    report_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get report preview and analysis data"""
    report = await db.reports.find_one({"id": report_id})
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report["department"] not in current_user["departments"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "report": serialize_doc(report),
        "analysis": report.get("analysis_data", {})
    }

# ============================================================================
# CORS PREFLIGHT HANDLERS
# ============================================================================

@app.options("/api/reports/upload-csv")
async def options_upload_csv():
    """Handle CORS preflight for CSV upload"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, Origin, X-Requested-With, *",
            "Access-Control-Allow-Credentials": "true"
        }
    )

@app.options("/api/reports/download/{report_id}")
async def options_download_report():
    """Handle CORS preflight for download"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, Origin, X-Requested-With, *",
            "Access-Control-Allow-Credentials": "true"
        }
    )

# ============================================================================
# DASHBOARD & KPI ENDPOINTS
# ============================================================================

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get overall dashboard statistics"""
    total_reports = await db.reports.count_documents({
        "department": {"$in": current_user["departments"]}
    })
    
    active_alerts = await db.alerts.count_documents({
        "department": {"$in": current_user["departments"]},
        "acknowledged": False
    })
    
    recent_activities = await db.activities.find({
        "user_id": current_user["id"]
    }).sort("timestamp", -1).limit(5).to_list(length=5)
    
    recent_activities = [serialize_doc(activity) for activity in recent_activities]
    
    return {
        "total_reports": total_reports,
        "active_alerts": active_alerts,
        "departments": len(current_user["departments"]),
        "data_sources": 23,
        "recent_activity": recent_activities
    }

@app.get("/api/dashboard/kpis/{department}")
async def get_department_kpis(
    department: Department,
    current_user: dict = Depends(get_current_user)
):
    """Get KPIs for a specific department"""
    if department not in current_user["departments"]:
        raise HTTPException(status_code=403, detail="Access denied to this department")
    
    data = generate_mock_kpi_data(department)
    return {
        "department": department,
        "kpis": data["kpis"],
        "chart_data": data["chart_data"],
        "summary": data["summary"],
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/api/dashboard/activity")
async def get_recent_activity(
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get recent activity log"""
    activities = await db.activities.find({
        "user_id": current_user["id"]
    }).sort("timestamp", -1).limit(limit).to_list(length=limit)
    
    activities = [serialize_doc(activity) for activity in activities]
    
    total_activities = await db.activities.count_documents({
        "user_id": current_user["id"]
    })
    
    return {
        "activities": activities,
        "total": total_activities
    }

# ============================================================================
# REPORT MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/reports/generate")
async def generate_report(
    report_data: ReportGenerate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Generate a new report"""
    if report_data.department not in current_user["departments"]:
        raise HTTPException(status_code=403, detail="Access denied to this department")
    
    report_id = str(uuid.uuid4())
    
    report = {
        "id": report_id,
        "title": report_data.title,
        "department": report_data.department,
        "report_type": report_data.report_type,
        "file_url": f"/reports/{report_id}.{report_data.report_type}",
        "size": "2.4 MB",
        "status": "completed",
        "created_by": current_user["id"],
        "created_by_name": current_user["name"],
        "created_at": datetime.utcnow(),
        "date_range": report_data.date_range,
        "frequency": report_data.frequency,
        "scheduled": report_data.schedule
    }
    
    await db.reports.insert_one(report)
    
    # Add to activity log
    activity = {
        "id": str(uuid.uuid4()),
        "action": f"Report Generated: {report_data.title}",
        "user_id": current_user["id"],
        "user_name": current_user["name"],
        "timestamp": datetime.utcnow(),
        "type": "report_generated",
        "department": report_data.department
    }
    
    await db.activities.insert_one(activity)
    
    return serialize_doc(report)

@app.get("/api/reports")
async def get_reports(
    department: Optional[Department] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get list of reports"""
    query = {"department": {"$in": current_user["departments"]}}
    
    if department:
        if department not in current_user["departments"]:
            raise HTTPException(status_code=403, detail="Access denied to this department")
        query["department"] = department
    
    reports = await db.reports.find(query).sort("created_at", -1).limit(limit).to_list(length=limit)
    reports = [serialize_doc(report) for report in reports]
    
    total = await db.reports.count_documents(query)
    
    return {
        "reports": reports,
        "total": total
    }

@app.get("/api/reports/{report_id}")
async def get_report(
    report_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get specific report details"""
    report = await db.reports.find_one({"id": report_id})
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report["department"] not in current_user["departments"]:
        raise HTTPException(status_code=403, detail="Access denied to this report")
    
    return serialize_doc(report)

@app.delete("/api/reports/{report_id}")
async def delete_report(
    report_id: str,
    current_user: dict = Depends(check_role([UserRole.ADMIN, UserRole.MANAGER])),
    db=Depends(get_database)
):
    """Delete a report (Admin/Manager only)"""
    report = await db.reports.find_one({"id": report_id})
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    await db.reports.delete_one({"id": report_id})
    
    # Also delete related comments
    await db.comments.delete_many({"report_id": report_id})
    
    return {"message": "Report deleted successfully", "report_id": report_id}

# ============================================================================
# NLP QUERY ENGINE ENDPOINTS
# ============================================================================

@app.post("/api/query", response_model=QueryResponse)
async def process_query(
    query_data: NLPQuery,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    """Process natural language query using LLaMA Agent"""
    if query_data.department and query_data.department not in current_user["departments"]:
        raise HTTPException(status_code=403, detail="Access denied to this department")
    
    try:
        # Get LLaMA agent
        agent = get_llama_agent()
        
        # Prepare context
        context = {
            "department": query_data.department.value if query_data.department else None,
            "user_role": current_user["role"],
            "query_context": query_data.context or {}
        }
        
        # Add department data if specified
        if query_data.department:
            dept_data = generate_mock_kpi_data(query_data.department)
            context["kpis"] = dept_data["kpis"]
            context["chart_data"] = dept_data["chart_data"]
        
        # Process with LLaMA agent
        result = agent.process_query(query_data.query, context)
        
        # Log activity
        activity = {
            "id": str(uuid.uuid4()),
            "action": f"LLaMA Query: {query_data.query[:50]}...",
            "user_id": current_user["id"],
            "user_name": current_user["name"],
            "timestamp": datetime.utcnow(),
            "type": "llama_query_processed",
            "department": query_data.department.value if query_data.department else None
        }
        
        await db.activities.insert_one(activity)
        
        return {
            "query": query_data.query,
            "answer": result["answer"],
            "insights": result.get("insights", []),
            "chart_data": result.get("chart_data"),
            "recommendations": result.get("recommendations", [])
        }
        
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing query")

# ============================================================================
# AI ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/api/analytics/llama-analysis")
async def llama_comprehensive_analysis(
    request_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Comprehensive department analysis using LLaMA Agent
    """
    department = request_data.get("department")
    
    if department not in current_user["departments"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get analysis agent
        analysis_agent = get_analysis_agent()
        
        # Get department data
        dept_data = generate_mock_kpi_data(department)
        
        # Perform comprehensive analysis
        result = analysis_agent.analyze_department_performance(
            department=department,
            kpis=dept_data["kpis"],
            chart_data=dept_data["chart_data"]
        )
        
        return {
            "department": department,
            "analysis": result,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Comprehensive analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis error")

# ============================================================================
# PUBLIC ENDPOINTS (No authentication required)
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Autonomous Report Generator"
    }

@app.get("/api/public/info")
async def public_info():
    """Public information about the API"""
    return {
        "name": "Autonomous Report Generator API",
        "version": "1.0.0",
        "description": "Enterprise AI-powered reporting system",
        "features": [
            "CSV analysis and report generation",
            "AI-powered insights",
            "Multi-department support",
            "PDF report generation",
            "Natural language queries"
        ]
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with CORS headers"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, Origin, X-Requested-With, *"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with CORS headers"""
    logger.error(f"Unhandled exception: {str(exc)}")
    import traceback
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept, Origin, X-Requested-With, *"
        }
    )

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)