import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

/**
 * CPCS 324 Group Project Part II
 * Huffman Coding vs Fixed-Length Encoding
 */
public class HuffmanProject {

    // --- INNER CLASSES FOR DATA STRUCTURES ---

    // Node for Huffman Tree
    static class HuffmanNode implements Comparable<HuffmanNode> {
        char character;
        int frequency;
        HuffmanNode left;
        HuffmanNode right;

        public HuffmanNode(char character, int frequency) {
            this.character = character;
            this.frequency = frequency;
        }

        public HuffmanNode(int frequency, HuffmanNode left, HuffmanNode right) {
            this.frequency = frequency;
            this.left = left;
            this.right = right;
        }

        // Compare nodes based on frequency for the Priority Queue
        @Override
        public int compareTo(HuffmanNode other) {
            return this.frequency - other.frequency;
        }
    }

    // Class to hold experiment results
    static class ExperimentResult {
        String fileName;
        String method;
        long originalSizeBytes;
        long compressedSizeBytes;
        double compressionRatio;
        long encodeTimeNs;
        long decodeTimeNs;

        public ExperimentResult(String fileName, String method, long original, long compressed, long encTime, long decTime) {
            this.fileName = fileName;
            this.method = method;
            this.originalSizeBytes = original;
            this.compressedSizeBytes = compressed;
            this.compressionRatio = (double) compressed / original; // Compressed / Original
            this.encodeTimeNs = encTime;
            this.decodeTimeNs = decTime;
        }
        
        public String toCSV() {
             return String.format("%s,%s,%d,%d,%.4f,%.2f,%.2f",
                     fileName, method, originalSizeBytes, compressedSizeBytes, compressionRatio, encodeTimeNs/1_000_000.0, decodeTimeNs/1_000_000.0);
        }
    }

    // --- FILE GENERATOR ---

    public static void generateRandomFile(String filename, int sizeInBytes) throws IOException {
        String characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        Random random = new Random();
        StringBuilder sb = new StringBuilder(sizeInBytes);
        
        for (int i = 0; i < sizeInBytes; i++) {
            int index = random.nextInt(characters.length());
            sb.append(characters.charAt(index));
        }
        
        try (FileWriter writer = new FileWriter(filename)) {
            writer.write(sb.toString());
        }
    }

    // --- ALGORITHMS ---

    // 1. Fixed Length Encoding (Baseline)
    public static ExperimentResult runFixedLength(String fileName, String content) {
        long startTime, endTime;

        // -- Encoding --
        startTime = System.nanoTime();
        
        // Simulation: Every char is 8 bits.
        // We build the bit string to prove we can, but for size we know it is len * 8
        StringBuilder encodedBits = new StringBuilder();
        for (char c : content.toCharArray()) {
            String binary = String.format("%8s", Integer.toBinaryString(c)).replace(' ', '0');
            encodedBits.append(binary);
        }
        
        endTime = System.nanoTime();
        long encodeTime = endTime - startTime;
        
        // Calculate size in Bytes (bits / 8)
        long compressedSize = encodedBits.length() / 8; 

        // -- Decoding --
        startTime = System.nanoTime();
        
        StringBuilder decodedText = new StringBuilder();
        for (int i = 0; i < encodedBits.length(); i += 8) {
            String byteStr = encodedBits.substring(i, i + 8);
            int charCode = Integer.parseInt(byteStr, 2);
            decodedText.append((char) charCode);
        }
        
        endTime = System.nanoTime();
        long decodeTime = endTime - startTime;

        // Verify correctness
        if (!decodedText.toString().equals(content)) {
            System.err.println("Error: Fixed-Length Decoding failed for " + fileName);
        }

        return new ExperimentResult(fileName, "Fixed-Length", content.length(), compressedSize, encodeTime, decodeTime);
    }

