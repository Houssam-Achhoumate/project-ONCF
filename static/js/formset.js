document.addEventListener("DOMContentLoaded", () => {
    const formsContainer = document.querySelector("#article-forms");
    const addButton = document.querySelector("#add-line");
    const emptyTemplate = document.querySelector("#empty-form-template");
    const totalForms = document.querySelector("#id_lignes-TOTAL_FORMS");

    if (!formsContainer || !addButton || !emptyTemplate || !totalForms) return;

    addButton.addEventListener("click", () => {
        const index = Number.parseInt(totalForms.value, 10);
        const html = emptyTemplate.innerHTML.replaceAll("__prefix__", index);
        formsContainer.insertAdjacentHTML("beforeend", html);
        totalForms.value = index + 1;

        const newRow = formsContainer.lastElementChild;
        newRow?.querySelector("input:not([type='hidden'])")?.focus();
    });

    formsContainer.addEventListener("click", (event) => {
        const removeButton = event.target.closest(".remove-line");
        if (!removeButton) return;

        const row = removeButton.closest(".article-form");
        const deleteInput = row?.querySelector("input[name$='-DELETE']");
        if (deleteInput) deleteInput.checked = true;
        row?.classList.add("d-none");
    });
});
