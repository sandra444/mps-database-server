$(document).ready(function() {

    jQuery.fn.sortElements = (function(){
        var sort = [].sort;
        return function(comparator, getSortable) {
            getSortable = getSortable || function(){return this;};
            var placements = this.map(function(){
                var sortElement = getSortable.call(this),
                    parentNode = sortElement.parentNode,
                    // Since the element itself will change position, we have
                    // to have some way of storing its original position in
                    // the DOM. The easiest way is to have a 'flag' node:
                    nextSibling = parentNode.insertBefore(
                        document.createTextNode(''),
                        sortElement.nextSibling
                    );
                return function() {
                    if (parentNode === this) {
                        throw new Error(
                            "You can't sort elements if any one is a descendant of another."
                        );
                    }
                    // Insert before flag:
                    parentNode.insertBefore(this, nextSibling);
                    // Remove flag:
                    parentNode.removeChild(nextSibling);
                };
            });
            return sort.call(this, comparator).each(function(i){
                placements[i].call(getSortable.call(this));
            });
        };
    })();


    function renameApps() {
        modules.find('table > caption > a').each(function (i, e) {
            e = $(e);
            var text = e.text().trim();
            if (APPS.hasOwnProperty(text)) {
                e.text(APPS[text][1]);
            }
        });

    };

    var INDENT = ["", "&nbsp;&nbsp;&#8866; ", "&nbsp;&nbsp;&nbsp;&nbsp;&#8866; ",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#8866; "]

    function renameModels(app, module) {
       if (MODELS.hasOwnProperty(app)) {
            app = MODELS[app];
            modules.find('table > tbody > tr > th > a').each(function (i, e) {
                e = $(e);
                var text = e.text().trim();
                if (app.hasOwnProperty(text)) {
                    e.html(INDENT[app[text][2]] + app[text][1]);
                 };
            });
        };
    };

    function sortModels(app, module) {
        if (MODELS.hasOwnProperty(app)) {
            app = MODELS[app];

            module.find('table > tbody > tr').sortElements(function(a, b){
                var text = $(a).find('th > a').text().trim();
                a = app.hasOwnProperty(text) ? app[text][0] : 100;
                var text = $(b).find('th > a').text().trim();
                b = app.hasOwnProperty(text) ? app[text][0] : 100;
                return a > b ? 1 : -1;
            });
        };
    };
    
    function renameBreadcrumbs() {
        var breadcrumbs = $('.breadcrumbs');
        var items = breadcrumbs.text().split('›')
        var last = items[items.length - 1].trim();
        var bcs = $('.breadcrumbs > a').clone();
        if (bcs.length > 1) {
            var bc = $(bcs[1]);
            var app = bc.text().trim();
            if (APPS.hasOwnProperty(app))
                bc.text(APPS[app][1]);
            if (MODELS.hasOwnProperty(app)) {
                app = MODELS[app];
                if (bcs.length > 2) {
                    bc = $(bcs[2]);
                    model = bc.text().trim();
                    if (app.hasOwnProperty(model))
                        bc.text(app[model][1]);
                } else {
                    if (app.hasOwnProperty(last))
                        last = app[last][1];
                };
            };
        } else {
            if (APPS.hasOwnProperty(last))
                last = APPS[last][1];
        };
        breadcrumbs.text('')
        for (var i = 0; i < bcs.length; i++) {
            breadcrumbs.append(bcs[i]);
            breadcrumbs.append(' › ')
        }
        breadcrumbs.append(last);
    };
    
    if ($('.breadcrumbs > a').length < 2) {
        // ADMIN INDEX or APP INDEX page
        var modules = $('#content-main > .module');
        if (modules.find('table > caption').length > 1) {
            // ADMIN INDEX page
            // hide models, by removing them
            modules.each(function(i, e) {
                e = $(e)
                var app = e.find('table > caption > a').text().trim();
                if (MODELS.hasOwnProperty(app)) {
                    e.find('table > tbody > tr').each(function(i, e) {
                        e = $(e);
                        var model = e.find('th > a').text().trim();
                        if (MODELS[app].hasOwnProperty(model)) {
                            if (MODELS[app][model][3]) {
                                e.remove();
                            }
                        }
                    });

                }
                sortModels(app, e);
                renameModels(app, e);
            });

            // sort apps
            modules.sortElements(function(a, b){
                var text = $(a).find('table > caption > a').text().trim();
                a = APPS.hasOwnProperty(text) ? APPS[text][0] : 100;
                var text = $(b).find('table > caption > a').text().trim();
                b = APPS.hasOwnProperty(text) ? APPS[text][0] : 100;
                return a > b ? 1 : -1;
            });

            renameApps(modules);
        } else {
            module = $(modules[0]);
            var app = module.find('table > caption > a').text().trim();
            if (APPS.hasOwnProperty(app))
                $('#content > h1').text(APPS[app][1] + " administration");
            sortModels(app, module);
            renameModels(app, module);
            renameApps(modules);
        };
    };
    renameBreadcrumbs();
});
