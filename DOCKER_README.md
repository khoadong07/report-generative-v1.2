# Docker Setup for Weekly Report Streamlit App

## Quick Start

### 1. Build and Run with Docker Compose

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### 2. Access the App

Open your browser and navigate to:
```
http://localhost:13333
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with your API credentials:

```env
API_KEY=your_api_key_here
BASE_URL=your_base_url_here
```

### Port Configuration

The app runs on port **13333** by default. To change the port:

1. Edit `docker-compose.yml`:
```yaml
ports:
  - "YOUR_PORT:13333"
```

2. Or set environment variable:
```bash
export STREAMLIT_PORT=YOUR_PORT
docker-compose up -d
```

## Docker Commands

### Build Only
```bash
docker-compose build
```

### Run in Foreground (see logs)
```bash
docker-compose up
```

### Run in Background
```bash
docker-compose up -d
```

### Stop Container
```bash
docker-compose down
```

### Restart Container
```bash
docker-compose restart
```

### View Logs
```bash
# All logs
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

### Execute Commands in Container
```bash
# Open bash shell
docker-compose exec streamlit-app bash

# Run Python script
docker-compose exec streamlit-app python your_script.py
```

## Development Mode

The `docker-compose.yml` is configured for development with code mounted as a volume:

```yaml
volumes:
  - .:/app  # Live code reload
```

For **production**, comment out this line to bake code into the image.

## Volumes

The following directories are mounted as volumes:

- `./output` - Generated HTML/PDF files
- `./demo` - Demo Excel files
- `.` (dev only) - Source code for live reload

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs streamlit-app

# Check container status
docker-compose ps
```

### Port already in use
```bash
# Find process using port 13333
lsof -i :13333

# Kill the process or change port in docker-compose.yml
```

### Permission issues with volumes
```bash
# Fix permissions
sudo chown -R $USER:$USER ./output ./demo
```

### Rebuild after code changes
```bash
# Rebuild and restart
docker-compose up -d --build
```

### Clear everything and start fresh
```bash
# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Rebuild from scratch
docker-compose up -d --build
```

## Health Check

The container includes a health check that runs every 30 seconds:

```bash
# Check health status
docker-compose ps

# Manual health check
curl http://localhost:13333/_stcore/health
```

## Production Deployment

For production deployment:

1. **Remove development volume mount** in `docker-compose.yml`:
   ```yaml
   # Comment out this line:
   # - .:/app
   ```

2. **Set production environment variables**:
   ```yaml
   environment:
     - STREAMLIT_SERVER_HEADLESS=true
     - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   ```

3. **Use a reverse proxy** (nginx/traefik) for SSL/HTTPS

4. **Set resource limits**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
       reservations:
         cpus: '1'
         memory: 2G
   ```

## System Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

## Features Included

- ✅ Streamlit app on port 13333
- ✅ PDF export with WeasyPrint
- ✅ Auto-restart on failure
- ✅ Health checks
- ✅ Volume persistence for output files
- ✅ Development mode with live reload
- ✅ Environment variable configuration

## Support

For issues or questions, check:
- Container logs: `docker-compose logs -f`
- Health status: `docker-compose ps`
- Streamlit docs: https://docs.streamlit.io/
