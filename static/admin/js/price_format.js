document.addEventListener("DOMContentLoaded", function () {
  const input = document.querySelector("#id_price");
  if (!input) return;

  // Force input type to text to allow selection and formatting
  input.setAttribute("type", "text");

  // Strip commas before form submission
  input.form.addEventListener("submit", function () {
    input.value = input.value.replace(/,/g, "");
  });

  input.addEventListener("input", function () {
    const raw = input.value.replace(/,/g, "");

    // Allow only numbers and optional decimal part
    if (!/^(\d*)(\.\d{0,2})?$/.test(raw)) return;

    const parts = raw.split(".");
    let intPart = parts[0];
    let decPart = parts[1] || "";

    // Format integer part
    intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");

    // Set formatted value
    input.value = decPart.length > 0 ? `${intPart}.${decPart}` : intPart;

    // Cursor reset isn't necessary with type="text"
  });
});
