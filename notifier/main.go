package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
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
}

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
		var n Notification
		err := json.Unmarshal([]byte(msg.Payload), &n)
		if err != nil {
			log.Printf("Error unmarshaling notification: %v", err)
			continue
		}

		fmt.Printf("📢 [NOTIFICATION] Family %s is OUT OF STOCK: %s %s. Notifying users: %v\n", 
			n.FamilyID[:8], n.ProductEmoji, n.ProductName, n.Subscribers)
		
		// TODO: Implement actual Telegram API call here
		// Example: sendNotificationToFamily(n.FamilyID, "Item out of stock: ...")
	}
}
