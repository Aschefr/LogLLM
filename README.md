# LogLLM - Log Monitoring with LLM Analysis

[![Docker Pulls](https://img.shields.io/docker/pulls/logllm/logllm)](https://hub.docker.com/r/logllm/logllm)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

LogLLM is a self-contained Docker application that monitors log files in real-time, analyzes critical errors using a local LLM (Ollama/LocalAI), and generates notifications.

## 🎯 Features

- **Real-time Log Monitoring**: Watch multiple log files simultaneously
- **LLM-Powered Analysis**: Analyze errors using Ollama or LocalAI
- **Configurable Notifications**: Send alerts via Discord, Telegram, Email, or Apprise
- **Web-Based GUI**: Sonarr/Radarr-inspired dark theme interface
- **Zero Configuration Files**: All settings managed through the web interface
- **SQLite Storage**: Local database for configuration and analysis history
- **Unraid Ready**: Community Apps template included

## 🚀 Quick Start

### Using Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/Aschefr/logllm
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

### Using Unraid

1. Install via Community Apps
2. Configure volumes:
   - **App Data**: `/mnt/user/appdata/logllm`
   - **Logs Directory**: `/mnt/user/logs`
3. Access at `http://your-unraid-ip:8080`

## 📁 Volume Configuration

| Volume | Internal Path | Description |
|--------|--------------|-------------|
| Config/Data | `/app/appdata` | SQLite database and configuration |
| Log Source | `/logs` | Directory to scan for log files |

## ⚙️ Configuration

### LLM Integration

#### Ollama
```
Endpoint: http://host.docker.internal:11434
Model: llama2 (or any installed model)
```

#### LocalAI
```
Endpoint: http://host.docker.internal:8080
Model: llama-2-7b (or any available model)
```

### Notification Providers

#### Discord
- Use a webhook URL
- Format: `https://discord.com/api/webhooks/...`

#### Telegram
- Requires bot token and chat ID
- Format: `bot_token:chat_id`

#### Email
- Uses Apprise library
- Format: `smtp://user:pass@smtp.server.com:port`

#### Apprise
- Supports 70+ notification services
- See: https://github.com/caronc/apprise

## 🧪 Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test file
python -m unittest tests.test_config_manager

# Run with coverage
python -m unittest discover tests -v
```

## 🏗️ Architecture

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: Bootstrap 5 + Vanilla JS
- **File Monitoring**: Watchdog library
- **Notifications**: Apprise library

## 🔒 Security

- No hardcoded credentials
- All sensitive data stored in `/app/appdata`
- No external API calls except configured LLM/notification endpoints
- SQLite database encrypted at rest (optional)

## 📊 Web Interface

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

## 🐛 Troubleshooting

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

### Tests fail
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip install -r requirements.txt

# Run tests
python run_tests.py
```

## 🤝 Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 📞 Support

For issues and questions, please open a GitHub issue or contact the maintainers.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM inference
- [Apprise](https://github.com/caronc/apprise) for notification support
- [Sonarr/Radarr](https://github.com/Sonarr/Sonarr) for UI inspiration
- [Watchdog](https://github.com/gorakhargosh/watchdog) for file monitoring

## 📈 Roadmap

- [ ] Add support for multiple LLM providers (OpenAI, Anthropic)
- [ ] Implement log rotation and archival
- [ ] Add advanced filtering and search
- [ ] Create mobile-responsive design
- [ ] Add API documentation (OpenAPI/Swagger)
- [ ] Implement user authentication
- [ ] Add export functionality (CSV, JSON)
- [ ] Create plugin system for custom analyzers
