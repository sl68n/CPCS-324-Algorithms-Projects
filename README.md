# CPCS 324 – Algorithms Projects

![Course](https://img.shields.io/badge/Course-CPCS324-orange)  
![Language](https://img.shields.io/badge/Language-Python%20%7C%20Java-blue)  
![Focus](https://img.shields.io/badge/Focus-Greedy%20Algorithms-purple)  
![University](https://img.shields.io/badge/University-KAU-black)  
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

This repository contains two major projects developed for  
CPCS 324 – Algorithms and Data Structures (II)  
King Abdulaziz University  

Both projects focus on Greedy Algorithms, performance analysis, and experimental comparison.

---

# Repository Structure

```
CPCS324-Algorithms-Projects/
│
├── Project1-MST/
│   ├── code.py
│   ├── graph.txt
│   ├── Report.docx
│   └── Presentation.pptx
│
├── Project2-Huffman/
│   ├── HuffmanProject.java
│   ├── file_50KB.txt
│   ├── file_200KB.txt
│   ├── file_1MB.txt
│   ├── results.csv
│   └── report.pdf
│
└── README.md
```

---

# Project 1 – Minimum Spanning Tree  
Prim vs Kruskal Comparison

## Objective

Design a minimum-cost water distribution network using MST.

- Vertices represent water junctions (J1–J6)  
- Edges represent pipelines  
- Weights represent construction cost  
- Goal: Connect all junctions with minimum total cost  

---

## Implemented Algorithms

### Prim’s Algorithm (Min-Heap)

Time Complexity: O(E log V)  
Tree-growing approach  
Uses a priority queue (heap) for efficient edge selection  

---

### Kruskal’s Algorithm (Union-Find)

Time Complexity: O(E log E)  
Forest-growing approach  
Uses sorting and Union-Find for cycle detection  

---

## Requirement 1 – Provided Graph

Input graph:
- 6 vertices  
- 15 edges  

Result:

Total MST Weight = 29  

Both algorithms produced identical results, confirming correctness.

---

## Requirement 2 – Experimental Comparison

Random connected graphs were generated up to:

- n = 10,000 vertices  
- m = 25,000 edges  

Performance observations:

- Prim was faster on dense graphs  
- Kruskal was faster on very sparse graphs  

This matches theoretical expectations:

Prim → O(E log V)  
Kruskal → O(E log E)  

---

# Project 2 – Huffman Coding vs Fixed-Length Encoding

## Objective

Compare compression efficiency and runtime performance between:

- Fixed-Length Encoding (8-bit)  
- Huffman Coding (Greedy Compression Algorithm)  

---

## Fixed-Length Encoding

Each character is represented using 8 bits.  
Compression Ratio = 1.0  
No compression is achieved.

Time Complexity:
- Encoding: O(N)  
- Decoding: O(N)  

---

## Huffman Coding

Steps:

1. Count character frequencies  
2. Insert characters into a Min-Heap  
3. Build a prefix-free binary tree  
4. Generate optimal variable-length codes  

Time Complexity:
- Tree Construction: O(n log n)  
- Encoding: O(N)  
- Decoding: O(N)  

---

## Dataset

Random uppercase text files:

- 50 KB  
- 200 KB  
- 1 MB  

---

## Results Summary

Compression Ratio for Huffman:

≈ 0.59  
≈ 40% size reduction  

Example (1MB file):

Original: 1,048,576 Bytes  
Compressed (Huffman): 624,935 Bytes  

---

# Key Concepts Applied

- Greedy Algorithms  
- Graph Theory  
- Minimum Spanning Trees  
- Heaps (Priority Queue)  
- Union-Find (Disjoint Set)  
- File Compression  
- Time Complexity Analysis  
- Experimental Benchmarking  

---

# Author

Sultan Yasir Alasami  
Computer Science Student  
King Abdulaziz University  

---

# Course Information

CPCS 324 – Algorithms and Data Structures (II)  
Department of Computer Science  
King Abdulaziz University
