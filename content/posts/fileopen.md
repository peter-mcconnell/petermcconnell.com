+++
title = "How to Open a File in Linux: A Deep Dive"
date = "2025-03-04T08:16:50Z"
author = "Peter McConnell"

cover = "https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/tux.png"
tags = ["linux", "filesystems"]
keywords = ["linux", "filesystems", "ext4", "kernel", "syscalls"]
description = "A detailed exploration of the layers involved when opening a file on Linux (Ubuntu 24.04), including syscalls, compatibility checks, and performance optimizations using Golang"
showFullContent = false
readingTime = false
hideComments = false
color = "" #color from the theme settings
+++

Introduction
------------

Opening a file is a fundamental operation in any operating system, yet under the hood, it involves numerous layers of abstraction, compatibility checks, and system interactions. In this post, we take an in-depth look at what happens when you open a file on Linux with Golang on Ubuntu 24.04, breaking it down from user-space functions to kernel syscalls and file system interactions. We will then explore how to optimize file opening in Golang, demonstrating the impact with a benchmark.

The Layered Breakdown of Opening a File
---------------------------------------

### User-Space API Call

When a program opens a file, it typically calls a standard function from the C library (glibc in most Linux distributions):

```c
FILE *fp = fopen("example.txt", "r");
```

Or in Golang:

```go
f, err := os.Open("example.txt")
if err != nil {
    log.Fatal(err)
}
defer f.Close()
```

These high-level calls abstract away the complexity of interacting with the Linux kernel directly.

### libc and System Compatibility Checks

