#!/bin/bash
# Simple one-command setup for Website RAG Q&A System

set -e

echo "🤖 Website RAG Q&A System - One-Container Setup"
echo "==============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker is installed"

# Check if we need sudo for docker
if ! docker ps &> /dev/null; then
    echo "ℹ️  Using sudo for Docker commands (permission required)"
    DOCKER_CMD="sudo docker"
else
    DOCKER_CMD="docker"
fi

# Check if .env file exists and has API key
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database Configuration
DATABASE_URL=sqlite:///./data/app.db

# Application Settings
DEBUG=True
ENVIRONMENT=development

# API Configuration
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost", "http://localhost:80"]
EOF

    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file and add your OpenAI API key"
    echo "   You can get an API key from: https://platform.openai.com/api-keys"
    echo ""
    echo "   Edit with: nano .env"
    echo "   Change: OPENAI_API_KEY=sk-your-openai-api-key-here"
    echo ""
    read -p "Press Enter after you've added your OpenAI API key..."
fi

# Validate OpenAI API key
if grep -q "sk-your-openai-api-key-here" .env; then
    echo "❌ Please update your OpenAI API key in the .env file"
    echo "   Current placeholder: sk-your-openai-api-key-here"
    exit 1
fi

echo "✅ Environment file configured"

# Stop any existing container
echo "🧹 Cleaning up any existing containers..."
$DOCKER_CMD stop website-rag-qa 2>/dev/null || true
$DOCKER_CMD rm website-rag-qa 2>/dev/null || true

# Build the Docker image
echo "🏗️  Building Docker image..."
echo "   This may take a few minutes on first run..."
$DOCKER_CMD build -t website-rag-qa .

# Run the container
echo "🚀 Starting the container..."
$DOCKER_CMD run -d \
  --name website-rag-qa \
  --env-file .env \
  -p 80:80 \
  -v $(pwd)/data:/app/data \
  website-rag-qa

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10




# Check if container is running
if $DOCKER_CMD ps | grep -q website-rag-qa; then
    echo ""
    echo "🎉 SUCCESS! Your RAG system is running!"
    echo ""
    echo "📱 Access your application:"
    echo "   • Complete System: http://localhost/dashboard"
    echo "   • API Documentation: http://localhost/docs"
    echo "   • Health Check: http://localhost/health"
    echo ""
    echo "🏃‍♂️ Next steps:"
    echo "   1. Open http://localhost/dashboard in your browser"
    echo "   2. Click 'Add Website' to add your first website"
    echo "   3. Use the chat widget to ask questions!"
    echo ""
    echo "📋 Useful commands:"
    echo "   • View logs: $DOCKER_CMD logs -f website-rag-qa"
    echo "   • Stop system: $DOCKER_CMD stop website-rag-qa"
    echo "   • Restart: $DOCKER_CMD restart website-rag-qa"
    echo "   • Remove: $DOCKER_CMD rm -f website-rag-qa"
    echo ""
    echo "🆘 Need help? Check the README.md"
else
    echo "❌ Something went wrong. Check the logs:"
    echo "   $DOCKER_CMD logs website-rag-qa"
    exit 1
fi