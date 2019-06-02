# The Littlest Web-GBAT

## Instructions: 
- start redis service:
    - `docker run --name dash-cache -p 6379:6379 -d redis redis-server --appendonly yes`
- build docker container and run service
    - `docker build -t geo-app .`
    - `docker run geo-app python app.py`