document.getElementById("query-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const queryInput = document.getElementById("query-input");
  const responseOutput = document.getElementById("response-output");
  const loader = document.getElementById("loader");
  const submitButton = document.querySelector("button[type='submit']");

  const query = queryInput.value.trim();

  if (!query) {
    alert("Please enter a query.");
    return;
  }

  // Disable the submit button
  submitButton.disabled = true;

  // Show the loader
  loader.style.display = "inline-block";

  const response = await fetch(`/query?query=${encodeURIComponent(query)}`);
  const data = await response.json();

  // Hide the loader
  loader.style.display = "none";

  // Enable the submit button
  submitButton.disabled = false;

  responseOutput.textContent = data.queryResult;
});
