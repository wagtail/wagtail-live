import fetchHelper from "./fetch_helper";
import showNotif from "./show_notif";
import bindUploadEvents from "./bind_upload_events";

function createLivePostDiv(content) {
    const livePostDiv = document.createElement("li");
    livePostDiv.classList.add("list-group-item", "mb-5", "p-0");
    livePostDiv.style.border = "none";
    livePostDiv.innerHTML = content;
    return livePostDiv;
}

export class LivePost {
    constructor(post, channelName, wrapper) {
        this.post = post;
        this.channelName = channelName;
        this.wrapper = wrapper;
        this.pk = this.post.dataset.id;
        if (this.pk === undefined) {
            this.pk = this.post.firstElementChild.dataset.id;
        }
        this.editButton = this.post.querySelector(".show-edit-form");
        this.deleteButton = this.post.querySelector(".delete-message");
    }

    bindEvents() {
        this.editButton.addEventListener("click", this.showEditForm.bind(this));
        this.deleteButton.addEventListener("click", this.delete.bind(this));
        this.fullyBound = false;
    }

    _bind() {
        if (this.fullyBound) {
            return;
        }

        this.content = this.post.querySelector(".message-body");

        this.editForm = this.post.querySelector(".edit-form");
        this.editForm.addEventListener("submit", this.edit.bind(this));

        this.cancelEditButton = this.post.querySelector(".cancel-edit");
        this.cancelEditButton.addEventListener(
            "click",
            this.cancelEdit.bind(this)
        );

        this.uploadImageButton = this.post.querySelector(".upload-btn");
        this.uploadImageSelect = this.post.querySelector(".upload-file");
        this.uploadCountDiv = this.post.querySelector(".upload-count");
        bindUploadEvents(
            this.uploadImageButton,
            this.uploadImageSelect,
            this.uploadCountDiv
        );

        this.deleteImageButtons = this.post.querySelectorAll(".delete-image");
        this.deleteImageButtons.forEach((btn) => {
            btn.addEventListener("click", this.deleteImage.bind(this));
        });

        this.fullyBound = true;
    }

    showEditForm() {
        this._bind();

        // Hide edit button.
        this.editButton.style.display = "none";

        // Hide post content.
        this.content.style.display = "none";

        // Show edit form.
        this.editForm.style.display = "";
    }

    replace(newContent) {
        const livePostDiv = createLivePostDiv(newContent);
        this.wrapper.replaceChild(livePostDiv, this.post);

        this.post = livePostDiv;
        this.deleteButton = this.post.querySelector(".delete-message");
        this.editButton = this.post.querySelector(".show-edit-form");
        this.bindEvents();
    }

    cancelEdit() {
        this.editForm.style.display = "none";
        this.content.style.display = "";
        this.editButton.style.display = "";
    }

    async edit(event) {
        event.preventDefault();
        const formdata = new FormData(this.editForm);
        formdata.append("channel", this.channelName);

        try {
            let result = await fetchHelper(
                `messages/${this.pk}/`,
                "PUT",
                formdata,
                200,
                false
            );
            if (!result.ok) {
                return;
            }

            showNotif(`Message ${this.pk} edited.`);
            const newContent = await result.response.text();
            this.replace(newContent);
        } catch (error) {
            showNotif(error, 0);
        }
    }

    async delete() {
        try {
            const result = await fetchHelper(
                `messages/${this.pk}/`,
                "DELETE",
                {},
                204
            );
            if (!result.ok) {
                return;
            }

            this.post.remove();
            showNotif(`Message ${this.pk} deleted.`);
        } catch (error) {
            showNotif(error, 0);
        }
    }

    getImage(imageID) {
        return this.post.querySelector(`li[data-id='${imageID}']`);
    }

    async deleteImage(event) {
        event.preventDefault();

        const pk = event.currentTarget.dataset.id;
        try {
            const result = await fetchHelper(
                `images/${pk}/`,
                "DELETE",
                {},
                204
            );
            if (!result.ok) {
                return;
            }

            const image = this.getImage(pk);
            if (image) {
                image.remove();
            }
            showNotif(`Image ${pk} deleted.`);
        } catch (error) {
            showNotif(error, 0);
        }
    }
}

export async function createLivePost(event, channelName, livePostsWrapper) {
    // Prevent default form submission
    event.preventDefault();

    const form = event.target;
    const formdata = new FormData(form);
    formdata.append("channel", channelName);

    // Send a POST request to save channel
    try {
        let result = await fetchHelper(
            "messages/",
            "POST",
            formdata,
            201,
            false
        );
        if (!result.ok) {
            return;
        }

        // Clear out composition fields
        document.querySelector("#content").value = "";
        document.querySelector("#images").value = "";
        document.querySelector("#imagesList").innerHTML = "";

        showNotif("Message posted.");

        const content = await result.response.text();
        const livePostDiv = createLivePostDiv(content);
        livePostsWrapper.prepend(livePostDiv);
        const handler = new LivePost(
            livePostDiv,
            channelName,
            livePostsWrapper
        );
        handler.bindEvents();
    } catch (error) {
        showNotif(error, 0);
    }
}
