FROM golang:1.21-alpine

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
# Use go run for development so volume mounts work correctly
CMD ["go", "run", "main.go"]