Before making a direct system call, glibc (or Go's runtime) performs compatibility checks:

- Pathname Resolution: Resolves symbolic links, checks if the file exists, and follows chroot or namespace constraints.

- Access Control: Determines whether the process has permission to open the file based on the effective user ID (UID) and group ID (GID).

- Environment Factors: If `LD_PRELOAD` is set, dynamic linker tricks may alter how file opening occurs (e.g., intercepting calls).

### Syscalls Involved in Opening a File

After the user-space checks, a system call is issued to the kernel. The primary syscall for opening a file is:

```c
int fd = open("example.txt", O_RDONLY);
```

In Golang this looks like:

```go
fd, err := unix.Open("example.txt", unix.O_RDONLY, 0)
```

The open() syscall triggers a sequence of actions within the kernel:

- VFS (Virtual File System) Layer: Interprets the syscall and determines which file system (ext4, XFS, NFS, etc.) the file resides on.

- Permissions Check: Validates access using UID/GID and POSIX ACLs.

- File Descriptor Allocation: Assigns a file descriptor if the file is accessible.

- Dentry and Inode Lookup: Translates the file path to an inode (using the dentry cache if available).

- Filesystem-Specific Handling: Ext4, for example, may check its journal before allowing access.

### Kernel Space Operations

When a file open request reaches the kernel, several sophisticated mechanisms come into play:

#### 1. VFS (Virtual File System) Layer
- Path Lookup: The VFS performs a path walk operation (namei lookup) to resolve the file location
- Mount Point Traversal: Checks if the path crosses different mount points
- File System Type Detection: Determines which concrete filesystem implementation to use

#### 2. Kernel Caching Mechanisms

##### Dentry Cache (dcache)
- Maintains a lookup cache of directory entries
- Structure includes parent directory, name, and inode reference
- Uses an LRU (Least Recently Used) algorithm for cache management
- Typical entry size: ~100 bytes

##### Inode Cache
- Caches the file metadata (inode) information
- Includes file size, permissions, timestamps, and block mappings
- Reduces disk reads for frequently accessed files
- Memory footprint: ~300-400 bytes per inode

##### Page Cache
- Caches actual file contents in memory
- Uses the buddy allocator for memory management
- Implements read-ahead for sequential access patterns
- Default read-ahead window: 128KB on most systems

### Physical Disk Operations

When cache misses occur, the kernel must interact with the physical disk:

#### 1. Block Layer Operations
- Request Queue Management: Merges adjacent requests
- I/O Scheduler: Reorders requests for optimal disk access (e.g., deadline scheduler)
- Block Size Management: Typically 4KB blocks on modern systems

#### 2. Device Driver Layer
- Translates block requests to device commands
- Handles interrupt processing
- Manages DMA (Direct Memory Access) operations

#### 3. Physical Disk Access
- Seek Time: 5-10ms for HDDs, ~0.1ms for SSDs
- Rotational Latency: ~4ms for 7200 RPM drives (HDDs only)
- Transfer Time: Depends on interface (SATA/NVMe) and media type

#### 4. Performance Considerations
- IOPS (Input/Output Operations Per Second)
  - HDDs: 100-200 IOPS
  - SSDs: 10,000-100,000 IOPS
  - NVMe: Up to 1,000,000 IOPS
- Block alignment impact on performance
- Journal transaction overhead for journaling filesystems

### Error Handling and Common Pitfalls

#### 1. Resource Exhaustion

```go
// Common mistake: not checking ulimit
for i := 0; i < 1000000; i++ {
    f, _ := os.Open("file.txt") // DON'T ignore errors!
    // f never closed - will hit ulimit
}

// Better approach
f, err := os.Open("file.txt")
if err != nil {
    return fmt.Errorf("open file: %w", err)
}
defer f.Close()
```

#### 2. Race Conditions

- File existence races between check and open
- Symlink attacks in privileged programs
- File descriptor leaks in error paths

```go
// WRONG: Race condition
if _, err := os.Stat("file.txt"); err == nil {
    f, err := os.Open("file.txt") // File might be gone now!
    // ...
}

// BETTER: Handle errors appropriately
f, err := os.Open("file.txt")
if err != nil {
    if os.IsNotExist(err) {
        // Handle non-existent file
    }
    return err
}
defer f.Close()
```

#### 3. System-Level Constraints

- File descriptor limits (`ulimit -n`)
- Filesystem-specific limitations:
  - Path length (typically 255 bytes)
  - Maximum file size (filesystem dependent)
  - Inode exhaustion

#### 4. Performance Impact Points

- Opening files in tight loops
- Not using buffered I/O when appropriate
- Incorrect buffer sizes for the workload
- Not considering filesystem journal overhead

### File Opening Optimizations in Golang

Using os.Open() in Go is simple, but specifying additional flags can improve performance, especially for high-throughput applications:

#### Optimization Techniques

Use `O_DIRECT` to bypass page cache when needed:

```go
f, err := os.OpenFile("example.txt", os.O_RDONLY|unix.O_DIRECT, 0666)
```

Reduce system calls with O_CLOEXEC (avoiding unnecessary file descriptor inheritance):

```go
f, err := os.OpenFile("example.txt", os.O_RDONLY|unix.O_CLOEXEC, 0666)
```

For high-performance applications, consider mmap for direct memory access:

```go
data, err := syscall.Mmap(fd, 0, length, syscall.PROT_READ, syscall.MAP_SHARED)
```

### Benchmark: Default vs. Optimized File Open in Golang

We'll benchmark file opening performance in Go under different conditions. I'm doing this from a Ubuntu 24.04 x86_64 EC2 on amazon linux (us-east-1) using the root volume.


#### Setup

We create a 1GB test file:

```bash
dd if=/dev/urandom of=testfile bs=1M count=1024
```

Then, we compare performance between os.Open() and optimized opening:

```go
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
```

We can run this test with:

```sh
go test -bench=. -run=^$ main_test.go
```

#### Results

| Method               | Time per Operation |
| -------------------- |------------------- |
| Standard `os.Open`   | 2523 ns/op         |
| Optimized `O_DIRECT` | 2515 ns/op         |
| syscall.Pread        | 1571 ns/op         |

syscall.Pread is ~38% faster than `os.Open()` + `Read()`

- This confirms that avoiding unnecessary file descriptor state changes (e.g., lseek()) improves efficiency.
- pread allows direct reading without modifying the file offset, reducing overhead.

`O_DIRECT` did not provide significant benefits.

- This suggests that our workload was small enough that bypassing the page cache isn’t useful.
- O_DIRECT typically benefits large file reads where cache pollution should be minimized.

#### Pushing the benchmarks a little further

Curious how different buffer sizes impact performance and how things look when actually reading line-by-line and performing some operations on that data I've extended the bench test a little more:

```go
package main

import (
	"bufio"
	"bytes"
	"golang.org/x/sys/unix"
	"crypto/md5"
	"fmt"
	"io"
	"log"
	"os"
	"regexp"
	"sync"
	"syscall"
	"testing"
)

const (
	filePath = "testfile"
	logFile = "biglogfile.log"
	bufferSize = 4096
	numWorkers = 4
	chunkSize = 1024 * 1024 * 10
)

func readFileWithMmapAndHash(filePath string) ([]byte, error) {
	fd, err := syscall.Open(filePath, syscall.O_RDONLY, 0666)
	if err != nil {
		return nil, err
	}
	defer syscall.Close(fd)

	stat := &syscall.Stat_t{}
	if err := syscall.Fstat(fd, stat); err != nil {
		return nil, err
	}
	size := int(stat.Size)

	data, err := unix.Mmap(fd, 0, size, unix.PROT_READ, unix.MAP_SHARED)
	if err != nil {
		return nil, err
	}
	defer unix.Munmap(data)

	hasher := md5.New()
	_, _ = hasher.Write(data)
	return hasher.Sum(nil), nil
}

func readFileWithOsOpenFile(filePath string) error {
	f, err := os.OpenFile(filePath, os.O_RDONLY, 0666)
	if err != nil {
		return err
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		_ = scanner.Text() // read line, discard output for benchmarking
	}

	return scanner.Err()
}

func readFileWithOsOpenFileAndHash(filePath string) ([]byte, error) {
	f, err := os.OpenFile(filePath, os.O_RDONLY, 0666)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	hasher := md5.New()
	_, err = io.Copy(hasher, f) // Use io.Copy for efficient reading
	if err != nil {
		return nil, err
	}

	return hasher.Sum(nil), nil
}

func readFileWithPreadAndHash(filePath string) ([]byte, error) {
	fd, err := syscall.Open(filePath, syscall.O_RDONLY, 0666)
	if err != nil {
		return nil, err
	}
	defer syscall.Close(fd)

	buf := make([]byte, bufferSize)
	var offset int64
	hasher := md5.New()

	for {
		n, err := syscall.Pread(fd, buf, offset)
		if n == 0 || err != nil {
			break
		}
		offset += int64(n)
		_, _ = hasher.Write(buf[:n])
	}

	return hasher.Sum(nil), nil
}

func readFileWithPreadLineByLine(filePath string) error {
	fd, err := syscall.Open(filePath, syscall.O_RDONLY, 0666)
	if err != nil {
		return err
	}
	defer syscall.Close(fd)

	buf := make([]byte, bufferSize)
	var offset int64
	var partialLine bytes.Buffer

	for {
		n, err := syscall.Pread(fd, buf, offset)
		if n == 0 || err != nil {
			break
		}
		offset += int64(n)

		scanner := bufio.NewScanner(bytes.NewReader(buf[:n]))
		scanner.Split(bufio.ScanLines)

		for scanner.Scan() {
			line := scanner.Text()

			if len(line) > 0 && line[len(line)-1] != '\n' {
				partialLine.WriteString(line)
			} else {
				// uncomment to actually print - you probably don't want to do this
				// fmt.Println(partialLine.String() + line)
				partialLine.Reset()
			}
		}

		if partialLine.Len() > 0 {
			partialLine.WriteByte('\n')
		}
	}

	return nil
}

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

func BenchmarkPread(b *testing.B) {
	for i := 0; i < b.N; i++ {
		fd, err := syscall.Open(filePath, syscall.O_RDONLY, 0666)
		if err != nil {
			log.Fatal(err)
		}
		buf := make([]byte, bufferSize)
		_, err = syscall.Pread(fd, buf, 0)
		if err != nil {
			log.Fatal(err)
		}
		syscall.Close(fd)
	}
}

func BenchmarkPreadSmallBufSize(b *testing.B) {
	for i := 0; i < b.N; i++ {
		fd, err := syscall.Open(filePath, syscall.O_RDONLY, 0666)
		if err != nil {
			log.Fatal(err)
		}
		buf := make([]byte, 1024)
		_, err = syscall.Pread(fd, buf, 0)
		if err != nil {
			log.Fatal(err)
		}
		syscall.Close(fd)
	}
}

func BenchmarkPreadSmallerBufSize(b *testing.B) {
	for i := 0; i < b.N; i++ {
		fd, err := syscall.Open(filePath, syscall.O_RDONLY, 0666)
		if err != nil {
			log.Fatal(err)
		}
		buf := make([]byte, 512)
		_, err = syscall.Pread(fd, buf, 0)
		if err != nil {
			log.Fatal(err)
		}
		syscall.Close(fd)
	}
}


func BenchmarkPreadLargeBufSize(b *testing.B) {
	for i := 0; i < b.N; i++ {
		fd, err := syscall.Open(filePath, syscall.O_RDONLY, 0666)
		if err != nil {
			log.Fatal(err)
		}
		buf := make([]byte, 8096)
		_, err = syscall.Pread(fd, buf, 0)
		if err != nil {
			log.Fatal(err)
		}
		syscall.Close(fd)
	}
}

func BenchmarkPreadReadWholeFile(b *testing.B) {
	for i := 0; i < b.N; i++ {
		err := readFileWithPreadLineByLine(filePath)
		if err != nil {
			log.Fatal(err)
		}
	}
}

func BenchmarkOsOpenFileReadWholeFile(b *testing.B) {
	for i := 0; i < b.N; i++ {
		err := readFileWithOsOpenFile(filePath)
		if err != nil {
			log.Fatal(err)
		}
	}
}

func BenchmarkPreadReadWholeFileAndHash(b *testing.B) {
	var hashResult []byte
	for i := 0; i < b.N; i++ {
		hash, err := readFileWithPreadAndHash(filePath)
		if err != nil {
			log.Fatal(err)
		}
		hashResult = hash
	}
	fmt.Printf("MD5 (syscall.Pread): %x\n", hashResult)
}

func BenchmarkOsOpenFileReadWholeFileAndHash(b *testing.B) {
	var hashResult []byte
	for i := 0; i < b.N; i++ {
		hash, err := readFileWithOsOpenFileAndHash(filePath)
		if err != nil {
			log.Fatal(err)
		}
		hashResult = hash
	}
	fmt.Printf("MD5 (os.OpenFile): %x\n", hashResult)
}

func BenchmarkMmapReadWholeFileAndHash(b *testing.B) {
	var hashResult []byte
	for i := 0; i < b.N; i++ {
		hash, err := readFileWithMmapAndHash(filePath)
		if err != nil {
			log.Fatal(err)
		}
		hashResult = hash
	}
	fmt.Printf("MD5 (mmap): %x\n", hashResult) // Print hash once
}

var searchPattern = regexp.MustCompile(`ERROR`)

// Uses syscall.Pread to read a specific file chunk and scan for matches
func searchFileWithPread(filePath string, startOffset, length int64, results chan int, wg *sync.WaitGroup) {
	defer wg.Done()

	fd, err := syscall.Open(filePath, syscall.O_RDONLY, 0666)
	if err != nil {
		log.Fatal(err)
	}
	defer syscall.Close(fd)

	buf := make([]byte, length)
	_, err = syscall.Pread(fd, buf, startOffset)
	if err != nil {
		log.Fatal(err)
	}

	// Convert to string and scan for regex matches
	count := len(searchPattern.FindAllString(string(buf), -1))
	results <- count
}

// Uses os.OpenFile with bufio.Scanner to read and process lines
func searchFileWithOpenFile(filePath string, startOffset, length int64, results chan int, wg *sync.WaitGroup) {
	defer wg.Done()

	f, err := os.OpenFile(filePath, os.O_RDONLY, 0666)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	// Seek to start position
	_, err = f.Seek(startOffset, 0)
	if err != nil {
		log.Fatal(err)
	}

	scanner := bufio.NewScanner(f)
	scanner.Buffer(make([]byte, 1024*64), 1024*64) // Larger buffer

	count := 0
	for scanner.Scan() {
		if searchPattern.MatchString(scanner.Text()) {
			count++
		}
		// Stop when reaching chunk limit
		seek, err := f.Seek(0, 1)
		if err != nil {
			panic(err)
		}
		if seek >= startOffset+length {
			break
		}
	}

	results <- count
}

// Benchmark: Multi-threaded search using syscall.Pread
func BenchmarkPreadRegexSearch(b *testing.B) {
	for i := 0; i < b.N; i++ {
		results := make(chan int, numWorkers)
		var wg sync.WaitGroup

		// Get file size
		fi, _ := os.Stat(logFile)
		fileSize := fi.Size()
		chunkSize := fileSize / int64(numWorkers)

		// Start workers
		for j := 0; j < numWorkers; j++ {
			start := int64(j) * chunkSize
			wg.Add(1)
			go searchFileWithPread(logFile, start, chunkSize, results, &wg) // ✅ Pass &wg
		}

		// Separate goroutine to close channel **after** all goroutines finish
		go func() {
			wg.Wait()  // ✅ Wait for all workers to finish before closing
			close(results)
		}()

		// Sum all results
		totalMatches := 0
		for matchCount := range results {
			totalMatches += matchCount
		}

		fmt.Printf("Matches found (Pread): %d\n", totalMatches)
	}
}

// Benchmark: Multi-threaded search using os.OpenFile
func BenchmarkOpenFileRegexSearch(b *testing.B) {
	for i := 0; i < b.N; i++ {
		results := make(chan int, numWorkers)
		var wg sync.WaitGroup

		// Get file size
		fi, _ := os.Stat(logFile)
		fileSize := fi.Size()
		chunkSize := fileSize / int64(numWorkers)

		// Start workers
		for j := 0; j < numWorkers; j++ {
			start := int64(j) * chunkSize
			wg.Add(1)
			go searchFileWithOpenFile(logFile, start, chunkSize, results, &wg)
		}

		// Separate goroutine to close the channel **after all workers finish**
		go func() {
			wg.Wait()
			close(results)
		}()

		// Sum all results
		totalMatches := 0
		for matchCount := range results {
			totalMatches += matchCount
		}

		fmt.Printf("Matches found (OpenFile): %d\n", totalMatches)
	}
}
```

Running this we yield the following results:

```sh
ubuntu@ip-192-168-0-13:~/blog$ go test -bench=. -run=^$ main_test.go
goos: linux
goarch: amd64
cpu: Intel(R) Xeon(R) Platinum 8375C CPU @ 2.90GHz
BenchmarkStandardOpen-8                     	  470482	      2520 ns/op
BenchmarkOptimizedOpen-8                    	  459942	      2530 ns/op
BenchmarkPread-8                            	  761684	      1586 ns/op
BenchmarkPreadSmallBufSize-8                	  775428	      1542 ns/op
BenchmarkPreadSmallerBufSize-8              	  777808	      1544 ns/op
BenchmarkPreadLargeBufSize-8                	  720202	      1656 ns/op
BenchmarkPreadReadWholeFile-8               	       2	 867923642 ns/op
BenchmarkOsOpenFileReadWholeFile-8          	       2	 590298956 ns/op
MD5 (syscall.Pread): e196fdf7806a4385382a8567ece65598
BenchmarkPreadReadWholeFileAndHash-8        	       1	1610504490 ns/op
MD5 (os.OpenFile): e196fdf7806a4385382a8567ece65598
BenchmarkOsOpenFileReadWholeFileAndHash-8   	       1	1535824016 ns/op
MD5 (mmap): e196fdf7806a4385382a8567ece65598
BenchmarkMmapReadWholeFileAndHash-8         	       1	1454061237 ns/op
Matches found (Pread): 998321
BenchmarkPreadRegexSearch-8                 	Matches found (Pread): 998321
Matches found (Pread): 998321
Matches found (Pread): 998321
Matches found (Pread): 998321
Matches found (Pread): 998321
Matches found (Pread): 998321
Matches found (Pread): 998321
Matches found (Pread): 998321
Matches found (Pread): 998321
Matches found (Pread): 998321
Matches found (Pread): 998321
Matches found (Pread): 998321
       5	 206179610 ns/op
Matches found (OpenFile): 997413
BenchmarkOpenFileRegexSearch-8              	Matches found (OpenFile): 997413
Matches found (OpenFile): 997413
       2	 581771636 ns/op
PASS
ok  	command-line-arguments	20.706s
```

Which can be summarised as:

| Benchmark	                     | Operations              | Time per Operation (ns)   | Notes                          |
| ---------------------------------- | ----------------------- | ------------------------- | ------------------------------ |
| Standard os.Open                   | 460,371                 | 2531 ns/op                | Baseline for simple file open  |
| Optimized O_DIRECT                 | 469,384                 | 2557 ns/op                | No significant improvement     |
| syscall.Pread (single read)        | 698,469                 | 1551 ns/op                | ~37% faster than os.Open       |
| Whole file (Pread)                 | 2                       | 896 ms (0.89s)            | Reads line by line             |
| Whole file (os.OpenFile)           | 2                       | 618 ms (0.61s)            | ~31% faster than syscall.Pread |
| Whole file + MD5 (Pread)           | 1                       | 1.61s                     | Hash calculation included      |
| Whole file + MD5 (os.OpenFile)     | 1                       | 1.55s                     | ~3% faster than Pread          |

Of particular note: when we added md5 to our functions we even out the benchmarks. The assumption here is that this is due to us now being CPU bound, but lets quickly sanity check that:

```sh
ubuntu@ip-192-168-0-13:~/blog$ go test -bench=BenchmarkPreadReadWholeFileAndHash -bench=BenchmarkOsOpenFileReadWholeFileAndHash -cpuprofile cpu.prof
MD5 (os.OpenFile): e196fdf7806a4385382a8567ece65598
goos: linux
goarch: amd64
pkg: github.com/peter-mcconnell/petermcconnell.com
cpu: Intel(R) Xeon(R) Platinum 8375C CPU @ 2.90GHz
BenchmarkOsOpenFileReadWholeFileAndHash-8   	       1	1542750540 ns/op
PASS
ok  	github.com/peter-mcconnell/petermcconnell.com	1.706s
ubuntu@ip-192-168-0-13:~/blog$ go tool pprof cpu.prof
File: petermcconnell.com.test
Build ID: d4e2c7e92f1c7b79b7572cdf54387115ff451bbc
Type: cpu
Time: 2025-03-04 09:44:06 UTC
Duration: 1.70s, Total samples = 1.55s (90.99%)
Entering interactive mode (type "help" for commands, "o" for options)
(pprof) top
Showing nodes accounting for 1.55s, 100% of 1.55s total
Showing top 10 nodes out of 28
      flat  flat%   sum%        cum   cum%
     1.40s 90.32% 90.32%      1.40s 90.32%  crypto/md5.block
     0.13s  8.39% 98.71%      0.13s  8.39%  internal/runtime/syscall.Syscall6
     0.01s  0.65% 99.35%      0.01s  0.65%  internal/poll.(*fdMutex).rwunlock
     0.01s  0.65%   100%      0.01s  0.65%  runtime.(*mcache).prepareForSweep
         0     0%   100%      1.40s 90.32%  crypto/md5.(*digest).Write
         0     0%   100%      1.55s   100%  github.com/peter-mcconnell/petermcconnell%2ecom.BenchmarkOsOpenFileReadWholeFileAndHash
         0     0%   100%      1.55s   100%  github.com/peter-mcconnell/petermcconnell%2ecom.readFileWithOsOpenFileAndHash
         0     0%   100%      0.15s  9.68%  internal/poll.(*FD).Read
         0     0%   100%      0.01s  0.65%  internal/poll.(*FD).readUnlock
         0     0%   100%      0.14s  9.03%  internal/poll.ignoringEINTRIO (inline)
(pprof)
```

As we can see `crypto/md5.block` accounts for ~90% and the disk is no longer the issue.

Some brief takeaways here are:

- os.OpenFile was slower but benefited from kernel-level read-ahead caching.
- Before MD5: syscall.Pread vs. os.OpenFile Performance was purely Disk-Bound
- After MD5: The Bottleneck Shifted to CPU Hashing

## Conclusion

Opening a file on Linux is far from a trivial operation—it involves user-space checks, syscalls, kernel caching, and filesystem-specific optimizations. By understanding these layers, developers can fine-tune performance, particularly in high-throughput applications. Golang offers flexible file opening mechanisms that, when optimized, can yield significant efficiency gains.

- Use syscall.Pread for performance-sensitive applications where random access or concurrent reads are required (multiple goroutines can read from different parts of the file simultaneously without locking the file descriptor).
- Use os.OpenFile for idiomatic, portable, and sequential file reads where system optimizations help.

For further reading, check out:

- `man 2 open`
- `man 7 vfs`
- Linux kernel source code (fs/open.c)
