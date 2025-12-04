// frontend/script.js
const API_BASE = "http://localhost:8000"; // backend url when running locally

document.getElementById("btn").addEventListener("click", async () => {
  const text = document.getElementById("msg").value;
  const status = document.getElementById("status");
  const preview = document.getElementById("preview");
  status.textContent = "Generating... this may take a few seconds.";
  preview.src = "";

  try {
    const res = await fetch(`${API_BASE}/generate`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ text })
    });
    if (!res.ok) {
      const err = await res.json();
      status.textContent = "Error: " + (err.detail || res.statusText);
      return;
    }
    const data = await res.json();
    const videoUrl = API_BASE + data.file_url;
    // small delay to let backend finalize file
    setTimeout(() => {
      preview.src = videoUrl;
      preview.load();
      status.textContent = "Done — preview below. Video will be deleted from server shortly.";
    }, 2000);
  } catch (err) {
    status.textContent = "Network error: " + err.message;
  }
});
