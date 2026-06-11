(function () {
    "use strict";

    function ensureMainTarget() {
        if (document.getElementById("main-content")) return;

        const main = document.querySelector(
            "body.tool-page > .container, body.tool-page > .tool-container, body.tool-page > .main-wrapper, body.tool-page > .toolbar"
        );
        if (main) {
            main.id = "main-content";
            main.setAttribute("tabindex", "-1");
        }
    }

    function setupCurrentYear() {
        document.querySelectorAll("[data-current-year]").forEach((node) => {
            node.textContent = String(new Date().getFullYear());
        });
    }

    function setupDropZones() {
        const selector = [
            ".upload-area",
            ".upload-section",
            ".drop-zone",
            ".file-upload",
            ".upload-zone",
            ".drag-drop-area"
        ].join(",");

        document.querySelectorAll(selector).forEach((zone) => {
            zone.addEventListener("dragover", () => zone.classList.add("is-dragover"));
            zone.addEventListener("dragleave", (event) => {
                if (!zone.contains(event.relatedTarget)) {
                    zone.classList.remove("is-dragover");
                }
            });
            zone.addEventListener("drop", () => zone.classList.remove("is-dragover"));
        });
    }

    function getToastRegion() {
        let region = document.querySelector(".toast-region");
        if (!region) {
            region = document.createElement("div");
            region.className = "toast-region";
            region.setAttribute("role", "status");
            region.setAttribute("aria-live", "polite");
            region.setAttribute("aria-atomic", "true");
            document.body.appendChild(region);
        }
        return region;
    }

    function showToast(message) {
        const region = getToastRegion();
        const toast = document.createElement("div");
        toast.className = "site-toast";
        toast.textContent = String(message);
        region.appendChild(toast);

        window.setTimeout(() => {
            toast.remove();
        }, 4200);
    }

    window.alert = showToast;

    document.addEventListener("DOMContentLoaded", () => {
        ensureMainTarget();
        setupCurrentYear();
        setupDropZones();
    });
})();
