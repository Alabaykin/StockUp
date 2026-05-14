FROM golang:1.21-alpine

WORKDIR /app

COPY go.mod ./
# RUN go mod download # Раскомментировать когда добавим зависимости

COPY . .
# RUN go build -o notifier main.go

CMD ["go", "run", "main.go"]
