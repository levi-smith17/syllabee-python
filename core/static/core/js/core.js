let core = (function() {
    "use strict"; let self = {};

    self.modal = null;
    self.offcanvas = null;
    self.searchInputTimer = null;

    $(window).on("load",(function() { self.initialize(); self.activate_handlers_all(); }));

    /**
     * Initializes all required variables and objects when the page is first loaded.
     */
    self.initialize = function() {
        if ($("#modal-generic").length) { self.modal = new bootstrap.Modal("#modal-generic"); }
        const offcanvas_generic = $("#offcanvas-generic");
        if (offcanvas_generic.length) { self.offcanvas = new bootstrap.Offcanvas("#offcanvas-generic"); }
        if (offcanvas_generic.length) {
            const offcanvas_generic = document.getElementById("offcanvas-generic");
            offcanvas_generic.addEventListener("show.bs.offcanvas", () => {
                $(".offcanvas-generic-backdrop").fadeIn().show();
            });
            offcanvas_generic.addEventListener("hide.bs.offcanvas", () => {
                $(".offcanvas-generic-backdrop").fadeOut().hide();
            });
        }//endif
    };//end initialize() function

    /**
     * Activates all event listeners across the entire web app (including those in other modules).
     */
    self.activate_handlers_all = function() {
        self.activate_handlers();
        if (typeof editor !== "undefined") { editor.activate_handlers(); }//endif
        if (typeof loader !== "undefined") { loader.activate_handlers(); }//endif
        if (typeof viewer !== "undefined") { viewer.activate_handlers(); }//endif
    };//end activate_handlers_all() function

    /**
     * Activates all event listeners for the Core module.
     */
    self.activate_handlers = function() {
        let my_toast = document.getElementById("toast-message");
        if(my_toast) {
            let toast = new bootstrap.Toast(mytoast); toast.show();
            my_toast.addEventListener("hidden.bs.toast", function () {
                $("#toast-message").parent().remove();
            });
        }//endif
        $(".button-load").off("click").on("click", function () {
            self.ajax("GET", $(this).data("target"), $(this).data("url"), true);
        });
        $(".copyright-version").off("click").on("click", function(e) {
            e.preventDefault();
            let title = $(this).attr("title");
            self.ajax("GET", "#offcanvas-generic .offcanvas-container", $(this).data("url"), true, "", function() {
                $("#offcanvas-generic .offcanvas-title").html(title);
                self.offcanvas.show();
            });
        });
        $(".filter-clear").off("click").on("click", function () {
            self.ajax("GET", $(this).data("target"), $(this).data("url"), true, "");
        });
        $(".filter-datalist .datalist").off("input").on("input", function(e) {
            e.preventDefault();
            let value = $(this).val();
            let name = $(this).attr("name").split("_datalist")[0];
            let field = $(this).siblings("label").text();
            let datalist = $(this).siblings("datalist");
            let valid_value = $(datalist).find("option[value='" + value + "']");
            if (valid_value !== null && valid_value.length > 0) {
                $("#no-filters").hide();
                $(".filter-datalist button[type='submit']").attr("disabled", false);
                let html = '<div class="filter badge rounded-pill btn-dark text-bg-dark-header ps-3 d-inline-flex ' +
                    'flex-nowrap align-items-center border border-secondary w-100">' + field + ': ' + value +
                    '<button type="button" class="filter-datalist-clear btn btn-sm btn-dark btn-darker p-0 d-flex ' +
                    'align-items-center ms-auto border-0" title="Clear Filter" data-target="#' + datalist.attr("id") +
                    '" data-value="' + value + '"><svg xmlns="http://www.w3.org/2000/svg" ' +
                    'width="1.5rem" height="1.5rem" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">' +
                    '  <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 ' +
                    '2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 ' +
                    '0-.708"/></svg></button><input type="hidden" name="' + name + '" value="' + value + '"</div>';
                $("#filters-selected").append(html);
                datalist.children("option[value='" + value + "']").remove();
                $(this).val("");
                self.activate_handlers_all();
            }//endif
        });
        $(".filter-datalist-clear").off("click").on("click", function(e) {
            e.preventDefault();
            let value = $(this).data("value");
            let target = $(this).data("target");
            $(target).append('<option value="' + value + '">');
            let datalist = $(target);
            datalist.append(datalist.find("option").remove()
                .sort(function(a, b) {
                    let at = $(a).val(),
                        bt = $(b).val();
                    return (at > bt) ? 1 : ((at < bt) ? -1 : 0);
                }));
            $(this).parent().remove();
            if ($("#filters-selected").children(".filter").length === 0) {
                $("#no-filters").show();
                $(".filter-datalist button[type='submit']").attr("disabled", true);
            }//endif
        });
        $(".filter-form").off("submit").on("submit", function(e) {
            e.preventDefault();
            let formData = new FormData(this);
            let model = $(this).data("model");
            let target = $(this).data("target");
            let url = $(this).attr("action");
            self.ajax("POST", target, url, true, formData, function() {
                self.offcanvas.hide();
                return model + " filtered successfully.";
            });
        });
        $(".filter-offcanvas").off("click").on("click", function (e) {
            e.preventDefault();
            let title = $(this).attr("title");
            let url = $(this).data("url");
            self.ajax("GET", "#offcanvas-generic .offcanvas-container", url, true, "", function() {
                $("#offcanvas-generic .offcanvas-title").html(title);
                self.offcanvas.show();
            });
        });
        $(".form-row").find(":input:not([data-prefix])").each(function() { $(this).prop("required", true); });
        $(".offcanvas-generic-backdrop").off("click").on("click", function(e) {
            e.preventDefault(); self.offcanvas.hide(); $(this).hide();
        });
        $(".scroll-to").off("click").on("click", function(e) {
            e.preventDefault();
            let scroll_to = $(this).data("scroll-to");
            let scroll_offset;
            if (typeof $(this).data("scroll-offset") !== "undefined") {
                scroll_offset = $(this).data("scroll-offset");
            } else {
                scroll_offset = 28;
            }//endif-else
            let container = $("#syllabus-content");
            container.animate({scrollTop: $(scroll_to).offset().top - container.offset().top + container.scrollTop() - scroll_offset }, 1000);
        });
        $(".scroll-top").off("click").on("click", function() {
            if (navigator.userAgent.match(/(iPod|iPhone|iPad|Android)/)) {
                window.scrollTo(0, 0);
            } else {
                if(window.matchMedia("(max-width: 992px)").matches) {
                    $(".syllabus").animate({scrollTop: 0}, 1000);
                } else {
                    $($(this).data("target")).animate({scrollTop: 0}, 1000);
                }//endif-else
            }//endif-else
        });
        let search = $(".search");
        search.off("keyup").on("keyup", function () {
            let pattern = $(this).val();
            let target = $(this).data("target");
            let url = $(this).data("url");
            clearTimeout(self.searchInputTimer);
            self.searchInputTimer = setTimeout(function() {
                self.ajax("GET", target, url, true, "pattern="+pattern);
            }, 500);
        });
        search.off("keydown").on("keydown", function () {
            clearTimeout(self.searchInputTimer);
        });
        $(".search-clear").off("click").on("click", function() {
            $($(this).data("field")).val("");
            $($(this).data("target")).empty();
            $(".btn-pagination").attr("disabled", true);
            let target = $(this).data("target");
            if(target) {
                self.ajax("GET", target, $(this).data("url"), true, "");
            }//endif
        });
        $(".search-toggle").off("click").on("click", function () {
            let module = $(this).data("module");
            let model = $(this).data("model");
            let target = $(this).data("target");
            $("#"+module+"-"+model+"-search").toggle();
            $("#"+module+"-"+model+"-search-button").toggle();
            $("#"+module+"-"+model+"-search-input").val("");
            if(target) {
                self.ajax("GET", $(this).data("target"), $(this).data("url"), true, "pattern=");
            }//endif
        });
    };//end activate_handlers() function

    /**
     * Initiates an AJAX call.
     *
     * @param {string} method - The method used by the AJAX request. Must be either 'GET' or 'POST'.
     * @param {string} target - The target element on the DOM to receive the result of the AJAX request.
     * @param {string} url - The URL used in the AJAX request.
     * @param {boolean} engage_loader - Whether to trigger the main loading indicator for this AJAX request or not.
     * @param {string=} data - Data to be sent to the server as part of the AJAX request (optional).
     * @param {function=} callback - A callback function to execute once the AJAX request has completed successfully
     * (optional).
     *
     * @returns Promise
     */
    self.ajax = function(method, target, url, engage_loader, data, callback) {
        if (engage_loader) { $("#core-loader").show(); }//endif
        if (url) {
            return $.ajax({url: url, type: method, data: data, cache: false, contentType: false, processData: false,
                encode: true, headers: {"accept": "application/json"},})
                .done(function (data, status, jqXHR) {
                    if (target) { $(target).html(data); }//endif
                    if (method === "POST") {
                        if (typeof callback === "function") {
                            self.build_toast(jqXHR, status, callback());
                        }//endif
                    } else {
                        if (typeof callback === "function") { callback(); }//endif
                    }//endif-else
                    if (engage_loader) { $("#core-loader").hide(); }//endif
                    self.activate_handlers_all();
                })
                .fail(function (jqXHR, status, error) {
                    self.build_toast(jqXHR, status, error);
                });//end-ajax
        } else { self.url_error(); }//endif-else
    };//end ajax() function

    /**
     * Builds a toast object for displaying a notification to the user. Once the notification has been cleared, it is
     * reformatted and added to the Recent Notifications area.
     *
     * @param {Object} jqXHR - An object representing the result of an AJAX request.
     * @param {string} status - The status of the AJAX request (determines what type of toast is built).
     * @param {string=} message - The message to be displayed to the user as part of the notification.
     */
    self.build_toast = function(jqXHR, status, message) {
        let toast_element = $("#toast-template").clone();
        let toast_element_header = toast_element.children(".toast-header");
        let toast_element_body = toast_element.children(".toast-body");
        toast_element.appendTo("#toast-container");
        let toast_element_with_id = document.getElementById(toast_element.attr("id"));
        toast_element.removeAttr("id");
        if(status === "info" || status === "success" || status === "warning") {
            toast_element_header.children(".toast-header-text").html(status.toUpperCase());
            toast_element_header.addClass("text-bg-" + status);
            toast_element_body.html(message);
            toast_element_body.addClass("text-bg-" + status);
        } else {
            try {
                let data;
                if (typeof jqXHR.responseText === "string") {
                    data = JSON.parse(jqXHR.responseText);
                } else {
                    data = jqXHR.responseText;
                }//endif-else
                toast_element_header.children(".toast-header-text").html(data.code + " " + data.type);
                toast_element_header.addClass("text-bg-" + data.class);
                toast_element_body.html(data.text.format);
                toast_element_body.addClass("text-bg-" + data.class);
            } catch (e) {
                toast_element.html(jqXHR.responseText);
            }//endtry-catch
        }//endif-else
        let toast = new bootstrap.Toast(toast_element); toast.show(); $("#core-loader").hide();
        toast_element_with_id.addEventListener("hidden.bs.toast", event => {
            $("#notifications .alert").remove();
            toast.dispose();
            event.target.classList.remove("hide");
            event.target.classList.remove("shadow-lg");
            event.target.classList.add("show");
            event.target.classList.add("w-100");
            let elements = event.target.getElementsByClassName("btn");
            while (elements[0]) {
                elements[0].parentNode.removeChild(elements[0]);
            }//end-while
            $("#notifications").prepend(event.target);
        })
    };//end build_toast() function

    /**
     * Displays a standardized error message if there is an issue with a URL.
     */
    self.url_error = function() {
        let error = {"responseText": '{"class": "danger", "code": 400, "text": {"format": ' +
                '"A nontemporal problem occurred connecting to the server. Please click the version button at ' +
                'the bottom of the left-hand navbar to report this issue, and include the following issue ' +
                'code when doing so: <strong>uakari</strong>."}, "type": "Bad Request"}'};
        self.build_toast(error, "danger");
    }//end url_error() function

    return self;
}());