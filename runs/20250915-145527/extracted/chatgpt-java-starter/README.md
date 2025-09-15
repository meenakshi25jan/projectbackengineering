# ChatGPT Java Starter (Spring Boot + HTML)

A minimal, runnable starter that integrates **OpenAI (ChatGPT) Responses API** in Java via the official SDK and serves a simple HTML UI.

## Requirements
- Java 21 (or 17+ if you change the pom)
- Maven 3.9+
- An OpenAI API key

## Quick Start
```bash
# 1) Set your key (PowerShell)
$env:OPENAI_API_KEY="sk-..."

# macOS/Linux:
export OPENAI_API_KEY="sk-..."

# 2) Run the app
mvn spring-boot:run

# 3) Open the UI
# Navigate to http://localhost:8080
```

## Files
- `src/main/java/com/example/chat/ChatApplication.java` – Spring Boot app
- `src/main/java/com/example/chat/OpenAIConfig.java` – OpenAI client bean
- `src/main/java/com/example/chat/WebCorsConfig.java` – permissive CORS for /api/**
- `src/main/java/com/example/chat/ChatController.java` – POST /api/chat endpoint
- `src/main/resources/static/index.html` – Simple HTML page with fetch()
- `src/main/resources/application.properties` – basic config

## Notes
- The controller uses the **Responses API** and `ChatModel.GPT_4O_MINI`. You can switch to any supported model.
- For production: restrict CORS, add timeouts/retries, and mask sensitive data in logs.
