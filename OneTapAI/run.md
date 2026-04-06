🚀 How to Run ZIEL-MAS                                                                                                        
                                                                                                               
  Prerequisites
                                                                                                                                
  Make sure you have these installed:
  - Python 3.9+                                                                                                                 
  - Node.js 18+                                             
  - MongoDB (running on port 27017)
  - Redis (running on port 6379)
  - GLM API Key                                                                                                                 
  
  Step-by-Step Setup                                                                                                            
                                                            
  1. Install Dependencies

  # Install Python dependencies
  pip install -r backend/requirements.txt

  # Install Node.js dependencies
  cd frontend
  npm install
  cd ..

  2. Configure Environment

  # Copy the example environment file
  cp .env.example .env

  # Edit .env with your configuration
  nano .env  # or use your preferred editor

  Minimum required in .env:                                                                                                     
  # Get your GLM API key from: https://open.bigmodel.cn/
  GLM_API_KEY=your-glm-api-key-here                                                                                             
                                                            
  # Database connections
  MONGODB_URI=mongodb://localhost:27017
  REDIS_URI=redis://localhost:6379/0

  # Security (generate secure random strings)
  JWT_SECRET=your-super-secret-jwt-key
  ENCRYPTION_KEY=your-32-byte-encryption-key

  3. Start Services

  Open 4 separate terminals:

  Terminal 1 - Redis:
  redis-server
              
  Terminal 2 - MongoDB:
  mongod                                                                                                                        
  
  Terminal 3 - Backend:                                                                                                         
  python backend/main.py                                    

  Terminal 4 - Frontend:
  cd frontend
  npm run dev

  4. Access the Application

  - Frontend: http://localhost:3000
  - Backend API: http://localhost:8000
  - API Docs: http://localhost:8000/docs

  Quick Test

  1. Open http://localhost:3000
  2. Enter this intent: "Send test email to john@example.com"
  3. Click "Create Task"                                                                                                        
  4. Copy the execution link
  5. Click "Execute Now" to run it                                                                                              
                                                            
  Run Demo Workflows

  # See example workflows in action
  python tests/demo_workflows.py

  Troubleshooting

  Port already in use?
  # Change ports in .env:
  BACKEND_PORT=8001  # For backend

  MongoDB connection error?
  # Make sure MongoDB is running:
  brew services start mongodb-community  # macOS
  sudo systemctl start mongod            # Linux
                                                
  Redis connection error?
  # Make sure Redis is running:                                                                                                 
  redis-server
                                                                                                                                
  Import errors?                                            
  # Install from backend directory:
  cd backend
  pip install -r requirements.txt

  Production Deployment

  For production, see DEPLOYMENT.md for:
  - Environment configuration
  - Security setup
  - Scaling recommendations
  - Monitoring setup
