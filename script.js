
document.getElementById('upload-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const log = document.getElementById('log');
    log.textContent = "⏳ Uploaden en verwerken...";

    const imageInput = document.getElementById('image');
    const colors = document.querySelector('input[name="colors"]:checked')?.value;
    const formData = new FormData();
    formData.append('image', imageInput.files[0]);
    formData.append('colors', colors);

    try {
        const response = await fetch("/process-numbers", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        if (data.error) {
            log.textContent = "❌ " + data.error;
            return;
        }

        // Gebruik directe pad naar afbeelding
        document.getElementById("canvas-preview").src = data.download_canvas.startsWith("/") ? data.download_canvas : "/static/" + data.download_canvas;
        document.getElementById("painted-preview").src = data.download_painted.startsWith("/") ? data.download_painted : "/static/" + data.download_painted;

        document.getElementById("download-canvas").href = data.download_canvas.startsWith("/") ? data.download_canvas : "/static/" + data.download_canvas;
        document.getElementById("download-painted").href = data.download_painted.startsWith("/") ? data.download_painted : "/static/" + data.download_painted;

        document.getElementById("download-canvas").style.display = "inline-block";
        document.getElementById("download-painted").style.display = "inline-block";

        log.textContent = "✅ Voorbeeld klaar!";
    } catch (error) {
        log.textContent = "❌ Fout: " + error.message;
    }
});
