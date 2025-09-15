package com.example.chat;

import org.springframework.web.bind.annotation.*;

import com.openai.client.OpenAIClient;
import com.openai.models.ChatModel;
import com.openai.models.responses.ResponseCreateParams;
import com.openai.models.responses.Response;

@RestController
@RequestMapping("/api/chat")

public class ChatController {

    private final OpenAIClient client;

    public ChatController(OpenAIClient client){ this.client = client; }

    public record ChatRequest(String message) {}
    public record ChatReply(String text) {}

    @PostMapping
    public ChatReply chat(@RequestBody ChatRequest req) {
        if (req == null || req.message() == null || req.message().isBlank()) {
            return new ChatReply("Please enter a message.");
        }
        ResponseCreateParams params = ResponseCreateParams.builder()
                .model(ChatModel.GPT_4O_MINI)
                .input(req.message())
                .build();
        Response resp = client.responses().create(params);
        return new ChatReply(resp.outputText());
    }
}
