package main

import (
	"log"
	"os"
	"syscall"
	"testing"
)

func BenchmarkStandardOpen(b *testing.B) {
	for i := 0; i < b.N; i++ {
		f, err := os.Open("testfile")
		if err != nil {
			log.Fatal(err)
		}
		f.Close()
	}
}

func BenchmarkOptimizedOpen(b *testing.B) {
	for i := 0; i < b.N; i++ {
		f, err := os.OpenFile("testfile", os.O_RDONLY|syscall.O_DIRECT, 0666)
		if err != nil {
			log.Fatal(err)
		}
		f.Close()
	}
}
