export default function bindUploadEvents(
    uploadImageButton,
    uploadImageSelect,
    uploadCountDiv
) {
    uploadImageButton.addEventListener("click", () => {
        uploadImageSelect.click();
    });
    uploadImageSelect.addEventListener("change", () => {
        const count = uploadImageSelect.files.length;
        uploadCountDiv.innerHTML = `${count} image${
            count > 1 ? "s" : ""
        } uploaded.`;
    });
}
