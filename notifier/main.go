package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/redis/go-redis/v9"
)

func main() {
	redisURL := os.Getenv("REDIS_URL")
	if redisURL == "" {
		redisURL = "redis://redis:6379/0"
		log.Println("REDIS_URL is not set, using default:", redisURL)
	}

	botToken := os.Getenv("BOT_TOKEN")
	if botToken == "" {
		log.Println("WARNING: BOT_TOKEN is not set. Telegram notifications will fail.")
	}

	opts, err := redis.ParseURL(redisURL)
	if err != nil {
		log.Fatalf("Failed to parse REDIS_URL: %v", err)
	}

	client := redis.NewClient(opts)
	ctx := context.Background()

	// Wait for Redis to be ready
	for i := 0; i < 5; i++ {
		_, err := client.Ping(ctx).Result()
		if err == nil {
			break
		}
		log.Printf("Waiting for Redis... (%d/5)", i+1)
		time.Sleep(2 * time.Second)
	}

	pubsub := client.Subscribe(ctx, "notifications")
	defer pubsub.Close()

	fmt.Println("StockUp Notifier Service started. Listening on 'notifications' channel...")

	ch := pubsub.Channel()

	for msg := range ch {
		// Example message format: "user_id|Message text"
		fmt.Printf("Received message: %s\n", msg.Payload)
		// TODO: Parse message and use Telegram API (HTTP POST) to send to user
	}
}
