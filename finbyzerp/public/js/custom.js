frappe.provide('frappe.ui.misc');

// Extending(Overiding) about.js
$("div.footer-powered").html(`<a href="https://finbyz.tech/" target="_blank" class="text-muted">Powered by FinbyzERP -  ERP Software for Distribution Companies</a>`)
frappe.ui.misc.about = function() {

	if(!frappe.ui.misc.about_dialog) {
		var d = new frappe.ui.Dialog({title: __('<img src="https://finbyz.tech/files/finbyz-tech.svg" width="180">')});

		$(d.body).html(repl("<div>\
		<p>"+__("At Finbyz Tech, we are passionate about revolutionizing businesses through the latest technology.")+"</p>  \
		<p><i class='fa fa-globe fa-fw'></i>\
			Website: <a href=' https://finbyz.tech' target='_blank'> https://finbyz.tech</a></p>\
		<p><i class='fa fa-github fa-fw'></i>\
			Support: <a href='support@finbyz.tech' target='_blank'>support@finbyz.tech</a></p>\
		<hr>\
		<h4>Installed Apps</h4>\
		<div id='about-app-versions'>Loading versions...</div>\
		<hr>\
		<p class='text-muted'>&copy; Finbyz Erp is powered by opensource technologies </p> \
		</div>", frappe.app));

		frappe.ui.misc.about_dialog = d;
		frappe.ui.misc.about_dialog.on_page_show = function() {
			
			if(!frappe.versions) {
				frappe.call({
					method: "frappe.utils.change_log.get_versions",
					callback: function(r) {
						show_versions(r.message);
					}
				})
			} else {
				show_versions(frappe.versions);
			}
		};

		var show_versions = function(versions) {
			var $wrap = $("#about-app-versions").empty();
			$.each(Object.keys(versions).sort(), function(i, key) {
				var v = versions[key];
				if(v.branch) {
					var text = $.format('<p><b>{0}:</b> v{1} ({2})<br></p>',
						[v.title, v.branch_version || v.version, v.branch])
				} else {
					var text = $.format('<p><b>{0}:</b> v{1}<br></p>',
						[v.title, v.version])
				}
				$(text).appendTo($wrap);
			});

			frappe.versions = versions;
		}

	}

	frappe.ui.misc.about_dialog.show();

}

//Extending(Overiding) toolbar.js
frappe.provide("frappe.ui.toolbar");
frappe.provide('frappe.search');

frappe.ui.toolbar.Toolbar = Class.extend({
	init: function() {
		$('header').append(frappe.render_template("navbar", {
			avatar: frappe.avatar(frappe.session.user)
		}));

		$('.navbar-home').html('<i class="fa fa-home"style="font-size: 25px !important;" aria-hidden="true"></i>');
		$('.navbar-home').css("padding","6px 15px");

		$('.dropdown-toggle').dropdown();

		let awesome_bar = new frappe.search.AwesomeBar();
		awesome_bar.setup("#navbar-search");
		awesome_bar.setup("#modal-search");

		this.make();
	},

	make: function() {
		this.setup_sidebar();
		this.setup_help();

		this.bind_events();

		$(document).trigger('toolbar_setup');
	},

	bind_events: function() {
		$(document).on("notification-update", function() {
			frappe.ui.notifications.update_notifications();
		});

		// clear all custom menus on page change
		$(document).on("page-change", function() {
			$("header .navbar .custom-menu").remove();
		});

		//focus search-modal on show in mobile view
		$('#search-modal').on('shown.bs.modal', function() {
			var search_modal = $(this);
			setTimeout(function() {
				search_modal.find('#modal-search').focus();
			}, 300);
		});
		$('.navbar-toggle-full-width').click(() => {
			frappe.ui.toolbar.toggle_full_width();
		});
	},

	setup_sidebar: function() {
		var header = $('header');
		header.find(".toggle-sidebar").on("click", function() {
			var layout_side_section = $('.layout-side-section');
			var overlay_sidebar = layout_side_section.find('.overlay-sidebar');

			overlay_sidebar.addClass('opened');
			overlay_sidebar.find('.reports-dropdown')
				.removeClass('dropdown-menu')
				.addClass('list-unstyled');
			overlay_sidebar.find('.dropdown-toggle')
				.addClass('text-muted').find('.caret')
				.addClass('hidden-xs hidden-sm');

			$('<div class="close-sidebar">').hide().appendTo(layout_side_section).fadeIn();

			var scroll_container = $('html');
			scroll_container.css("overflow-y", "hidden");

			layout_side_section.find(".close-sidebar").on('click', close_sidebar);
			layout_side_section.on("click", "a:not(.dropdown-toggle)", close_sidebar);

			function close_sidebar(e) {
				scroll_container.css("overflow-y", "");

				layout_side_section.find("div.close-sidebar").fadeOut(function() {
					overlay_sidebar.removeClass('opened')
						.find('.dropdown-toggle')
						.removeClass('text-muted');
					overlay_sidebar.find('.reports-dropdown')
						.addClass('dropdown-menu');
				});
			}
		});
	},

	setup_help: function() {
		frappe.provide('frappe.help');
		frappe.help.show_results = show_results;

		this.search = new frappe.search.SearchDialog();
		frappe.provide('frappe.searchdialog');
		frappe.searchdialog.search = this.search;

		$(".dropdown-help .dropdown-toggle").on("click", function() {
			$(".dropdown-help input").focus();
		});

		$(".dropdown-help .dropdown-menu").on("click", "input, button", function(e) {
			e.stopPropagation();
		});

		$("#input-help").on("keydown", function(e) {
			if(e.which == 13) {
				$(this).val("");
			}
		});
		$('.dropdown-help .dropdown-menu').on('click', 'a', show_results);
		$(document).on("page-change", function () {
			var $help_links = $(".dropdown-help #help-links");
			$help_links.html("");

			var route = frappe.get_route_str();
			var breadcrumbs = route.split("/");

			var links = [];
			for (var i = 0; i < breadcrumbs.length; i++) {
				var r = route.split("/", i + 1);
				var key = r.join("/");
				var help_links = frappe.help.help_links[key] || [];
				links = $.merge(links, help_links);
			}

			if(links.length === 0) {
				$help_links.next().hide();
			} else {
				$help_links.next().show();
			}

			for (var i = 0; i < links.length; i++) {
				var link = links[i];
				var url = link.url;
				$("<a>", {
					href: link.url,
					text: link.label,
					target: "_blank"
				}).appendTo($help_links);
			}

			$('.dropdown-help .dropdown-menu').on('click', 'a', show_results);
		});

		var $result_modal = frappe.get_modal("", "");
		$result_modal.addClass("help-modal");

		$(document).on("click", ".help-modal a", show_results);

		function show_results(e) {
			//edit links
			var href = e.target.href;
			
			if(href === "https://github.com/frappe/erpnext/issues"){
				var project_name = "";
				frappe.call({
					method:  "finbyzerp.api.get_project_name",
					async: false,
					callback: function(r) {
						console.log(r);
						e.target.href = `https://finbyz.tech/issue-form?new=1&project=${r.message.project_name}&raised_by=${frappe.session.user_email}&contact_person=${frappe.session.user_fullname}`;	
					}
				});
			}
			if(href.indexOf('blob') > 0) {
				window.open(href, '_blank');
			}
			var path = $(e.target).attr("data-path");
			if(path) {
				e.preventDefault();
			}
		}
	}
});

