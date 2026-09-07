FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod .
COPY cmd ./cmd
RUN go build -o /worker ./cmd/integration-worker

FROM alpine:3.21
COPY --from=build /worker /worker
USER 65532:65532
ENTRYPOINT ["/worker"]
