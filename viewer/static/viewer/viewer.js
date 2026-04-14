let viewer = (function() {
    "use strict"; let self = {};

    self.request_in_process = false;

    /**
     * Activates all event listeners for the Viewer module.
     */
    self.activate_handlers = function() {
        let interactive_next_button = $("#interactive-next");
        if (interactive_next_button.length) {
            if (typeof(interactive_next_button.data("timeout")) !== 'undefined') {
                let timeout = parseInt(interactive_next_button.data("timeout"));
                setTimeout(function() {
                    interactive_next_button.attr("disabled", false);
                }, timeout);
            }//endif
        }
        $(".check-form").off("submit").on("submit", function(e) {
            e.preventDefault();
            if($(this).data("submitted")) {
                return;
            }//endif
            $(".check-form-submit").prop("disabled", true);
            let data = "response=" + $("input[name=responses]:checked").val();
            let target = $(this).data("target");
            let url = $(this).attr("action");
            if(!self.request_in_process) {
                self.request_in_process = true;
                let promise = core.ajax("GET", target, url, false, data);
                promise.then(function() {
                    self.request_in_process = false;
                })
            }//endif
        });
        $(".check-response").off("click").on("click", function(e) {
            let form_id = $(this).data("form-id");
            let id = $(form_id + " input[name=responses]:checked").attr("id");
            let response_form_checked = $(form_id + " .checked");
            let response_form_unchecked = $(form_id + " .unchecked");
            let label_checked = $(form_id + " #" + id + "-label .checked");
            let label_unchecked = $(form_id + " #" + id + "-label .unchecked");
            response_form_checked.addClass("d-none");
            response_form_checked.removeClass("d-flex");
            response_form_unchecked.addClass("d-flex");
            response_form_unchecked.removeClass("d-none");
            label_checked.addClass("d-flex");
            label_checked.removeClass("d-none");
            label_unchecked.addClass("d-none");
            label_unchecked.removeClass("d-flex");
        })
        $(".interactive-load").off("click").on("click", function(e) {
            e.preventDefault();
            let toc_target = $(this).data("toc-target");
            let toc_url = $(this).data("toc-url");
            let toc_prev_target = $(this).data("toc-prev-target");
            let toc_prev_url = $(this).data("toc-prev-url");
            core.ajax("GET", $(this).data("target"), $(this).data("url"), true, "", function() {
                if (toc_url) { core.ajax("GET", toc_target, toc_url, false); }//endif
                if (toc_prev_url) { core.ajax("GET", toc_prev_target, toc_prev_url, false); }//endif
                $(toc_target).get(0).scrollIntoView({behavior: 'smooth'});
            });
        });
        $(".print-btn").off("click").on("click", function (e) {
            e.preventDefault();
            let title = $(this).attr("title");
            let control = $(this).data("control");
            let target = "#" + control + "-generic ." + control + "-container";
            let url = $(this).data("url");
            core.ajax("GET", target, url, true, "", function() {
                $("#" + control + "-generic ." + control + "-title").html(title);
                if (control === "modal") { core.modal.show(); }//endif
            });
        });
    };//end activate_handlers() function

    return self;
}());