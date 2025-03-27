package main

import (
	"log"
	"os"
)

func main() {
	file, err := os.Open("testfile")
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	// Read some data to ensure file system interaction
	buf := make([]byte, 128)
	_, err = file.Read(buf)
	if err != nil {
		log.Fatal(err)
	}
}