    // 2. Huffman Coding
    public static ExperimentResult runHuffman(String fileName, String content) {
        long startTime, endTime;

        // -- Encoding Phase --
        startTime = System.nanoTime();

        // Step A: Calculate Frequencies
        Map<Character, Integer> freqMap = new HashMap<>();
        for (char c : content.toCharArray()) {
            freqMap.put(c, freqMap.getOrDefault(c, 0) + 1);
        }

        // Step B: Priority Queue
        PriorityQueue<HuffmanNode> pq = new PriorityQueue<>();
        for (Map.Entry<Character, Integer> entry : freqMap.entrySet()) {
            pq.add(new HuffmanNode(entry.getKey(), entry.getValue()));
        }

        // Step C: Build Huffman Tree
        // Handle edge case: only 1 distinct character
        if (pq.size() == 1) {
            HuffmanNode node = pq.poll();
            pq.add(new HuffmanNode(node.frequency, node, null)); 
        }

        while (pq.size() > 1) {
            HuffmanNode left = pq.poll();
            HuffmanNode right = pq.poll();
            HuffmanNode parent = new HuffmanNode(left.frequency + right.frequency, left, right);
            pq.add(parent);
        }
        HuffmanNode root = pq.peek();

        // Step D: Generate Codes
        Map<Character, String> huffmanCodes = new HashMap<>();
        generateCodes(root, "", huffmanCodes);
        
        // (Optional) Print Table for Small File demo
        if (fileName.contains("50KB")) {
             System.out.println("\n--- Huffman Codes for " + fileName + " (Partial Sample) ---");
             int count = 0;
             for(Map.Entry<Character, String> e : huffmanCodes.entrySet()){
                 if(count++ < 5) System.out.println("'" + e.getKey() + "' : " + e.getValue());
             }
             System.out.println("...");
        }

        // Generate Bitstream
        StringBuilder encodedBits = new StringBuilder();
        for (char c : content.toCharArray()) {
            encodedBits.append(huffmanCodes.get(c));
        }

        endTime = System.nanoTime();
        long encodeTime = endTime - startTime;

        // Calculate size in Bytes (rounding up to nearest byte)
        long compressedSize = (long) Math.ceil(encodedBits.length() / 8.0);

        // -- Decoding Phase --
        startTime = System.nanoTime();
        
        StringBuilder decodedText = new StringBuilder();
        HuffmanNode current = root;
        for (int i = 0; i < encodedBits.length(); i++) {
            char bit = encodedBits.charAt(i);
            if (bit == '0') {
                current = current.left;
            } else {
                current = current.right;
            }

            // Leaf node reached
            if (current.left == null && current.right == null) {
                decodedText.append(current.character);
                current = root; // Reset to root for next char
            }
        }
        
        endTime = System.nanoTime();
        long decodeTime = endTime - startTime;

        // Verify correctness
        if (!decodedText.toString().equals(content)) {
            System.err.println("Error: Huffman Decoding failed for " + fileName);
        }

        return new ExperimentResult(fileName, "Huffman", content.length(), compressedSize, encodeTime, decodeTime);
    }

    private static void generateCodes(HuffmanNode node, String code, Map<Character, String> huffmanCodes) {
        if (node == null) return;

        // Leaf node
        if (node.left == null && node.right == null) {
            huffmanCodes.put(node.character, code.length() > 0 ? code : "0");
            return;
        }

        generateCodes(node.left, code + "0", huffmanCodes);
        generateCodes(node.right, code + "1", huffmanCodes);
    }

    // --- MAIN EXECUTION ---

    public static void main(String[] args) {
        try {
            // 1. Data Preparation
            System.out.println("Generating files...");
            String[] fileNames = {"file_50KB.txt", "file_200KB.txt", "file_1MB.txt"};
            int[] sizes = {50 * 1024, 200 * 1024, 1024 * 1024}; // 50KB, 200KB, 1MB

            for (int i = 0; i < fileNames.length; i++) {
                generateRandomFile(fileNames[i], sizes[i]);
                System.out.println("Generated " + fileNames[i]);
            }

            // 2. Run Experiments
            List<ExperimentResult> results = new ArrayList<>();

            System.out.println("\nRunning experiments...");
            for (String fileName : fileNames) {
                String content = Files.readString(Path.of(fileName));
                
                // Run Huffman
                results.add(runHuffman(fileName, content));
                
                // Run Fixed-Length
                results.add(runFixedLength(fileName, content));
                
                System.out.println("Finished " + fileName);
            }

            // 3. Display Results
            System.out.println("\n--- EXPERIMENTAL RESULTS ---");
            System.out.println("File Name,Method,Original Size (B),Compressed Size (B),Ratio,Encode Time (ms),Decode Time (ms)");
            for (ExperimentResult r : results) {
                System.out.println(r.toCSV());
            }
            
            // Save results to CSV for plotting
            try (FileWriter csvWriter = new FileWriter("results.csv")) {
                csvWriter.write("FileName,Method,OriginalSize,CompressedSize,CompressionRatio,EncodeTime,DecodeTime\n");
                for (ExperimentResult r : results) {
                    csvWriter.write(r.toCSV() + "\n");
                }
            }
            System.out.println("\nResults saved to 'results.csv'. Use the Python script to plot.");

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}