import { useState } from "react";
import "./App.css";

function App() {
  const [sizeBeforeCompression, setSizeBeforeCompression] = useState("");
  const [sizeAfterCompression, setSizeAfterCompression] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const resetMessages = () => {
    setError("");
    setSuccess("");
    setSizeBeforeCompression("");
    setSizeAfterCompression("");
  };

  async function upload(fileList) {
    if (!fileList || fileList.length === 0) {
      setError("Please select a file to upload");
      return;
    }

    const selectedFile = fileList[0];

    // Validation
    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setError("Please select a PDF file");
      return;
    }

    if (selectedFile.size > 50 * 1024 * 1024) {
      setError("File size must be less than 50MB");
      return;
    }

    resetMessages();
    setIsLoading(true);

    try {
      const quality = document.getElementById("quality").value;
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("quality", quality);

      // Relative URL for API calling
      const response = await fetch("/compress", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.status}`);
      }

      // Get file size information from headers
      const originalSize = response.headers.get("X-File-Size-MB");
      const compressedSize = response.headers.get("X-File-Size-Compressed-MB");

      setSizeBeforeCompression(originalSize || "Unknown");
      setSizeAfterCompression(compressedSize || "Unknown");

      // Download the compressed file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const downloadLink = document.createElement("a");
      downloadLink.href = url;
      downloadLink.download = selectedFile.name.replace(
        ".pdf",
        "_compressed.pdf",
      );
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      window.URL.revokeObjectURL(url);

      setSuccess("File compressed and downloaded successfully!");

      // Clean up files on server
      fetch("/removeFiles", { method: "GET" }).catch(console.error);
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.message || "Failed to compress file. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div>
      <h1>Compress PDF</h1>

      <div style={{ marginBottom: "20px" }}>
        <label htmlFor="quality">Quality Level:</label>
        <select id="quality" style={{ marginLeft: "10px", padding: "5px" }}>
          <option value="screen">Low (Smallest file)</option>
          <option value="ebook">Medium</option>
          <option value="printer">High</option>
          <option value="prepress">Very High (Largest file)</option>
        </select>
      </div>

      <div style={{ marginBottom: "20px" }}>
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => upload([...e.target.files])}
          disabled={isLoading}
          style={{
            padding: "10px",
            fontSize: "16px",
            border: "2px dashed #646cff",
            borderRadius: "8px",
            backgroundColor: "#1a1a1a",
          }}
        />
      </div>

      <p style={{ color: "#ffa500", fontSize: "14px" }}>
        Only PDF files accepted • Max size: 50MB • File will download
        automatically
      </p>

      {error && (
        <div
          style={{
            color: "#ff6b6b",
            backgroundColor: "#2d1b20",
            padding: "10px",
            borderRadius: "5px",
            margin: "10px 0",
          }}
        >
          Error: {error}
        </div>
      )}

      {success && (
        <div
          style={{
            color: "#4ecdc4",
            backgroundColor: "#1b2d2a",
            padding: "10px",
            borderRadius: "5px",
            margin: "10px 0",
          }}
        >
          {success}
        </div>
      )}

      {(sizeBeforeCompression || sizeAfterCompression) && (
        <div
          style={{
            backgroundColor: "#2a2a2a",
            padding: "15px",
            borderRadius: "8px",
            margin: "20px 0",
          }}
        >
          <p>
            <strong>Compression Results:</strong>
          </p>
          <p>Original size: {sizeBeforeCompression}</p>
          <p>Compressed size: {sizeAfterCompression}</p>
        </div>
      )}

      {isLoading && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(0,0,0,0.7)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
        >
          <div style={{ textAlign: "center", color: "white" }}>
            <div className="loader"></div>
            <p style={{ marginTop: "20px" }}>Compressing PDF...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
