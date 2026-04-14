# LogLLM - Log Monitoring with LLM Analysis

LogLLM is a self-contained Docker application that monitors log files in real-time, analyzes critical errors using a local LLM (Ollama/LocalAI), and generates notifications.

## Features

- **Real-time Log Monitoring**: Watch multiple log files simultaneously
- **LLM-Powered Analysis**: Analyze errors using Ollama or LocalAI
- **Configurable Notifications**: Send alerts via Discord, Telegram, Email, or Apprise
- **Web-Based GUI**: Sonarr/Radarr-inspired dark theme interface
- **Zero Configuration Files**: All settings managed through the web interface
- **SQLite Storage**: Local database for configuration and analysis history

## Quick Start

### Using Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/yourusername/logllm.git
cd logllm
```

2. Create the required directories:
```bash
mkdir -p appdata logs
```

3. Start the container:
```bash
docker-compose up -d
```

4. Access the web interface at `http://localhost:8080`

### Using Docker Directly

```bash
docker run -d \
  --name logllm \
  -p 8080:8080 \
  -v $(pwd)/appdata:/app/appdata \
  -v $(pwd)/logs:/logs \
  logllm/logllm:latest
```

## Configuration

### Volumes

| Volume | Internal Path | Description |
|--------|--------------|-------------|
| Config/Data | `/app/appdata` | SQLite database and configuration |
| Log Source | `/logs` | Directory to scan for log files |

### Environment Variables

No environment variables are required. All configuration is done through the web interface.

## Web Interface

### Dashboard
- Monitoring status overview
- Active logs count
- Errors detected today
- LLM usage statistics
- Recent alerts list

### Logs Management
- View all configured log monitors
- See analysis history per log
- Mark analyses as read/ignored
- Manual scan trigger

### Wizard
- Step-by-step log monitor setup
- Select files from mounted volumes
- Configure AI settings per log
- Set notification preferences

### Settings
- LLM provider configuration (Ollama/LocalAI)
- System and user prompts
- Notification provider setup
- Test connections before saving

## LLM Integration

### Ollama
```
Endpoint: http://host.docker.internal:11434
Model: llama2 (or any installed model)
```

### LocalAI
```
Endpoint: http://host.docker.internal:8080
Model: llama-2-7b (or any available model)
```

## Notification Providers

### Discord
- Use a webhook URL
- Format: `https://discord.com/api/webhooks/...`

### Telegram
- Requires bot token and chat ID
- Format: `bot_token:chat_id`

### Email
- Uses Apprise library
- Format: `smtp://user:pass@smtp.server.com:port`

### Apprise
- Supports 70+ notification services
- See: https://github.com/caronc/apprise

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Building Docker Image
```bash
docker build -t logllm:latest .
```

## Architecture

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: Bootstrap 5 + Vanilla JS
- **File Monitoring**: Watchdog library
- **Notifications**: Apprise library

## Security

- No hardcoded credentials
- All sensitive data stored in `/app/appdata`
- No external API calls except configured LLM/notification endpoints

## Troubleshooting

### Container won't start
```bash
docker logs logllm
```

### LLM connection fails
- Check that Ollama/LocalAI is accessible from the container
- Use `host.docker.internal` for Docker Desktop
- Verify the endpoint in Settings

### No files found in wizard
- Ensure log files are mounted to `/logs` directory
- Files must be readable by the container

## License

MIT License

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.

## Support

For issues and questions, please open a GitHub issue.
