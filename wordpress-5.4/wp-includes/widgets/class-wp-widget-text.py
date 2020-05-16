#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import cgi
    import os
    import os.path
    import copy
    import sys
    from goto import with_goto
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
#// 
#// Widget API: WP_Widget_Text class
#// 
#// @package WordPress
#// @subpackage Widgets
#// @since 4.4.0
#// 
#// 
#// Core class used to implement a Text widget.
#// 
#// @since 2.8.0
#// 
#// @see WP_Widget
#//
class WP_Widget_Text(WP_Widget):
    registered = False
    #// 
    #// Sets up a new Text widget instance.
    #// 
    #// @since 2.8.0
    #//
    def __init__(self):
        
        widget_ops = Array({"classname": "widget_text", "description": __("Arbitrary text."), "customize_selective_refresh": True})
        control_ops = Array({"width": 400, "height": 350})
        super().__init__("text", __("Text"), widget_ops, control_ops)
    # end def __init__
    #// 
    #// Add hooks for enqueueing assets when registering all widget instances of this widget class.
    #// 
    #// @param integer $number Optional. The unique order number of this widget instance
    #// compared to other instances of the same class. Default -1.
    #//
    def _register_one(self, number=-1):
        
        super()._register_one(number)
        if self.registered:
            return
        # end if
        self.registered = True
        wp_add_inline_script("text-widgets", php_sprintf("wp.textWidgets.idBases.push( %s );", wp_json_encode(self.id_base)))
        if self.is_preview():
            add_action("wp_enqueue_scripts", Array(self, "enqueue_preview_scripts"))
        # end if
        #// Note that the widgets component in the customizer will also do
        #// the 'admin_print_scripts-widgets.php' action in WP_Customize_Widgets::print_scripts().
        add_action("admin_print_scripts-widgets.php", Array(self, "enqueue_admin_scripts"))
        #// Note that the widgets component in the customizer will also do
        #// the 'admin_footer-widgets.php' action in WP_Customize_Widgets::print_footer_scripts().
        add_action("admin_footer-widgets.php", Array("WP_Widget_Text", "render_control_template_scripts"))
    # end def _register_one
    #// 
    #// Determines whether a given instance is legacy and should bypass using TinyMCE.
    #// 
    #// @since 4.8.1
    #// 
    #// @param array $instance {
    #// Instance data.
    #// 
    #// @type string      $text   Content.
    #// @type bool|string $filter Whether autop or content filters should apply.
    #// @type bool        $legacy Whether widget is in legacy mode.
    #// }
    #// @return bool Whether Text widget instance contains legacy data.
    #//
    def is_legacy_instance(self, instance=None):
        
        #// Legacy mode when not in visual mode.
        if (php_isset(lambda : instance["visual"])):
            return (not instance["visual"])
        # end if
        #// Or, the widget has been added/updated in 4.8.0 then filter prop is 'content' and it is no longer legacy.
        if (php_isset(lambda : instance["filter"])) and "content" == instance["filter"]:
            return False
        # end if
        #// If the text is empty, then nothing is preventing migration to TinyMCE.
        if php_empty(lambda : instance["text"]):
            return False
        # end if
        wpautop = (not php_empty(lambda : instance["filter"]))
        has_line_breaks = False != php_strpos(php_trim(instance["text"]), "\n")
        #// If auto-paragraphs are not enabled and there are line breaks, then ensure legacy mode.
        if (not wpautop) and has_line_breaks:
            return True
        # end if
        #// If an HTML comment is present, assume legacy mode.
        if False != php_strpos(instance["text"], "<!--"):
            return True
        # end if
        #// In the rare case that DOMDocument is not available we cannot reliably sniff content and so we assume legacy.
        if (not php_class_exists("DOMDocument")):
            #// @codeCoverageIgnoreStart
            return True
            pass
        # end if
        doc = php_new_class("DOMDocument", lambda : DOMDocument())
        #// Suppress warnings generated by loadHTML.
        errors = libxml_use_internal_errors(True)
        #// phpcs:ignore WordPress.PHP.NoSilencedErrors.Discouraged
        php_no_error(lambda: doc.loadhtml(php_sprintf("<!DOCTYPE html><html><head><meta charset=\"%s\"></head><body>%s</body></html>", esc_attr(get_bloginfo("charset")), instance["text"])))
        libxml_use_internal_errors(errors)
        body = doc.getelementsbytagname("body").item(0)
        #// See $allowedposttags.
        safe_elements_attributes = Array({"strong": Array(), "em": Array(), "b": Array(), "i": Array(), "u": Array(), "s": Array(), "ul": Array(), "ol": Array(), "li": Array(), "hr": Array(), "abbr": Array(), "acronym": Array(), "code": Array(), "dfn": Array(), "a": Array({"href": True})}, {"img": Array({"src": True, "alt": True})})
        safe_empty_elements = Array("img", "hr", "iframe")
        for element in body.getelementsbytagname("*"):
            #// @var DOMElement $element
            tag_name = php_strtolower(element.nodeName)
            #// If the element is not safe, then the instance is legacy.
            if (not (php_isset(lambda : safe_elements_attributes[tag_name]))):
                return True
            # end if
            #// If the element is not safely empty and it has empty contents, then legacy mode.
            if (not php_in_array(tag_name, safe_empty_elements, True)) and "" == php_trim(element.textContent):
                return True
            # end if
            #// If an attribute is not recognized as safe, then the instance is legacy.
            for attribute in element.attributes:
                #// @var DOMAttr $attribute
                attribute_name = php_strtolower(attribute.nodeName)
                if (not (php_isset(lambda : safe_elements_attributes[tag_name][attribute_name]))):
                    return True
                # end if
            # end for
        # end for
        #// Otherwise, the text contains no elements/attributes that TinyMCE could drop, and therefore the widget does not need legacy mode.
        return False
    # end def is_legacy_instance
    #// 
    #// Filter gallery shortcode attributes.
    #// 
    #// Prevents all of a site's attachments from being shown in a gallery displayed on a
    #// non-singular template where a $post context is not available.
    #// 
    #// @since 4.9.0
    #// 
    #// @param array $attrs Attributes.
    #// @return array Attributes.
    #//
    def _filter_gallery_shortcode_attrs(self, attrs=None):
        
        if (not is_singular()) and php_empty(lambda : attrs["id"]) and php_empty(lambda : attrs["include"]):
            attrs["id"] = -1
        # end if
        return attrs
    # end def _filter_gallery_shortcode_attrs
    #// 
    #// Outputs the content for the current Text widget instance.
    #// 
    #// @since 2.8.0
    #// 
    #// @global WP_Post $post Global post object.
    #// 
    #// @param array $args     Display arguments including 'before_title', 'after_title',
    #// 'before_widget', and 'after_widget'.
    #// @param array $instance Settings for the current Text widget instance.
    #//
    def widget(self, args=None, instance=None):
        
        global post
        php_check_if_defined("post")
        title = instance["title"] if (not php_empty(lambda : instance["title"])) else ""
        #// This filter is documented in wp-includes/widgets/class-wp-widget-pages.php
        title = apply_filters("widget_title", title, instance, self.id_base)
        text = instance["text"] if (not php_empty(lambda : instance["text"])) else ""
        is_visual_text_widget = (not php_empty(lambda : instance["visual"])) and (not php_empty(lambda : instance["filter"]))
        #// In 4.8.0 only, visual Text widgets get filter=content, without visual prop; upgrade instance props just-in-time.
        if (not is_visual_text_widget):
            is_visual_text_widget = (php_isset(lambda : instance["filter"])) and "content" == instance["filter"]
        # end if
        if is_visual_text_widget:
            instance["filter"] = True
            instance["visual"] = True
        # end if
        #// 
        #// Suspend legacy plugin-supplied do_shortcode() for 'widget_text' filter for the visual Text widget to prevent
        #// shortcodes being processed twice. Now do_shortcode() is added to the 'widget_text_content' filter in core itself
        #// and it applies after wpautop() to prevent corrupting HTML output added by the shortcode. When do_shortcode() is
        #// added to 'widget_text_content' then do_shortcode() will be manually called when in legacy mode as well.
        #//
        widget_text_do_shortcode_priority = has_filter("widget_text", "do_shortcode")
        should_suspend_legacy_shortcode_support = is_visual_text_widget and False != widget_text_do_shortcode_priority
        if should_suspend_legacy_shortcode_support:
            remove_filter("widget_text", "do_shortcode", widget_text_do_shortcode_priority)
        # end if
        #// Override global $post so filters (and shortcodes) apply in a consistent context.
        original_post = post
        if is_singular():
            #// Make sure post is always the queried object on singular queries (not from another sub-query that failed to clean up the global $post).
            post = get_queried_object()
        else:
            #// Nullify the $post global during widget rendering to prevent shortcodes from running with the unexpected context on archive queries.
            post = None
        # end if
        #// Prevent dumping out all attachments from the media library.
        add_filter("shortcode_atts_gallery", Array(self, "_filter_gallery_shortcode_attrs"))
        #// 
        #// Filters the content of the Text widget.
        #// 
        #// @since 2.3.0
        #// @since 4.4.0 Added the `$this` parameter.
        #// @since 4.8.1 The `$this` param may now be a `WP_Widget_Custom_HTML` object in addition to a `WP_Widget_Text` object.
        #// 
        #// @param string                               $text     The widget content.
        #// @param array                                $instance Array of settings for the current widget.
        #// @param WP_Widget_Text|WP_Widget_Custom_HTML $this     Current Text widget instance.
        #//
        text = apply_filters("widget_text", text, instance, self)
        if is_visual_text_widget:
            #// 
            #// Filters the content of the Text widget to apply changes expected from the visual (TinyMCE) editor.
            #// 
            #// By default a subset of the_content filters are applied, including wpautop and wptexturize.
            #// 
            #// @since 4.8.0
            #// 
            #// @param string         $text     The widget content.
            #// @param array          $instance Array of settings for the current widget.
            #// @param WP_Widget_Text $this     Current Text widget instance.
            #//
            text = apply_filters("widget_text_content", text, instance, self)
        else:
            #// Now in legacy mode, add paragraphs and line breaks when checkbox is checked.
            if (not php_empty(lambda : instance["filter"])):
                text = wpautop(text)
            # end if
            #// 
            #// Manually do shortcodes on the content when the core-added filter is present. It is added by default
            #// in core by adding do_shortcode() to the 'widget_text_content' filter to apply after wpautop().
            #// Since the legacy Text widget runs wpautop() after 'widget_text' filters are applied, the widget in
            #// legacy mode here manually applies do_shortcode() on the content unless the default
            #// core filter for 'widget_text_content' has been removed, or if do_shortcode() has already
            #// been applied via a plugin adding do_shortcode() to 'widget_text' filters.
            #//
            if has_filter("widget_text_content", "do_shortcode") and (not widget_text_do_shortcode_priority):
                if (not php_empty(lambda : instance["filter"])):
                    text = shortcode_unautop(text)
                # end if
                text = do_shortcode(text)
            # end if
        # end if
        #// Restore post global.
        post = original_post
        remove_filter("shortcode_atts_gallery", Array(self, "_filter_gallery_shortcode_attrs"))
        #// Undo suspension of legacy plugin-supplied shortcode handling.
        if should_suspend_legacy_shortcode_support:
            add_filter("widget_text", "do_shortcode", widget_text_do_shortcode_priority)
        # end if
        php_print(args["before_widget"])
        if (not php_empty(lambda : title)):
            php_print(args["before_title"] + title + args["after_title"])
        # end if
        text = preg_replace_callback("#<(video|iframe|object|embed)\\s[^>]*>#i", Array(self, "inject_video_max_width_style"), text)
        #// Adds noreferrer and noopener relationships, without duplicating values, to all HTML A elements that have a target.
        text = wp_targeted_link_rel(text)
        php_print("         <div class=\"textwidget\">")
        php_print(text)
        php_print("</div>\n     ")
        php_print(args["after_widget"])
    # end def widget
    #// 
    #// Inject max-width and remove height for videos too constrained to fit inside sidebars on frontend.
    #// 
    #// @since 4.9.0
    #// 
    #// @see WP_Widget_Media_Video::inject_video_max_width_style()
    #// 
    #// @param array $matches Pattern matches from preg_replace_callback.
    #// @return string HTML Output.
    #//
    def inject_video_max_width_style(self, matches=None):
        
        html = matches[0]
        html = php_preg_replace("/\\sheight=\"\\d+\"/", "", html)
        html = php_preg_replace("/\\swidth=\"\\d+\"/", "", html)
        html = php_preg_replace("/(?<=width:)\\s*\\d+px(?=;?)/", "100%", html)
        return html
    # end def inject_video_max_width_style
    #// 
    #// Handles updating settings for the current Text widget instance.
    #// 
    #// @since 2.8.0
    #// 
    #// @param array $new_instance New settings for this instance as input by the user via
    #// WP_Widget::form().
    #// @param array $old_instance Old settings for this instance.
    #// @return array Settings to save or bool false to cancel saving.
    #//
    def update(self, new_instance=None, old_instance=None):
        
        new_instance = wp_parse_args(new_instance, Array({"title": "", "text": "", "filter": False, "visual": None}))
        instance = old_instance
        instance["title"] = sanitize_text_field(new_instance["title"])
        if current_user_can("unfiltered_html"):
            instance["text"] = new_instance["text"]
        else:
            instance["text"] = wp_kses_post(new_instance["text"])
        # end if
        instance["filter"] = (not php_empty(lambda : new_instance["filter"]))
        #// Upgrade 4.8.0 format.
        if (php_isset(lambda : old_instance["filter"])) and "content" == old_instance["filter"]:
            instance["visual"] = True
        # end if
        if "content" == new_instance["filter"]:
            instance["visual"] = True
        # end if
        if (php_isset(lambda : new_instance["visual"])):
            instance["visual"] = (not php_empty(lambda : new_instance["visual"]))
        # end if
        #// Filter is always true in visual mode.
        if (not php_empty(lambda : instance["visual"])):
            instance["filter"] = True
        # end if
        return instance
    # end def update
    #// 
    #// Enqueue preview scripts.
    #// 
    #// These scripts normally are enqueued just-in-time when a playlist shortcode is used.
    #// However, in the customizer, a playlist shortcode may be used in a text widget and
    #// dynamically added via selective refresh, so it is important to unconditionally enqueue them.
    #// 
    #// @since 4.9.3
    #//
    def enqueue_preview_scripts(self):
        
        php_include_file(php_dirname(__DIR__) + "/media.php", once=True)
        wp_playlist_scripts("audio")
        wp_playlist_scripts("video")
    # end def enqueue_preview_scripts
    #// 
    #// Loads the required scripts and styles for the widget control.
    #// 
    #// @since 4.8.0
    #//
    def enqueue_admin_scripts(self):
        
        wp_enqueue_editor()
        wp_enqueue_media()
        wp_enqueue_script("text-widgets")
        wp_add_inline_script("text-widgets", "wp.textWidgets.init();", "after")
    # end def enqueue_admin_scripts
    #// 
    #// Outputs the Text widget settings form.
    #// 
    #// @since 2.8.0
    #// @since 4.8.0 Form only contains hidden inputs which are synced with JS template.
    #// @since 4.8.1 Restored original form to be displayed when in legacy mode.
    #// 
    #// @see WP_Widget_Text::render_control_template_scripts()
    #// @see _WP_Editors::editor()
    #// 
    #// @param array $instance Current settings.
    #//
    def form(self, instance=None):
        
        instance = wp_parse_args(instance, Array({"title": "", "text": ""}))
        php_print("     ")
        if (not self.is_legacy_instance(instance)):
            php_print("         ")
            if user_can_richedit():
                add_filter("the_editor_content", "format_for_editor", 10, 2)
                default_editor = "tinymce"
            else:
                default_editor = "html"
            # end if
            #// This filter is documented in wp-includes/class-wp-editor.php
            text = apply_filters("the_editor_content", instance["text"], default_editor)
            #// Reset filter addition.
            if user_can_richedit():
                remove_filter("the_editor_content", "format_for_editor")
            # end if
            #// Prevent premature closing of textarea in case format_for_editor() didn't apply or the_editor_content filter did a wrong thing.
            escaped_text = php_preg_replace("#</textarea#i", "&lt;/textarea", text)
            php_print("         <input id=\"")
            php_print(self.get_field_id("title"))
            php_print("\" name=\"")
            php_print(self.get_field_name("title"))
            php_print("\" class=\"title sync-input\" type=\"hidden\" value=\"")
            php_print(esc_attr(instance["title"]))
            php_print("\">\n            <textarea id=\"")
            php_print(self.get_field_id("text"))
            php_print("\" name=\"")
            php_print(self.get_field_name("text"))
            php_print("\" class=\"text sync-input\" hidden>")
            php_print(escaped_text)
            php_print("</textarea>\n            <input id=\"")
            php_print(self.get_field_id("filter"))
            php_print("\" name=\"")
            php_print(self.get_field_name("filter"))
            php_print("\" class=\"filter sync-input\" type=\"hidden\" value=\"on\">\n           <input id=\"")
            php_print(self.get_field_id("visual"))
            php_print("\" name=\"")
            php_print(self.get_field_name("visual"))
            php_print("\" class=\"visual sync-input\" type=\"hidden\" value=\"on\">\n       ")
        else:
            php_print("         <input id=\"")
            php_print(self.get_field_id("visual"))
            php_print("\" name=\"")
            php_print(self.get_field_name("visual"))
            php_print("\" class=\"visual\" type=\"hidden\" value=\"\">\n            <p>\n               <label for=\"")
            php_print(self.get_field_id("title"))
            php_print("\">")
            _e("Title:")
            php_print("</label>\n               <input class=\"widefat\" id=\"")
            php_print(self.get_field_id("title"))
            php_print("\" name=\"")
            php_print(self.get_field_name("title"))
            php_print("\" type=\"text\" value=\"")
            php_print(esc_attr(instance["title"]))
            php_print("""\"/>
            </p>
            <div class=\"notice inline notice-info notice-alt\">
            """)
            if (not (php_isset(lambda : instance["visual"]))):
                php_print("                 <p>")
                _e("This widget may contain code that may work better in the &#8220;Custom HTML&#8221; widget. How about trying that widget instead?")
                php_print("</p>\n               ")
            else:
                php_print("                 <p>")
                _e("This widget may have contained code that may work better in the &#8220;Custom HTML&#8221; widget. If you haven&#8217;t yet, how about trying that widget instead?")
                php_print("</p>\n               ")
            # end if
            php_print("         </div>\n            <p>\n               <label for=\"")
            php_print(self.get_field_id("text"))
            php_print("\">")
            _e("Content:")
            php_print("</label>\n               <textarea class=\"widefat\" rows=\"16\" cols=\"20\" id=\"")
            php_print(self.get_field_id("text"))
            php_print("\" name=\"")
            php_print(self.get_field_name("text"))
            php_print("\">")
            php_print(esc_textarea(instance["text"]))
            php_print("""</textarea>
            </p>
            <p>
            <input id=\"""")
            php_print(self.get_field_id("filter"))
            php_print("\" name=\"")
            php_print(self.get_field_name("filter"))
            php_print("\" type=\"checkbox\"")
            checked((not php_empty(lambda : instance["filter"])))
            php_print(" />&nbsp;<label for=\"")
            php_print(self.get_field_id("filter"))
            php_print("\">")
            _e("Automatically add paragraphs")
            php_print("</label>\n           </p>\n          ")
        # end if
    # end def form
    #// 
    #// Render form template scripts.
    #// 
    #// @since 4.8.0
    #// @since 4.9.0 The method is now static.
    #//
    @classmethod
    def render_control_template_scripts(self):
        
        dismissed_pointers = php_explode(",", php_str(get_user_meta(get_current_user_id(), "dismissed_wp_pointers", True)))
        php_print("""       <script type=\"text/html\" id=\"tmpl-widget-text-control-fields\">
        <# var elementIdPrefix = 'el' + String( Math.random() ).replace( /\\D/g, '' ) + '_' #>
        <p>
        <label for=\"{{ elementIdPrefix }}title\">""")
        esc_html_e("Title:")
        php_print("""</label>
        <input id=\"{{ elementIdPrefix }}title\" type=\"text\" class=\"widefat title\">
        </p>
        """)
        if (not php_in_array("text_widget_custom_html", dismissed_pointers, True)):
            php_print("             <div hidden class=\"wp-pointer custom-html-widget-pointer wp-pointer-top\">\n                   <div class=\"wp-pointer-content\">\n                        <h3>")
            _e("New Custom HTML Widget")
            php_print("</h3>\n                      ")
            if is_customize_preview():
                php_print("                         <p>")
                _e("Did you know there is a &#8220;Custom HTML&#8221; widget now? You can find it by pressing the &#8220;<a class=\"add-widget\" href=\"#\">Add a Widget</a>&#8221; button and searching for &#8220;HTML&#8221;. Check it out to add some custom code to your site!")
                php_print("</p>\n                       ")
            else:
                php_print("                         <p>")
                _e("Did you know there is a &#8220;Custom HTML&#8221; widget now? You can find it by scanning the list of available widgets on this screen. Check it out to add some custom code to your site!")
                php_print("</p>\n                       ")
            # end if
            php_print("                     <div class=\"wp-pointer-buttons\">\n                            <a class=\"close\" href=\"#\">")
            _e("Dismiss")
            php_print("""</a>
            </div>
            </div>
            <div class=\"wp-pointer-arrow\">
            <div class=\"wp-pointer-arrow-inner\"></div>
            </div>
            </div>
            """)
        # end if
        php_print("\n           ")
        if (not php_in_array("text_widget_paste_html", dismissed_pointers, True)):
            php_print("             <div hidden class=\"wp-pointer paste-html-pointer wp-pointer-top\">\n                   <div class=\"wp-pointer-content\">\n                        <h3>")
            _e("Did you just paste HTML?")
            php_print("</h3>\n                      <p>")
            _e("Hey there, looks like you just pasted HTML into the &#8220;Visual&#8221; tab of the Text widget. You may want to paste your code into the &#8220;Text&#8221; tab instead. Alternately, try out the new &#8220;Custom HTML&#8221; widget!")
            php_print("</p>\n                       <div class=\"wp-pointer-buttons\">\n                            <a class=\"close\" href=\"#\">")
            _e("Dismiss")
            php_print("""</a>
            </div>
            </div>
            <div class=\"wp-pointer-arrow\">
            <div class=\"wp-pointer-arrow-inner\"></div>
            </div>
            </div>
            """)
        # end if
        php_print("\n           <p>\n               <label for=\"{{ elementIdPrefix }}text\" class=\"screen-reader-text\">")
        esc_html_e("Content:")
        php_print("""</label>
        <textarea id=\"{{ elementIdPrefix }}text\" class=\"widefat text wp-editor-area\" style=\"height: 200px\" rows=\"16\" cols=\"20\"></textarea>
        </p>
        </script>
        """)
    # end def render_control_template_scripts
# end class WP_Widget_Text
