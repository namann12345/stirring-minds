#!/bin/bash

echo "🔗 Testing Frontend-Backend Connection..."
echo ""

# Test 1: Backend Health Check
echo "1️⃣ Testing Backend Health..."
BACKEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)

if [ "$BACKEND_RESPONSE" -eq 200 ]; then
    echo "✅ Backend is running and responding"
else
    echo "❌ Backend is not responding (HTTP $BACKEND_RESPONSE)"
    echo "   Make sure backend is running: cd backend && python main.py"
    exit 1
fi

# Test 2: Backend API Docs
echo ""
echo "2️⃣ Testing Backend API Docs..."
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)

if [ "$DOCS_RESPONSE" -eq 200 ]; then
    echo "✅ API Documentation is accessible"
else
    echo "❌ API Docs not accessible (HTTP $DOCS_RESPONSE)"
fi

# Test 3: Login Endpoint
echo ""
echo "3️⃣ Testing Login Endpoint..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.com","password":"admin123"}' \
  -w "%{http_code}" -o /dev/null)

if [ "$LOGIN_RESPONSE" -eq 200 ]; then
    echo "✅ Login endpoint working"
else
    echo "❌ Login endpoint failed (HTTP $LOGIN_RESPONSE)"
fi

# Test 4: Frontend
echo ""
echo "4️⃣ Testing Frontend..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/)

if [ "$FRONTEND_RESPONSE" -eq 200 ]; then
    echo "✅ Frontend is running and responding"
else
    echo "❌ Frontend is not responding (HTTP $FRONTEND_RESPONSE)"
    echo "   Make sure frontend is running: cd frontend && npm run dev"
    exit 1
fi

# Summary
echo ""
echo "======================================"
echo "🎉 CONNECTION TEST COMPLETE"
echo "======================================"
echo ""
echo "✅ Backend: http://localhost:8000"
echo "✅ Frontend: http://localhost:5173"
echo "✅ API Docs: http://localhost:8000/docs"
echo ""
echo "🔐 Default Login:"
echo "   Email: admin@company.com"
echo "   Password: admin123"
echo ""
echo "Ready to test in browser! 🚀"