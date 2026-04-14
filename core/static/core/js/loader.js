let loader = (function() {
    "use strict"; let self = {};

    self.progress_width = 0;
    self.progress_increment = 0;
    self.region_timeouts = [];

    window.onpopstate = function() { location.reload(); }
    $(window).on("load",(function() { self.initialize(); }));

    /**
     * Initializes all required variables and objects when the page is first loaded.
     */
    self.initialize = function() {
        self.initialize_regions("#main-grid");
    };//end initialize() function

    /**
     * Activates all event listeners for the Core module.
     */
    self.activate_handlers = function() {
        $(".load-regions").off("click").on("click", function(e) {
            e.preventDefault(); self.initialize_regions($(this)); self.update_main_grid_data($(this));
        });
    };//end activate_handlers() function

    /**
     * PHASE 3 HELPER
     *
     * Used in phase 3 to build the promise for each individual region.
     *
     * PHASES:
     * PHASE 1 - Initialization;
     * PHASE 2 - Staging;
     * PHASE 3 - Building;
     * PHASE 4 - Loading;
     *
     * All JSON objects represent a series of targets (locations on the DOM as IDs) and URLs (where to retrieve that
     * regions content from).
     * @param {Promise[]} promises - A collection of existing promises being built for all asynchronous AJAX calls.
     * @param {JSON} json_obj - A JSON object for building a specific region (region is specified in the object's key).
     * @param {boolean} show_toc - Whether to display the toc region or not. In many cases the toc must be displayed
     * only after all promises have been resolved.
     *
     * @returns {number|boolean} - The number of regions built from the supplied JSON object or false if none were built.
     */
    self.build_promise = function(promises, json_obj, show_toc) {
        let regions_to_load = 0;
        $.each(json_obj, function(target, url) {
            if (target === "error") {
                self.build_toast(url, "danger");
                return false;
            }//endif
            if (url === "empty") {
                $(target).empty();
                $(target + "-loader").hide()
                return false;
            }//endif
            let promise;
            if (((Object.keys(json_obj).length - 1) === regions_to_load) && show_toc) {
                promise = self.load_region(target, url, false, function() {
                    self.show_toc();
                });
                promises.push(promise);
            } else {
                promise = self.load_region(target, url, false, function() {
                    self.show_toc();
                    self.show_content();
                });
                promises.push(promise);
            }//endif-else
            regions_to_load += 1;
            self.region_timeout(target);
        });
        return regions_to_load;
    };//end build_promise() function

    /**
     * Builds and loads an individual region outside the full four-phase loading process.
     *
     * @param {JSON} region_json - A JSON object for building a specific region (region is specified in the object's
     * key).
     * @param {string} region_string - The name of the region to load.
     */
    self.build_region = function(region_json, region_string) {
        self.clear_region_timeouts();
        // Prepare to load region.
        let promises = [];
        let regions_to_load = 0;
        // If JSON exists for the specified region, then add it to promises.
        if (typeof region_json !== "undefined" && typeof region_json === "object") {
            $("#" + region_string + "-container-loader").show();
            $("#" + region_string + "-container").empty();
            regions_to_load = self.build_promise(promises, region_json, false);
        }//endif
        self.load_regions(promises, regions_to_load);
    };//end build_region() function

    /**
     * Continues the region loading process by determining which regions need to be loaded, clearing any existing
     * content from regions affected, and then building promises for each region needing to be loaded (PHASE 3).
     *
     * Note: regions are not cleared if staging took place.
     * Note: JSON objects may contain multiple ID and URL pairs (each region may have more than one asynchronous AJAX
     * call for it).
     *
     * PHASES:
     * PHASE 1 - Initialization;
     * PHASE 2 - Staging;
     * PHASE 3 - Building;
     * PHASE 4 - Loading;
     *
     * All JSON objects represent a series of targets (locations on the DOM as IDs) and URLs (where to retrieve that
     * regions content from).
     * @param {Object} empty_region - Whether any region was staged (executed synchronously) or not. Each key/value
     * pair consists of a DOM ID (key) and a boolean value for that region (value).
     * @param {JSON} content - A JSON object for the content region's asynchronous AJAX calls.
     * @param {JSON} profile - A JSON object for the profile region's asynchronous AJAX calls.
     * @param {JSON} toc - A JSON object for the toc region's asynchronous AJAX calls.
     */
    self.build_regions = function(empty_region, content, profile, toc) {
        // Prepare to load regions.
        let promises = [];
        let regions_to_load = 0;
        // If JSON exists for the content region, then add it to promises.
        if (typeof content !== "undefined" && typeof content === "object") {
            let region_id = "#content-container";
            $(region_id + "-loader").show();
            if (empty_region[region_id]) { $(region_id).empty(); }//endif
            regions_to_load += self.build_promise(promises, content, true);
        }//endif
        // If JSON exists for the profile region, then add it to promises.
        if (typeof profile !== "undefined" && typeof profile === "object") {
            let region_id = "#profile-container";
            $(region_id + "-loader").show();
            if (empty_region[region_id]) { $(region_id).empty(); }//endif
            regions_to_load += self.build_promise(promises, profile, false);
        }//endif
        // If JSON exists for the toc region, then add it to promises.
        if (typeof toc !== "undefined" && typeof toc === "object") {
            let region_id = "#toc-container";
            $(region_id + "-loader").show();
            let toc_container = $(region_id);
            toc_container.hide();
            if (empty_region[region_id]) { toc_container.empty(); }
            regions_to_load += self.build_promise(promises, toc, true);
        }//endif
        if (regions_to_load > 0) {
            self.load_regions(promises, regions_to_load);
        }//endif
    };//end build_regions() function

    /**
     * PHASE 1 HELPER
     *
     * Used in phase 1 of the region loading process to ensure that warnings are displayed if a region fails to load.
     */
    self.clear_region_timeouts = function() {
        for (let i = 0; i < self.region_timeouts.length; i++) {
            clearTimeout(self.region_timeouts[i])
        }//endfor
    };//end clear_region_timeouts() function

    /**
     * Starts off the region loading process (PHASE 1).
     *
     * PHASES:
     * PHASE 1 - Initialization;
     * PHASE 2 - Staging;
     * PHASE 3 - Building;
     * PHASE 4 - Loading;
     *
     * @param {string} source_id - The source ID used to pull region data from (in JSON format).
     */
    self.initialize_regions = function(source_id) {
        self.clear_region_timeouts();
        let source;
        if (typeof source_id !== "undefined") {
            source = $(source_id); // We are attempting an autoload operation.
        } else {
            source = source_id; // We got here via a button click.
        }//endif-else
        // If the source_id has an "update-selected" class, then make that adjustment.
        if (source.hasClass("update-selected")) {
            $(".load-regions.update-selected > span:first-child").removeClass("text-warning").addClass("text-light");
            source.children("span:first-child").addClass("text-warning").removeClass("text-light");
        }//endif
        // Attempt to retrieve JSON objects from the calling element's data attributes.
        let content = source.data("content");
        let stage = source.data("stage");
        let profile = source.data("profile");
        let toc = source.data("toc");
        // Set the title everywhere.
        if (typeof source.data("title") !== "undefined") {
            $("#offcanvas-title").html(source.data("title"));
            $("#syllabus-title").html(source.data("title"));
            $(document).prop("title", app_name + " | " + source.data("title"));
        }//endif
        // Update the page URL if needed.
        if (typeof source.data("url") !== "undefined") {
            window.history.pushState(null, "", source.data("url"));
        }//endif
        self.stage_regions(stage, content, profile, toc);
    };//end initialize_regions() function

    /**
     * Loads an individual region via an asynchronous AJAX request.
     *
     * @param {string} target - The target region element on the DOM to receive the result of the AJAX request.
     * @param {string} url - The URL used in the AJAX request.
     * @param {boolean} engage_loader - Whether to trigger the main loading indicator for this AJAX request or not.
     * @param {function=} callback - A callback function to execute once the AJAX request has completed successfully
     * (optional).
     */
    self.load_region = function(target, url, engage_loader, callback) {
        return core.ajax("GET", target, url, engage_loader, "", function () {
            if (!~target.indexOf("toc")) { $(target + "-loader").hide(); }//endif
            self.progress_width += self.progress_increment
            $("#load-progress > div").width(self.progress_width + "%");
            if (typeof callback === "function") {
                callback();
            }//endif
        });
    };//end load_region() function

    /**
     * Completes the region loading process (PHASE 4).
     *
     * PHASES:
     * PHASE 1 - Initialization;
     * PHASE 2 - Staging;
     * PHASE 3 - Building;
     * PHASE 4 - Loading;
     *
     * @param {Promise[]} promises - An array of promises to be resolved during the final loading process.
     * @param {number} regions_to_load - The number of regions to be loaded.
     */
    self.load_regions = function(promises, regions_to_load) {
        // We have something to do, so set up the progress loader!
        let load_progress = $("#load-progress > div");
        load_progress.width(0);
        load_progress.addClass("progress-bar-striped progress-bar-animated");
        self.progress_width = 0;
        self.progress_increment = (100 / regions_to_load);
        // Handle the first promise synchronously (the first content region), then handle any remaining regions
        // asynchronously.
        $.when(...promises).then(function() {
            load_progress.removeClass("progress-bar-striped progress-bar-animated");
            $("#content-container-loader").hide();
            $("#profile-container-loader").hide();
            $("#toc-container-loader").hide();
            $("#interactive-next").attr("disabled", false);
        });
    }//end load_regions() function

    /**
     * Sets a timeout for the loading of a region. If the timer expires before the region is loaded, then a warning is
     * displayed to the user.
     *
     * @param {string} target - The target region to set a timeout for as a DOM ID.
     */
    self.region_timeout = function(target) {
        self.region_timeouts.push(setTimeout(function() {
            if ($(target).is(":empty")) {
                let region_name = $(target).data("name");
                core.build_toast({}, "warning", "Hmm... It's taking a really long time to load " +
                    "the <strong>" + region_name + "</strong> content region. This could be a temporary problem. " +
                    "If there were no errors, then give it a few more seconds, and if the content still doesn't " +
                    "load, try refreshing the page. If the problem persists, please report it.");
            }//endif
        }, 10000));
    }//end region_timeout() function

    /**
     * Displays the content region's segments once the first one has loaded.
     */
    self.show_content = function() {
        if ($(".content-container-first").children().length > 0) {
            let content_containers = $(".content-containers");
            content_containers.addClass("d-grid");
            content_containers.removeClass("d-none");
        }//endif
    };//end show_content() function

    /**
     * Displays the toc region if it has content. Otherwise, this function does nothing.
     */
    self.show_toc = function() {
        let toc_container = $("#toc-container");
        let content_containers = $(".content-containers");
        let content_containers_fully_loaded = true;
        if (content_containers.length > 0) {
            content_containers.each(function() {
                if ($(this).children().length === 0) {
                    content_containers_fully_loaded = false;
                }//endif
            });//end-each
        }//endif
        if (($("#content-container").children().length > 0) && (toc_container.children().length > 0)
            && content_containers_fully_loaded) {
            toc_container.show();
            $("#toc-container-loader").hide();
        }//endif
    };//end show_toc() function

    /**
     * Continues the region loading process by initiating any required synchronous AJAX calls that must be completed
     * before continuing with the building phase (PHASE 2).
     *
     * PHASES:
     * PHASE 1 - Initialization;
     * PHASE 2 - Staging;
     * PHASE 3 - Building;
     * PHASE 4 - Loading;
     *
     * All JSON objects represent a series of targets (locations on the DOM as IDs) and URLs (where to retrieve that
     * regions content from).
     * @param {JSON} stage - A JSON object used for staging (all synchronous AJAX calls).
     * @param {JSON} content - A JSON object for the content region's asynchronous AJAX calls.
     * @param {JSON} profile - A JSON object for the profile region's asynchronous AJAX calls.
     * @param {JSON} toc - A JSON object for the toc region's asynchronous AJAX calls.
     */
    self.stage_regions = function(stage, content, profile, toc) {
        // Stage the content region first, if necessary.
        let promises_stage = [];
        let empty_region = {'#content-container': true, '#profile-container': true, '#toc-container': true}
        if (typeof stage !== "undefined" && typeof stage === "object") {
            $.each(stage, function (target, url) {
                promises_stage.push(self.load_region(target, url, true));
                empty_region[target] = false;
            });
        }//endif
        $.when(...promises_stage).then().done(function() {
            // Determine if the stage has any replacements for any of the regions. If it does, then replace the
            // previous versions of those regions and use the ones from the stage instead.
            if (promises_stage.length > 0) {
                let stage_post = $("#stage_post");
                let stage_post_content = stage_post.data("content");
                let stage_post_profile = stage_post.data("profile");
                let stage_post_toc = stage_post.data("toc");
                if (typeof stage_post_content !== "undefined" && typeof stage_post_content === "object") {
                    content = stage_post_content;
                }//endif
                if (typeof stage_post_profile !== "undefined" && typeof stage_post_profile === "object") {
                    profile = stage_post_profile;
                }//endif
                if (typeof stage_post_toc !== "undefined" && typeof stage_post_toc === "object") {
                    toc = stage_post_toc;
                }//endif
            }//endif
            self.build_regions(empty_region, content, profile, toc);
        });
    }//end stage_regions() function

    /**
     * Updates the main-grid data attributes to allow proper reloading operations later on.
     */
    self.update_main_grid_data = function(source) {
        let main_grid = $("#main-grid");
        main_grid.attr("data-content", JSON.stringify(source.data("content")));
        main_grid.data("content", JSON.stringify(source.data("content")));
        main_grid.attr("data-profile", JSON.stringify(source.data("profile")));
        main_grid.data("profile", JSON.stringify(source.data("profile")));
        main_grid.attr("data-toc", JSON.stringify(source.data("toc")));
        main_grid.data("toc", JSON.stringify(source.data("toc")));
        main_grid.attr("data-title", source.data("title"));
        main_grid.data("title", source.data("title"));
        main_grid.attr("data-url", source.data("url"));
        main_grid.data("url", source.data("url"));
    };//end update_main_grid_data() function

    return self;
}());