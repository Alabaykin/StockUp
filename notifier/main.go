package main

import (
	"fmt"
	"log"
	"os"
)

func main() {
	redisURL := os.Getenv("REDIS_URL")
	if redisURL == "" {
		log.Println("REDIS_URL is not set, using default")
	}

	fmt.Println("StockUp Notifier Service started. Waiting for messages...")
	
	// Бесконечный цикл для предотвращения закрытия контейнера
	select {}
}
