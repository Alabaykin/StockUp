package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/redis/go-redis/v9"
)

type Notification struct {
	Type         string  `json:"type"`
	ProductName  string  `json:"product_name"`
	ProductEmoji string  `json:"product_emoji"`
	FamilyID     string  `json:"family_id"`
	Subscribers  []int64 `json:"subscribers"`
	UserName     string  `json:"user_name,omitempty"` // For shopping requests
}

func main() {
	redisURL := os.Getenv("REDIS_URL")
	if redisURL == "" {
		redisURL = "redis://redis:6379/0"
	}

	botToken := os.Getenv("BOT_TOKEN")
	if botToken == "" || botToken == "YOUR_TELEGRAM_BOT_TOKEN" {
		log.Println("WARNING: BOT_TOKEN is not set. Telegram notifications will ONLY be printed to console.")
	}

	opts, err := redis.ParseURL(redisURL)
	if err != nil {
		log.Fatalf("Failed to parse REDIS_URL: %v", err)
	}

	client := redis.NewClient(opts)
	ctx := context.Background()

	// Wait for Redis
	for i := 0; i < 5; i++ {
		if _, err := client.Ping(ctx).Result(); err == nil {
			break
		}
		time.Sleep(2 * time.Second)
	}

	pubsub := client.Subscribe(ctx, "notifications")
	defer pubsub.Close()

	log.Println("🚀 StockUp Notifier Service started.")

	ch := pubsub.Channel()
	for msg := range ch {
		var n Notification
		if err := json.Unmarshal([]byte(msg.Payload), &n); err != nil {
			log.Printf("Error: %v", err)
			continue
		}

		processNotification(n, botToken)
	}
}

func processNotification(n Notification, token string) {
	var message string
	
	switch n.Type {
	case "out_of_stock":
		message = fmt.Sprintf("⚠️ *Out of Stock!*\n\n%s %s is finished. Time to buy more!", n.ProductEmoji, n.ProductName)
	case "shopping_request":
		message = fmt.Sprintf("🛒 *Shopping Request*\n\n%s says we need: %s %s", n.UserName, n.ProductEmoji, n.ProductName)
	case "back_in_stock":
		message = fmt.Sprintf("✨ *Снова в наличии!*\n\n%s %s снова в наличии! (куплено %s)", n.ProductEmoji, n.ProductName, n.UserName)
	case "request_fulfilled":
		message = fmt.Sprintf("✅ *Запрос выполнен!*\n\n%s %s запрашивали в семью — товар успешно куплен %s!", n.ProductEmoji, n.ProductName, n.UserName)
	default:
		message = fmt.Sprintf("🔔 *Notification*\n\n%s %s needs attention.", n.ProductEmoji, n.ProductName)
	}

	log.Printf("📢 Event: %s | Family: %s | Users: %v", n.Type, n.FamilyID[:8], n.Subscribers)

	if token == "" || token == "YOUR_TELEGRAM_BOT_TOKEN" {
		return
	}

	// Send to each subscriber
	for _, userID := range n.Subscribers {
		sendTelegramMessage(token, userID, message)
	}
}

func sendTelegramMessage(token string, chatID int64, text string) {
	url := fmt.Sprintf("https://api.telegram.org/bot%s/sendMessage", token)
	
	payload := map[string]interface{}{
		"chat_id":    chatID,
		"text":       text,
		"parse_mode": "Markdown",
	}
	
	jsonPayload, _ := json.Marshal(payload)
	
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonPayload))
	if err != nil {
		log.Printf("Failed to send to %d: %v", chatID, err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		log.Printf("Telegram API returned error for %d: %s", chatID, resp.Status)
	} else {
		log.Printf("✅ Message sent to %d", chatID)
	}
}
