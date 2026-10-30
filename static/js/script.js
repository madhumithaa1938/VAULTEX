
document.addEventListener("DOMContentLoaded", () => {

    // Get file upload elements

    const input = document.getElementById("file");

    const selected = document.getElementById("selected-file");

    const form = document.querySelector(".upload-panel");


    // Display selected file information

    if (input && selected) {

        input.addEventListener("change", () => {

            const file = input.files && input.files[0];

            if (!file) {

                selected.textContent = "No file selected";

                return;
            }


            // Convert file size into readable format

            const size = file.size < 1048576

                ? `${(file.size / 1024).toFixed(1)} KB`

                : `${(file.size / 1048576).toFixed(2)} MB`;


            selected.textContent = `${file.name} · ${size}`;

        });

    }


    // Handle upload form submission

    if (form) {

        form.addEventListener("submit", (event) => {

            if (!form.checkValidity()) return;

            const button = form.querySelector(
                'button[type="submit"]'
            );

            if (button) {

                button.disabled = true;

                button.textContent = "Encrypting and storing…";

            }

        });

    }


    // Ensure notification messages have status roles

    document.querySelectorAll(".flash").forEach((item) => {

        item.setAttribute("role", "status");

    });

});
