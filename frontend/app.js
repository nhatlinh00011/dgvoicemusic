const fileInput = document.getElementById("audioFile");
const fileName = document.getElementById("fileName");
const runBtn = document.getElementById("runBtn");
const statusEl = document.getElementById("status");
const progress = document.querySelector("#progress i");
const results = document.getElementById("results");
const resultList = document.getElementById("resultList");

fileInput.addEventListener("change", () => {
  fileName.textContent = fileInput.files[0]?.name || "MP3, WAV, FLAC, M4A hoặc OGG";
});

function addResult(name, url) {
  const row = document.createElement("div");
  row.className = "result";
  row.innerHTML = `<span>${escapeHtml(name)}</span><a href="${url}" download>Tải xuống</a>`;
  resultList.appendChild(row);
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[c]));
}

async function postFile(url, file) {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(url, {method:"POST", body:fd});
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Xử lý thất bại");
  return data;
}

runBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    alert("Hãy chọn file nhạc trước.");
    return;
  }

  const doSplit = document.getElementById("doSplit").checked;
  const doMidi = document.getElementById("doMidi").checked;

  if (!doSplit && !doMidi) {
    alert("Hãy chọn ít nhất một chức năng.");
    return;
  }

  runBtn.disabled = true;
  results.classList.add("hidden");
  resultList.innerHTML = "";
  progress.style.width = "5%";

  try {
    if (doSplit) {
      statusEl.textContent = "Đang tách Vocal / Drums / Bass / Other...";
      progress.style.width = "35%";
      const data = await postFile("/api/split", file);
      data.files.forEach(x => addResult(x.name, x.url));
    }

    if (doMidi) {
      statusEl.textContent = "Đang phân tích giai điệu và tạo MIDI...";
      progress.style.width = doSplit ? "70%" : "35%";
      const data = await postFile("/api/midi", file);
      data.files.forEach(x => addResult(x.name, x.url));
    }

    progress.style.width = "100%";
    statusEl.textContent = "Hoàn tất!";
    results.classList.remove("hidden");
  } catch (err) {
    statusEl.textContent = "Có lỗi: " + err.message;
    progress.style.width = "0%";
  } finally {
    runBtn.disabled = false;
  }
});