$.extend(frappe.ui.toolbar, {
	add_dropdown_button: function(parent, label, click, icon) {
		var menu = frappe.ui.toolbar.get_menu(parent);
		if(menu.find("li:not(.custom-menu)").length && !menu.find(".divider").length) {
			frappe.ui.toolbar.add_menu_divider(menu);
		}

		return $('<li class="custom-menu"><a><i class="fa-fw '
			+icon+'"></i> '+label+'</a></li>')
			.insertBefore(menu.find(".divider"))
			.find("a")
			.click(function() {
				click.apply(this);
			});
	},
	get_menu: function(label) {
		return $("#navbar-" + label.toLowerCase());
	},
	add_menu_divider: function(menu) {
		menu = typeof menu == "string" ?
			frappe.ui.toolbar.get_menu(menu) : menu;

		$('<li class="divider custom-menu"></li>').prependTo(menu);
	},
	add_icon_link(route, icon, index, class_name) {
		let parent_element = $(".navbar-right").get(0);
		let new_element = $(`<li class="${class_name}">
			<a class="btn" href="${route}" title="${frappe.utils.to_title_case(class_name, true)}" aria-haspopup="true" aria-expanded="true">
				<div>
					<i class="octicon ${icon}"></i>
				</div>
			</a>
		</li>`).get(0);

		parent_element.insertBefore(new_element, parent_element.children[index]);
	},
	toggle_full_width() {
		let fullwidth = JSON.parse(localStorage.container_fullwidth || 'false');
		fullwidth = !fullwidth;
		localStorage.container_fullwidth = fullwidth;
		frappe.ui.toolbar.set_fullwidth_if_enabled();
	},
	set_fullwidth_if_enabled() {
		let fullwidth = JSON.parse(localStorage.container_fullwidth || 'false');
		$(document.body).toggleClass('full-width', fullwidth);
	},
	show_shortcuts (e) {
		e.preventDefault();
		frappe.ui.keys.show_keyboard_shortcut_dialog();
		return false;
	},
});

frappe.ui.toolbar.clear_cache = function() {
	frappe.assets.clear_local_storage();
	frappe.call({
		method: 'frappe.sessions.clear',
		callback: function(r) {
			if(!r.exc) {
				frappe.show_alert({message:r.message, indicator:'green'});
				location.reload(true);
			}
		}
	});
	return false;
};

frappe.ui.toolbar.show_about = function() {
	try {
		frappe.ui.misc.about();
	} catch(e) {
		console.log(e);
	}
	return false;
};