#!/bin/bash
# Health check script for Docker containers

API_URL="${1:-http://localhost:8000}"

echo "Checking Sutra-Markdown health at $API_URL..."

# Check API health endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/health)

if [ "$response" = "200" ]; then
    echo "✅ API is healthy"
    exit 0
else
    echo "❌ API is unhealthy (HTTP $response)"
    exit 1
fi
