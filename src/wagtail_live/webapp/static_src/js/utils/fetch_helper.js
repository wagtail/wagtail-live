import showNotif from "./show_notif";

export default async function fetchHelper(
    path,
    method,
    body,
    expectedStatus = 200,
    jsonContentType = true
) {
    const csrfToken = document.querySelector(
        "[name=csrfmiddlewaretoken]"
    ).value;
    if (!csrfToken) {
        throw new Error("No CSRF Token found.");
    }
    const headers = { "X-CSRFToken": csrfToken };
    if (jsonContentType) {
        headers["Content-Type"] = "application/json";
    }

    const fullPath = `/webapp/api/${path}`;
    const response = await fetch(fullPath, {
        method,
        headers: headers,
        body,
    });

    if (response.status != expectedStatus) {
        // Display corresponding error message
        const errorMsg = await response.json();
        showNotif(Object.values(errorMsg)[0], 0);
        return { ok: false };
    }

    return { ok: true, response: response };
}
