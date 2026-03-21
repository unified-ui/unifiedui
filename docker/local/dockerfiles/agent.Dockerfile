FROM golang:1.24-alpine

WORKDIR /app

RUN apk add --no-cache git ca-certificates tzdata curl && \
    go install github.com/air-verse/air@v1.61.7

COPY go.mod go.sum ./
RUN go mod download

EXPOSE 8085

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8085/api/v1/agent-service/health || exit 1

CMD ["air", "-c", ".air.toml"]
