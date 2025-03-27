FROM golang:latest

WORKDIR /app

COPY . /src

WORKDIR /src

RUN go build -o simpleopen simple.go

CMD ["./simpleopen"]
