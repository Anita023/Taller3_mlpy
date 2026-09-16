// ==========================================
// 1. REFERENCIAS A ELEMENTOS COMUNES
// ==========================================
const loader = document.getElementById("loader");
const imgResult = document.getElementById("imgResult");
const metricsZone = document.getElementById("metricsZone");
const faceCount = document.getElementById("faceCount");
const statusIndicator = document.getElementById("statusIndicator");
const statusText = document.getElementById("statusText");

// ==========================================
// 2. REFERENCIAS MODO ARCHIVO (UPLOAD)
// ==========================================
const sectionUpload = document.getElementById("sectionUpload");
const btnModeUpload = document.getElementById("btnModeUpload");
const fileInput = document.getElementById("fileInput");
const dropZone = document.getElementById("dropZone");
const btnProcess = document.getElementById("btnProcess");
const imgOriginal = document.getElementById("imgOriginal");
const boxOriginal = document.getElementById("boxOriginal");

// ==========================================
// 3. REFERENCIAS MODO CÁMARA (WEBCAM)
// ==========================================
const sectionCamera = document.getElementById("sectionCamera");
const btnModeCamera = document.getElementById("btnModeCamera");
const video = document.getElementById("webcam");
const canvas = document.getElementById("canvasFrame");
const btnStartCamera = document.getElementById("btnStartCamera");
const btnStopCamera = document.getElementById("btnStopCamera");
const btnToggleCamera = document.getElementById("btnToggleCamera");

// ==========================================
// 4. VARIABLES DE ESTADO
// ==========================================
let selectedFile = null;
let streamInstance = null;
let streamInterval = null;
let isStreaming = false;
let currentFacingMode = "user"; // "user" = frontal | "environment" = trasera

// ==========================================
// 5. CONTROL DE INTERFAZ (CONMUTACIÓN DE MODOS)
// ==========================================
btnModeUpload.addEventListener("click", () => switchMode("upload"));
btnModeCamera.addEventListener("click", () => switchMode("camera"));

function switchMode(mode) {
  if (mode === "upload") {
    btnModeUpload.classList.add("is-active");
    btnModeUpload.setAttribute("aria-selected", "true");
    btnModeCamera.classList.remove("is-active");
    btnModeCamera.setAttribute("aria-selected", "false");

    sectionUpload.classList.remove("hidden");
    sectionCamera.classList.add("hidden");
    boxOriginal.classList.remove("hidden");

    stopCameraFlow();
    setStatus("idle", "Listo");
  } else {
    btnModeCamera.classList.add("is-active");
    btnModeCamera.setAttribute("aria-selected", "true");
    btnModeUpload.classList.remove("is-active");
    btnModeUpload.setAttribute("aria-selected", "false");

    sectionCamera.classList.remove("hidden");
    sectionUpload.classList.add("hidden");
    boxOriginal.classList.add("hidden"); // Centramos el resultado al ocultar el origen

    imgResult.classList.add("hidden");
    metricsZone.classList.add("hidden");
    setStatus("idle", "Cámara apagada");
  }
}

function setStatus(state, text) {
  statusIndicator.classList.remove("is-live", "is-busy");
  if (state === "live") statusIndicator.classList.add("is-live");
  if (state === "busy") statusIndicator.classList.add("is-busy");
  statusText.textContent = text;
}

// ==========================================
// 6. LÓGICA MODO ARCHIVO (DRAG & DROP)
// ==========================================
["dragenter", "dragover"].forEach((name) => {
  dropZone.addEventListener(name, (e) => {
    e.preventDefault();
    dropZone.classList.add("is-dragover");
  });
});

["dragleave", "drop"].forEach((name) => {
  dropZone.addEventListener(name, (e) => {
    e.preventDefault();
    dropZone.classList.remove("is-dragover");
  });
});

dropZone.addEventListener("drop", (e) => {
  handleFile(e.dataTransfer.files[0]);
});

fileInput.addEventListener("change", (e) => {
  handleFile(e.target.files[0]);
});

function handleFile(file) {
  if (file && file.type.startsWith("image/")) {
    selectedFile = file;
    btnProcess.disabled = false;

    const reader = new FileReader();
    reader.onload = (e) => {
      imgOriginal.src = e.target.result;
      imgOriginal.classList.remove("hidden");
      imgResult.classList.add("hidden");
      metricsZone.classList.add("hidden");
    };
    reader.readAsDataURL(file);
  }
}

btnProcess.addEventListener("click", async () => {
  if (!selectedFile) return;
  const formData = new FormData();
  formData.append("image", selectedFile);

  loader.classList.remove("hidden");
  imgResult.classList.add("hidden");
  setStatus("busy", "Procesando...");

  await sendFrameToBackend(formData);
  loader.classList.add("hidden");
  setStatus("idle", "Listo");
});

// ==========================================
// 7. LÓGICA MODO CÁMARA (FLUJO EN TIEMPO REAL)
// ==========================================
btnStartCamera.addEventListener("click", async () => {
  await initCamera();
  btnStartCamera.disabled = true;
  btnStopCamera.disabled = false;
  btnToggleCamera.style.display = "inline-block";
});

btnToggleCamera.addEventListener("click", async () => {
  currentFacingMode = currentFacingMode === "user" ? "environment" : "user";

  if (isStreaming) {
    clearInterval(streamInterval);
    if (streamInstance) {
      streamInstance.getTracks().forEach((track) => track.stop());
    }
    await initCamera();
  }
});

async function initCamera() {
  try {
    streamInstance = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 400 },
        height: { ideal: 300 },
        facingMode: currentFacingMode,
      },
      audio: false,
    });

    video.srcObject = streamInstance;
    isStreaming = true;
    imgResult.classList.remove("hidden");
    sectionCamera.classList.add("is-streaming");
    setStatus("live", "En vivo");

    // Iniciar el intervalo de procesamiento (Cada 600ms)
    streamInterval = setInterval(processCameraFrame, 600);
  } catch (err) {
    console.error("Error al acceder a la cámara:", err);
    alert("No se pudo acceder a la cámara seleccionada.");
    currentFacingMode = currentFacingMode === "user" ? "environment" : "user";
    setStatus("idle", "Error de cámara");
  }
}

btnStopCamera.addEventListener("click", stopCameraFlow);

function stopCameraFlow() {
  clearInterval(streamInterval);
  isStreaming = false;

  if (streamInstance) {
    streamInstance.getTracks().forEach((track) => track.stop());
  }

  video.srcObject = null;
  btnStartCamera.disabled = false;
  btnStopCamera.disabled = true;
  btnToggleCamera.style.display = "none";
  loader.classList.add("hidden");
  sectionCamera.classList.remove("is-streaming");
}

async function processCameraFrame() {
  if (!isStreaming) return;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(
    async (blob) => {
      if (!blob) return;

      const formData = new FormData();
      formData.append("image", blob, "frame.jpg");

      await sendFrameToBackend(formData);
    },
    "image/jpeg",
    0.7,
  );
}

async function sendFrameToBackend(formData) {
  try {
    const response = await fetch("/api/detect", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(`Error ${response.status} del servidor:`, errorData.error || response.statusText);
      return;
    }

    const data = await response.json();

    if (data.success) {
      imgResult.src = data.image;
      imgResult.classList.remove("hidden");
      metricsZone.classList.remove("hidden");
      faceCount.textContent = data.faces_detected;
    }
  } catch (error) {
    console.error("Error en la conexión con la API:", error);
  }
}