// main.go
package main

import "fmt"

func doubleit(val int) int {
	return val * 3 // should be * 2
}

func main() {
	fmt.Printf("doubleit 2: %d\n", doubleit(2))
	fmt.Printf("doubleit 4: %d\n", doubleit(4))
	fmt.Printf("doubleit 8: %d\n", doubleit(8))
}
