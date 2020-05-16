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
#// Rewrite API: WP_Rewrite class
#// 
#// @package WordPress
#// @subpackage Rewrite
#// @since 1.5.0
#// 
#// 
#// Core class used to implement a rewrite component API.
#// 
#// The WordPress Rewrite class writes the rewrite module rules to the .htaccess
#// file. It also handles parsing the request to get the correct setup for the
#// WordPress Query class.
#// 
#// The Rewrite along with WP class function as a front controller for WordPress.
#// You can add rules to trigger your page view and processing using this
#// component. The full functionality of a front controller does not exist,
#// meaning you can't define how the template files load based on the rewrite
#// rules.
#// 
#// @since 1.5.0
#//
class WP_Rewrite():
    permalink_structure = Array()
    use_trailing_slashes = Array()
    author_base = "author"
    author_structure = Array()
    date_structure = Array()
    page_structure = Array()
    search_base = "search"
    search_structure = Array()
    comments_base = "comments"
    pagination_base = "page"
    comments_pagination_base = "comment-page"
    feed_base = "feed"
    comment_feed_structure = Array()
    feed_structure = Array()
    front = Array()
    root = ""
    index = "index.php"
    matches = ""
    rules = Array()
    extra_rules = Array()
    extra_rules_top = Array()
    non_wp_rules = Array()
    extra_permastructs = Array()
    endpoints = Array()
    use_verbose_rules = False
    use_verbose_page_rules = True
    rewritecode = Array("%year%", "%monthnum%", "%day%", "%hour%", "%minute%", "%second%", "%postname%", "%post_id%", "%author%", "%pagename%", "%search%")
    rewritereplace = Array("([0-9]{4})", "([0-9]{1,2})", "([0-9]{1,2})", "([0-9]{1,2})", "([0-9]{1,2})", "([0-9]{1,2})", "([^/]+)", "([0-9]+)", "([^/]+)", "([^/]+?)", "(.+)")
    queryreplace = Array("year=", "monthnum=", "day=", "hour=", "minute=", "second=", "name=", "p=", "author_name=", "pagename=", "s=")
    feeds = Array("feed", "rdf", "rss", "rss2", "atom")
    #// 
    #// Determines whether permalinks are being used.
    #// 
    #// This can be either rewrite module or permalink in the HTTP query string.
    #// 
    #// @since 1.5.0
    #// 
    #// @return bool True, if permalinks are enabled.
    #//
    def using_permalinks(self):
        
        return (not php_empty(lambda : self.permalink_structure))
    # end def using_permalinks
    #// 
    #// Determines whether permalinks are being used and rewrite module is not enabled.
    #// 
    #// Means that permalink links are enabled and index.php is in the URL.
    #// 
    #// @since 1.5.0
    #// 
    #// @return bool Whether permalink links are enabled and index.php is in the URL.
    #//
    def using_index_permalinks(self):
        
        if php_empty(lambda : self.permalink_structure):
            return False
        # end if
        #// If the index is not in the permalink, we're using mod_rewrite.
        return php_preg_match("#^/*" + self.index + "#", self.permalink_structure)
    # end def using_index_permalinks
    #// 
    #// Determines whether permalinks are being used and rewrite module is enabled.
    #// 
    #// Using permalinks and index.php is not in the URL.
    #// 
    #// @since 1.5.0
    #// 
    #// @return bool Whether permalink links are enabled and index.php is NOT in the URL.
    #//
    def using_mod_rewrite_permalinks(self):
        
        return self.using_permalinks() and (not self.using_index_permalinks())
    # end def using_mod_rewrite_permalinks
    #// 
    #// Indexes for matches for usage in preg_*() functions.
    #// 
    #// The format of the string is, with empty matches property value, '$NUM'.
    #// The 'NUM' will be replaced with the value in the $number parameter. With
    #// the matches property not empty, the value of the returned string will
    #// contain that value of the matches property. The format then will be
    #// '$MATCHES[NUM]', with MATCHES as the value in the property and NUM the
    #// value of the $number parameter.
    #// 
    #// @since 1.5.0
    #// 
    #// @param int $number Index number.
    #// @return string
    #//
    def preg_index(self, number=None):
        
        match_prefix = "$"
        match_suffix = ""
        if (not php_empty(lambda : self.matches)):
            match_prefix = "$" + self.matches + "["
            match_suffix = "]"
        # end if
        return str(match_prefix) + str(number) + str(match_suffix)
    # end def preg_index
    #// 
    #// Retrieves all page and attachments for pages URIs.
    #// 
    #// The attachments are for those that have pages as parents and will be
    #// retrieved.
    #// 
    #// @since 2.5.0
    #// 
    #// @global wpdb $wpdb WordPress database abstraction object.
    #// 
    #// @return array Array of page URIs as first element and attachment URIs as second element.
    #//
    def page_uri_index(self):
        
        global wpdb
        php_check_if_defined("wpdb")
        #// Get pages in order of hierarchy, i.e. children after parents.
        pages = wpdb.get_results(str("SELECT ID, post_name, post_parent FROM ") + str(wpdb.posts) + str(" WHERE post_type = 'page' AND post_status != 'auto-draft'"))
        posts = get_page_hierarchy(pages)
        #// If we have no pages get out quick.
        if (not posts):
            return Array(Array(), Array())
        # end if
        #// Now reverse it, because we need parents after children for rewrite rules to work properly.
        posts = array_reverse(posts, True)
        page_uris = Array()
        page_attachment_uris = Array()
        for id,post in posts:
            #// URL => page name.
            uri = get_page_uri(id)
            attachments = wpdb.get_results(wpdb.prepare(str("SELECT ID, post_name, post_parent FROM ") + str(wpdb.posts) + str(" WHERE post_type = 'attachment' AND post_parent = %d"), id))
            if (not php_empty(lambda : attachments)):
                for attachment in attachments:
                    attach_uri = get_page_uri(attachment.ID)
                    page_attachment_uris[attach_uri] = attachment.ID
                # end for
            # end if
            page_uris[uri] = id
        # end for
        return Array(page_uris, page_attachment_uris)
    # end def page_uri_index
    #// 
    #// Retrieves all of the rewrite rules for pages.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string[] Page rewrite rules.
    #//
    def page_rewrite_rules(self):
        
        #// The extra .? at the beginning prevents clashes with other regular expressions in the rules array.
        self.add_rewrite_tag("%pagename%", "(.?.+?)", "pagename=")
        return self.generate_rewrite_rules(self.get_page_permastruct(), EP_PAGES, True, True, False, False)
    # end def page_rewrite_rules
    #// 
    #// Retrieves date permalink structure, with year, month, and day.
    #// 
    #// The permalink structure for the date, if not set already depends on the
    #// permalink structure. It can be one of three formats. The first is year,
    #// month, day; the second is day, month, year; and the last format is month,
    #// day, year. These are matched against the permalink structure for which
    #// one is used. If none matches, then the default will be used, which is
    #// year, month, day.
    #// 
    #// Prevents post ID and date permalinks from overlapping. In the case of
    #// post_id, the date permalink will be prepended with front permalink with
    #// 'date/' before the actual permalink to form the complete date permalink
    #// structure.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string|false Date permalink structure on success, false on failure.
    #//
    def get_date_permastruct(self):
        
        if (php_isset(lambda : self.date_structure)):
            return self.date_structure
        # end if
        if php_empty(lambda : self.permalink_structure):
            self.date_structure = ""
            return False
        # end if
        #// The date permalink must have year, month, and day separated by slashes.
        endians = Array("%year%/%monthnum%/%day%", "%day%/%monthnum%/%year%", "%monthnum%/%day%/%year%")
        self.date_structure = ""
        date_endian = ""
        for endian in endians:
            if False != php_strpos(self.permalink_structure, endian):
                date_endian = endian
                break
            # end if
        # end for
        if php_empty(lambda : date_endian):
            date_endian = "%year%/%monthnum%/%day%"
        # end if
        #// 
        #// Do not allow the date tags and %post_id% to overlap in the permalink
        #// structure. If they do, move the date tags to $front/date/.
        #//
        front = self.front
        preg_match_all("/%.+?%/", self.permalink_structure, tokens)
        tok_index = 1
        for token in tokens[0]:
            if "%post_id%" == token and tok_index <= 3:
                front = front + "date/"
                break
            # end if
            tok_index += 1
        # end for
        self.date_structure = front + date_endian
        return self.date_structure
    # end def get_date_permastruct
    #// 
    #// Retrieves the year permalink structure without month and day.
    #// 
    #// Gets the date permalink structure and strips out the month and day
    #// permalink structures.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string|false Year permalink structure on success, false on failure.
    #//
    def get_year_permastruct(self):
        
        structure = self.get_date_permastruct()
        if php_empty(lambda : structure):
            return False
        # end if
        structure = php_str_replace("%monthnum%", "", structure)
        structure = php_str_replace("%day%", "", structure)
        structure = php_preg_replace("#/+#", "/", structure)
        return structure
    # end def get_year_permastruct
    #// 
    #// Retrieves the month permalink structure without day and with year.
    #// 
    #// Gets the date permalink structure and strips out the day permalink
    #// structures. Keeps the year permalink structure.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string|false Year/Month permalink structure on success, false on failure.
    #//
    def get_month_permastruct(self):
        
        structure = self.get_date_permastruct()
        if php_empty(lambda : structure):
            return False
        # end if
        structure = php_str_replace("%day%", "", structure)
        structure = php_preg_replace("#/+#", "/", structure)
        return structure
    # end def get_month_permastruct
    #// 
    #// Retrieves the day permalink structure with month and year.
    #// 
    #// Keeps date permalink structure with all year, month, and day.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string|false Year/Month/Day permalink structure on success, false on failure.
    #//
    def get_day_permastruct(self):
        
        return self.get_date_permastruct()
    # end def get_day_permastruct
    #// 
    #// Retrieves the permalink structure for categories.
    #// 
    #// If the category_base property has no value, then the category structure
    #// will have the front property value, followed by 'category', and finally
    #// '%category%'. If it does, then the root property will be used, along with
    #// the category_base property value.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string|false Category permalink structure on success, false on failure.
    #//
    def get_category_permastruct(self):
        
        return self.get_extra_permastruct("category")
    # end def get_category_permastruct
    #// 
    #// Retrieve the permalink structure for tags.
    #// 
    #// If the tag_base property has no value, then the tag structure will have
    #// the front property value, followed by 'tag', and finally '%tag%'. If it
    #// does, then the root property will be used, along with the tag_base
    #// property value.
    #// 
    #// @since 2.3.0
    #// 
    #// @return string|false Tag permalink structure on success, false on failure.
    #//
    def get_tag_permastruct(self):
        
        return self.get_extra_permastruct("post_tag")
    # end def get_tag_permastruct
    #// 
    #// Retrieves an extra permalink structure by name.
    #// 
    #// @since 2.5.0
    #// 
    #// @param string $name Permalink structure name.
    #// @return string|false Permalink structure string on success, false on failure.
    #//
    def get_extra_permastruct(self, name=None):
        
        if php_empty(lambda : self.permalink_structure):
            return False
        # end if
        if (php_isset(lambda : self.extra_permastructs[name])):
            return self.extra_permastructs[name]["struct"]
        # end if
        return False
    # end def get_extra_permastruct
    #// 
    #// Retrieves the author permalink structure.
    #// 
    #// The permalink structure is front property, author base, and finally
    #// '/%author%'. Will set the author_structure property and then return it
    #// without attempting to set the value again.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string|false Author permalink structure on success, false on failure.
    #//
    def get_author_permastruct(self):
        
        if (php_isset(lambda : self.author_structure)):
            return self.author_structure
        # end if
        if php_empty(lambda : self.permalink_structure):
            self.author_structure = ""
            return False
        # end if
        self.author_structure = self.front + self.author_base + "/%author%"
        return self.author_structure
    # end def get_author_permastruct
    #// 
    #// Retrieves the search permalink structure.
    #// 
    #// The permalink structure is root property, search base, and finally
    #// '/%search%'. Will set the search_structure property and then return it
    #// without attempting to set the value again.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string|false Search permalink structure on success, false on failure.
    #//
    def get_search_permastruct(self):
        
        if (php_isset(lambda : self.search_structure)):
            return self.search_structure
        # end if
        if php_empty(lambda : self.permalink_structure):
            self.search_structure = ""
            return False
        # end if
        self.search_structure = self.root + self.search_base + "/%search%"
        return self.search_structure
    # end def get_search_permastruct
    #// 
    #// Retrieves the page permalink structure.
    #// 
    #// The permalink structure is root property, and '%pagename%'. Will set the
    #// page_structure property and then return it without attempting to set the
    #// value again.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string|false Page permalink structure on success, false on failure.
    #//
    def get_page_permastruct(self):
        
        if (php_isset(lambda : self.page_structure)):
            return self.page_structure
        # end if
        if php_empty(lambda : self.permalink_structure):
            self.page_structure = ""
            return False
        # end if
        self.page_structure = self.root + "%pagename%"
        return self.page_structure
    # end def get_page_permastruct
    #// 
    #// Retrieves the feed permalink structure.
    #// 
    #// The permalink structure is root property, feed base, and finally
    #// '/%feed%'. Will set the feed_structure property and then return it
    #// without attempting to set the value again.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string|false Feed permalink structure on success, false on failure.
    #//
    def get_feed_permastruct(self):
        
        if (php_isset(lambda : self.feed_structure)):
            return self.feed_structure
        # end if
        if php_empty(lambda : self.permalink_structure):
            self.feed_structure = ""
            return False
        # end if
        self.feed_structure = self.root + self.feed_base + "/%feed%"
        return self.feed_structure
    # end def get_feed_permastruct
    #// 
    #// Retrieves the comment feed permalink structure.
    #// 
    #// The permalink structure is root property, comment base property, feed
    #// base and finally '/%feed%'. Will set the comment_feed_structure property
    #// and then return it without attempting to set the value again.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string|false Comment feed permalink structure on success, false on failure.
    #//
    def get_comment_feed_permastruct(self):
        
        if (php_isset(lambda : self.comment_feed_structure)):
            return self.comment_feed_structure
        # end if
        if php_empty(lambda : self.permalink_structure):
            self.comment_feed_structure = ""
            return False
        # end if
        self.comment_feed_structure = self.root + self.comments_base + "/" + self.feed_base + "/%feed%"
        return self.comment_feed_structure
    # end def get_comment_feed_permastruct
    #// 
    #// Adds or updates existing rewrite tags (e.g. %postname%).
    #// 
    #// If the tag already exists, replace the existing pattern and query for
    #// that tag, otherwise add the new tag.
    #// 
    #// @since 1.5.0
    #// 
    #// @see WP_Rewrite::$rewritecode
    #// @see WP_Rewrite::$rewritereplace
    #// @see WP_Rewrite::$queryreplace
    #// 
    #// @param string $tag   Name of the rewrite tag to add or update.
    #// @param string $regex Regular expression to substitute the tag for in rewrite rules.
    #// @param string $query String to append to the rewritten query. Must end in '='.
    #//
    def add_rewrite_tag(self, tag=None, regex=None, query=None):
        
        position = php_array_search(tag, self.rewritecode)
        if False != position and None != position:
            self.rewritereplace[position] = regex
            self.queryreplace[position] = query
        else:
            self.rewritecode[-1] = tag
            self.rewritereplace[-1] = regex
            self.queryreplace[-1] = query
        # end if
    # end def add_rewrite_tag
    #// 
    #// Removes an existing rewrite tag.
    #// 
    #// @since 4.5.0
    #// 
    #// @see WP_Rewrite::$rewritecode
    #// @see WP_Rewrite::$rewritereplace
    #// @see WP_Rewrite::$queryreplace
    #// 
    #// @param string $tag Name of the rewrite tag to remove.
    #//
    def remove_rewrite_tag(self, tag=None):
        
        position = php_array_search(tag, self.rewritecode)
        if False != position and None != position:
            self.rewritecode[position] = None
            self.rewritereplace[position] = None
            self.queryreplace[position] = None
        # end if
    # end def remove_rewrite_tag
    #// 
    #// Generates rewrite rules from a permalink structure.
    #// 
    #// The main WP_Rewrite function for building the rewrite rule list. The
    #// contents of the function is a mix of black magic and regular expressions,
    #// so best just ignore the contents and move to the parameters.
    #// 
    #// @since 1.5.0
    #// 
    #// @param string $permalink_structure The permalink structure.
    #// @param int    $ep_mask             Optional. Endpoint mask defining what endpoints are added to the structure.
    #// Accepts `EP_NONE`, `EP_PERMALINK`, `EP_ATTACHMENT`, `EP_DATE`, `EP_YEAR`,
    #// `EP_MONTH`, `EP_DAY`, `EP_ROOT`, `EP_COMMENTS`, `EP_SEARCH`, `EP_CATEGORIES`,
    #// `EP_TAGS`, `EP_AUTHORS`, `EP_PAGES`, `EP_ALL_ARCHIVES`, and `EP_ALL`.
    #// Default `EP_NONE`.
    #// @param bool   $paged               Optional. Whether archive pagination rules should be added for the structure.
    #// Default true.
    #// @param bool   $feed                Optional Whether feed rewrite rules should be added for the structure.
    #// Default true.
    #// @param bool   $forcomments         Optional. Whether the feed rules should be a query for a comments feed.
    #// Default false.
    #// @param bool   $walk_dirs           Optional. Whether the 'directories' making up the structure should be walked
    #// over and rewrite rules built for each in-turn. Default true.
    #// @param bool   $endpoints           Optional. Whether endpoints should be applied to the generated rewrite rules.
    #// Default true.
    #// @return string[] Array of rewrite rules keyed by their regex pattern.
    #//
    def generate_rewrite_rules(self, permalink_structure=None, ep_mask=EP_NONE, paged=True, feed=True, forcomments=False, walk_dirs=True, endpoints=True):
        
        #// Build a regex to match the feed section of URLs, something like (feed|atom|rss|rss2)/?
        feedregex2 = ""
        for feed_name in self.feeds:
            feedregex2 += feed_name + "|"
        # end for
        feedregex2 = "(" + php_trim(feedregex2, "|") + ")/?$"
        #// 
        #// $feedregex is identical but with /feed/ added on as well, so URLs like <permalink>/feed/atom
        #// and <permalink>/atom are both possible
        #//
        feedregex = self.feed_base + "/" + feedregex2
        #// Build a regex to match the trackback and page/xx parts of URLs.
        trackbackregex = "trackback/?$"
        pageregex = self.pagination_base + "/?([0-9]{1,})/?$"
        commentregex = self.comments_pagination_base + "-([0-9]{1,})/?$"
        embedregex = "embed/?$"
        #// Build up an array of endpoint regexes to append => queries to append.
        if endpoints:
            ep_query_append = Array()
            for endpoint in self.endpoints:
                #// Match everything after the endpoint name, but allow for nothing to appear there.
                epmatch = endpoint[1] + "(/(.*))?/?$"
                #// This will be appended on to the rest of the query for each dir.
                epquery = "&" + endpoint[2] + "="
                ep_query_append[epmatch] = Array(endpoint[0], epquery)
            # end for
        # end if
        #// Get everything up to the first rewrite tag.
        front = php_substr(permalink_structure, 0, php_strpos(permalink_structure, "%"))
        #// Build an array of the tags (note that said array ends up being in $tokens[0]).
        preg_match_all("/%.+?%/", permalink_structure, tokens)
        num_tokens = php_count(tokens[0])
        index = self.index
        #// Probably 'index.php'.
        feedindex = index
        trackbackindex = index
        embedindex = index
        #// 
        #// Build a list from the rewritecode and queryreplace arrays, that will look something
        #// like tagname=$matches[i] where i is the current $i.
        #//
        queries = Array()
        i = 0
        while i < num_tokens:
            
            if 0 < i:
                queries[i] = queries[i - 1] + "&"
            else:
                queries[i] = ""
            # end if
            query_token = php_str_replace(self.rewritecode, self.queryreplace, tokens[0][i]) + self.preg_index(i + 1)
            queries[i] += query_token
            i += 1
        # end while
        #// Get the structure, minus any cruft (stuff that isn't tags) at the front.
        structure = permalink_structure
        if "/" != front:
            structure = php_str_replace(front, "", structure)
        # end if
        #// 
        #// Create a list of dirs to walk over, making rewrite rules for each level
        #// so for example, a $structure of /%year%/%monthnum%/%postname% would create
        #// rewrite rules for /%year%/, /%year%/%monthnum%/ and /%year%/%monthnum%/%postname%
        #//
        structure = php_trim(structure, "/")
        dirs = php_explode("/", structure) if walk_dirs else Array(structure)
        num_dirs = php_count(dirs)
        #// Strip slashes from the front of $front.
        front = php_preg_replace("|^/+|", "", front)
        #// The main workhorse loop.
        post_rewrite = Array()
        struct = front
        j = 0
        while j < num_dirs:
            
            #// Get the struct for this dir, and trim slashes off the front.
            struct += dirs[j] + "/"
            #// Accumulate. see comment near explode('/', $structure) above.
            struct = php_ltrim(struct, "/")
            #// Replace tags with regexes.
            match = php_str_replace(self.rewritecode, self.rewritereplace, struct)
            #// Make a list of tags, and store how many there are in $num_toks.
            num_toks = preg_match_all("/%.+?%/", struct, toks)
            #// Get the 'tagname=$matches[i]'.
            query = queries[num_toks - 1] if (not php_empty(lambda : num_toks)) and (php_isset(lambda : queries[num_toks - 1])) else ""
            #// Set up $ep_mask_specific which is used to match more specific URL types.
            for case in Switch(dirs[j]):
                if case("%year%"):
                    ep_mask_specific = EP_YEAR
                    break
                # end if
                if case("%monthnum%"):
                    ep_mask_specific = EP_MONTH
                    break
                # end if
                if case("%day%"):
                    ep_mask_specific = EP_DAY
                    break
                # end if
                if case():
                    ep_mask_specific = EP_NONE
                # end if
            # end for
            #// Create query for /page/xx.
            pagematch = match + pageregex
            pagequery = index + "?" + query + "&paged=" + self.preg_index(num_toks + 1)
            #// Create query for /comment-page-xx.
            commentmatch = match + commentregex
            commentquery = index + "?" + query + "&cpage=" + self.preg_index(num_toks + 1)
            if get_option("page_on_front"):
                #// Create query for Root /comment-page-xx.
                rootcommentmatch = match + commentregex
                rootcommentquery = index + "?" + query + "&page_id=" + get_option("page_on_front") + "&cpage=" + self.preg_index(num_toks + 1)
            # end if
            #// Create query for /feed/(feed|atom|rss|rss2|rdf).
            feedmatch = match + feedregex
            feedquery = feedindex + "?" + query + "&feed=" + self.preg_index(num_toks + 1)
            #// Create query for /(feed|atom|rss|rss2|rdf) (see comment near creation of $feedregex).
            feedmatch2 = match + feedregex2
            feedquery2 = feedindex + "?" + query + "&feed=" + self.preg_index(num_toks + 1)
            #// Create query and regex for embeds.
            embedmatch = match + embedregex
            embedquery = embedindex + "?" + query + "&embed=true"
            #// If asked to, turn the feed queries into comment feed ones.
            if forcomments:
                feedquery += "&withcomments=1"
                feedquery2 += "&withcomments=1"
            # end if
            #// Start creating the array of rewrites for this dir.
            rewrite = Array()
            #// ...adding on /feed/ regexes => queries.
            if feed:
                rewrite = Array({feedmatch: feedquery, feedmatch2: feedquery2, embedmatch: embedquery})
            # end if
            #// ...and /page/xx ones.
            if paged:
                rewrite = php_array_merge(rewrite, Array({pagematch: pagequery}))
            # end if
            #// Only on pages with comments add ../comment-page-xx/.
            if EP_PAGES & ep_mask or EP_PERMALINK & ep_mask:
                rewrite = php_array_merge(rewrite, Array({commentmatch: commentquery}))
            elif EP_ROOT & ep_mask and get_option("page_on_front"):
                rewrite = php_array_merge(rewrite, Array({rootcommentmatch: rootcommentquery}))
            # end if
            #// Do endpoints.
            if endpoints:
                for regex,ep in ep_query_append:
                    #// Add the endpoints on if the mask fits.
                    if ep[0] & ep_mask or ep[0] & ep_mask_specific:
                        rewrite[match + regex] = index + "?" + query + ep[1] + self.preg_index(num_toks + 2)
                    # end if
                # end for
            # end if
            #// If we've got some tags in this dir.
            if num_toks:
                post = False
                page = False
                #// 
                #// Check to see if this dir is permalink-level: i.e. the structure specifies an
                #// individual post. Do this by checking it contains at least one of 1) post name,
                #// 2) post ID, 3) page name, 4) timestamp (year, month, day, hour, second and
                #// minute all present). Set these flags now as we need them for the endpoints.
                #//
                if php_strpos(struct, "%postname%") != False or php_strpos(struct, "%post_id%") != False or php_strpos(struct, "%pagename%") != False or php_strpos(struct, "%year%") != False and php_strpos(struct, "%monthnum%") != False and php_strpos(struct, "%day%") != False and php_strpos(struct, "%hour%") != False and php_strpos(struct, "%minute%") != False and php_strpos(struct, "%second%") != False:
                    post = True
                    if php_strpos(struct, "%pagename%") != False:
                        page = True
                    # end if
                # end if
                if (not post):
                    #// For custom post types, we need to add on endpoints as well.
                    for ptype in get_post_types(Array({"_builtin": False})):
                        if php_strpos(struct, str("%") + str(ptype) + str("%")) != False:
                            post = True
                            #// This is for page style attachment URLs.
                            page = is_post_type_hierarchical(ptype)
                            break
                        # end if
                    # end for
                # end if
                #// If creating rules for a permalink, do all the endpoints like attachments etc.
                if post:
                    #// Create query and regex for trackback.
                    trackbackmatch = match + trackbackregex
                    trackbackquery = trackbackindex + "?" + query + "&tb=1"
                    #// Create query and regex for embeds.
                    embedmatch = match + embedregex
                    embedquery = embedindex + "?" + query + "&embed=true"
                    #// Trim slashes from the end of the regex for this dir.
                    match = php_rtrim(match, "/")
                    #// Get rid of brackets.
                    submatchbase = php_str_replace(Array("(", ")"), "", match)
                    #// Add a rule for at attachments, which take the form of <permalink>/some-text.
                    sub1 = submatchbase + "/([^/]+)/"
                    #// Add trackback regex <permalink>/trackback/...
                    sub1tb = sub1 + trackbackregex
                    #// And <permalink>/feed/(atom|...)
                    sub1feed = sub1 + feedregex
                    #// And <permalink>/(feed|atom...)
                    sub1feed2 = sub1 + feedregex2
                    #// And <permalink>/comment-page-xx
                    sub1comment = sub1 + commentregex
                    #// And <permalink>/embed/...
                    sub1embed = sub1 + embedregex
                    #// 
                    #// Add another rule to match attachments in the explicit form:
                    #// <permalink>/attachment/some-text
                    #//
                    sub2 = submatchbase + "/attachment/([^/]+)/"
                    #// And add trackbacks <permalink>/attachment/trackback.
                    sub2tb = sub2 + trackbackregex
                    #// Feeds, <permalink>/attachment/feed/(atom|...)
                    sub2feed = sub2 + feedregex
                    #// And feeds again on to this <permalink>/attachment/(feed|atom...)
                    sub2feed2 = sub2 + feedregex2
                    #// And <permalink>/comment-page-xx
                    sub2comment = sub2 + commentregex
                    #// And <permalink>/embed/...
                    sub2embed = sub2 + embedregex
                    #// Create queries for these extra tag-ons we've just dealt with.
                    subquery = index + "?attachment=" + self.preg_index(1)
                    subtbquery = subquery + "&tb=1"
                    subfeedquery = subquery + "&feed=" + self.preg_index(2)
                    subcommentquery = subquery + "&cpage=" + self.preg_index(2)
                    subembedquery = subquery + "&embed=true"
                    #// Do endpoints for attachments.
                    if (not php_empty(lambda : endpoints)):
                        for regex,ep in ep_query_append:
                            if ep[0] & EP_ATTACHMENT:
                                rewrite[sub1 + regex] = subquery + ep[1] + self.preg_index(3)
                                rewrite[sub2 + regex] = subquery + ep[1] + self.preg_index(3)
                            # end if
                        # end for
                    # end if
                    #// 
                    #// Now we've finished with endpoints, finish off the $sub1 and $sub2 matches
                    #// add a ? as we don't have to match that last slash, and finally a $ so we
                    #// match to the end of the URL
                    #//
                    sub1 += "?$"
                    sub2 += "?$"
                    #// 
                    #// Post pagination, e.g. <permalink>/2
                    #// Previously: '(/[0-9]+)?/?$', which produced '/2' for page.
                    #// When cast to int, returned 0.
                    #//
                    match = match + "(?:/([0-9]+))?/?$"
                    query = index + "?" + query + "&page=" + self.preg_index(num_toks + 1)
                    pass
                else:
                    #// Close the match and finalise the query.
                    match += "?$"
                    query = index + "?" + query
                # end if
                #// 
                #// Create the final array for this dir by joining the $rewrite array (which currently
                #// only contains rules/queries for trackback, pages etc) to the main regex/query for
                #// this dir
                #//
                rewrite = php_array_merge(rewrite, Array({match: query}))
                #// If we're matching a permalink, add those extras (attachments etc) on.
                if post:
                    #// Add trackback.
                    rewrite = php_array_merge(Array({trackbackmatch: trackbackquery}), rewrite)
                    #// Add embed.
                    rewrite = php_array_merge(Array({embedmatch: embedquery}), rewrite)
                    #// Add regexes/queries for attachments, attachment trackbacks and so on.
                    if (not page):
                        #// Require <permalink>/attachment/stuff form for pages because of confusion with subpages.
                        rewrite = php_array_merge(rewrite, Array({sub1: subquery, sub1tb: subtbquery, sub1feed: subfeedquery, sub1feed2: subfeedquery, sub1comment: subcommentquery, sub1embed: subembedquery}))
                    # end if
                    rewrite = php_array_merge(Array({sub2: subquery, sub2tb: subtbquery, sub2feed: subfeedquery, sub2feed2: subfeedquery, sub2comment: subcommentquery, sub2embed: subembedquery}), rewrite)
                # end if
            # end if
            #// Add the rules for this dir to the accumulating $post_rewrite.
            post_rewrite = php_array_merge(rewrite, post_rewrite)
            j += 1
        # end while
        #// The finished rules. phew!
        return post_rewrite
    # end def generate_rewrite_rules
    #// 
    #// Generates rewrite rules with permalink structure and walking directory only.
    #// 
    #// Shorten version of WP_Rewrite::generate_rewrite_rules() that allows for shorter
    #// list of parameters. See the method for longer description of what generating
    #// rewrite rules does.
    #// 
    #// @since 1.5.0
    #// 
    #// @see WP_Rewrite::generate_rewrite_rules() See for long description and rest of parameters.
    #// 
    #// @param string $permalink_structure The permalink structure to generate rules.
    #// @param bool   $walk_dirs           Optional, default is false. Whether to create list of directories to walk over.
    #// @return array
    #//
    def generate_rewrite_rule(self, permalink_structure=None, walk_dirs=False):
        
        return self.generate_rewrite_rules(permalink_structure, EP_NONE, False, False, False, walk_dirs)
    # end def generate_rewrite_rule
    #// 
    #// Constructs rewrite matches and queries from permalink structure.
    #// 
    #// Runs the action {@see 'generate_rewrite_rules'} with the parameter that is an
    #// reference to the current WP_Rewrite instance to further manipulate the
    #// permalink structures and rewrite rules. Runs the {@see 'rewrite_rules_array'}
    #// filter on the full rewrite rule array.
    #// 
    #// There are two ways to manipulate the rewrite rules, one by hooking into
    #// the {@see 'generate_rewrite_rules'} action and gaining full control of the
    #// object or just manipulating the rewrite rule array before it is passed
    #// from the function.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string[] An associative array of matches and queries.
    #//
    def rewrite_rules(self):
        
        rewrite = Array()
        if php_empty(lambda : self.permalink_structure):
            return rewrite
        # end if
        #// robots.txt -- only if installed at the root.
        home_path = php_parse_url(home_url())
        robots_rewrite = Array({"robots\\.txt$": self.index + "?robots=1"}) if php_empty(lambda : home_path["path"]) or "/" == home_path["path"] else Array()
        #// favicon.ico -- only if installed at the root.
        favicon_rewrite = Array({"favicon\\.ico$": self.index + "?favicon=1"}) if php_empty(lambda : home_path["path"]) or "/" == home_path["path"] else Array()
        #// Old feed and service files.
        deprecated_files = Array({".*wp-(atom|rdf|rss|rss2|feed|commentsrss2)\\.php$": self.index + "?feed=old", ".*wp-app\\.php(/.*)?$": self.index + "?error=403"})
        #// Registration rules.
        registration_pages = Array()
        if is_multisite() and is_main_site():
            registration_pages[".*wp-signup.php$"] = self.index + "?signup=true"
            registration_pages[".*wp-activate.php$"] = self.index + "?activate=true"
        # end if
        #// Deprecated.
        registration_pages[".*wp-register.php$"] = self.index + "?register=true"
        #// Post rewrite rules.
        post_rewrite = self.generate_rewrite_rules(self.permalink_structure, EP_PERMALINK)
        #// 
        #// Filters rewrite rules used for "post" archives.
        #// 
        #// @since 1.5.0
        #// 
        #// @param string[] $post_rewrite Array of rewrite rules for posts, keyed by their regex pattern.
        #//
        post_rewrite = apply_filters("post_rewrite_rules", post_rewrite)
        #// Date rewrite rules.
        date_rewrite = self.generate_rewrite_rules(self.get_date_permastruct(), EP_DATE)
        #// 
        #// Filters rewrite rules used for date archives.
        #// 
        #// Likely date archives would include /yyyy/, /yyyy/mm/, and /yyyy/mm/dd/.
        #// 
        #// @since 1.5.0
        #// 
        #// @param string[] $date_rewrite Array of rewrite rules for date archives, keyed by their regex pattern.
        #//
        date_rewrite = apply_filters("date_rewrite_rules", date_rewrite)
        #// Root-level rewrite rules.
        root_rewrite = self.generate_rewrite_rules(self.root + "/", EP_ROOT)
        #// 
        #// Filters rewrite rules used for root-level archives.
        #// 
        #// Likely root-level archives would include pagination rules for the homepage
        #// as well as site-wide post feeds (e.g. /feed/, and /feed/atom/).
        #// 
        #// @since 1.5.0
        #// 
        #// @param string[] $root_rewrite Array of root-level rewrite rules, keyed by their regex pattern.
        #//
        root_rewrite = apply_filters("root_rewrite_rules", root_rewrite)
        #// Comments rewrite rules.
        comments_rewrite = self.generate_rewrite_rules(self.root + self.comments_base, EP_COMMENTS, False, True, True, False)
        #// 
        #// Filters rewrite rules used for comment feed archives.
        #// 
        #// Likely comments feed archives include /comments/feed/, and /comments/feed/atom/.
        #// 
        #// @since 1.5.0
        #// 
        #// @param string[] $comments_rewrite Array of rewrite rules for the site-wide comments feeds, keyed by their regex pattern.
        #//
        comments_rewrite = apply_filters("comments_rewrite_rules", comments_rewrite)
        #// Search rewrite rules.
        search_structure = self.get_search_permastruct()
        search_rewrite = self.generate_rewrite_rules(search_structure, EP_SEARCH)
        #// 
        #// Filters rewrite rules used for search archives.
        #// 
        #// Likely search-related archives include /search/search+query/ as well as
        #// pagination and feed paths for a search.
        #// 
        #// @since 1.5.0
        #// 
        #// @param string[] $search_rewrite Array of rewrite rules for search queries, keyed by their regex pattern.
        #//
        search_rewrite = apply_filters("search_rewrite_rules", search_rewrite)
        #// Author rewrite rules.
        author_rewrite = self.generate_rewrite_rules(self.get_author_permastruct(), EP_AUTHORS)
        #// 
        #// Filters rewrite rules used for author archives.
        #// 
        #// Likely author archives would include /author/author-name/, as well as
        #// pagination and feed paths for author archives.
        #// 
        #// @since 1.5.0
        #// 
        #// @param string[] $author_rewrite Array of rewrite rules for author archives, keyed by their regex pattern.
        #//
        author_rewrite = apply_filters("author_rewrite_rules", author_rewrite)
        #// Pages rewrite rules.
        page_rewrite = self.page_rewrite_rules()
        #// 
        #// Filters rewrite rules used for "page" post type archives.
        #// 
        #// @since 1.5.0
        #// 
        #// @param string[] $page_rewrite Array of rewrite rules for the "page" post type, keyed by their regex pattern.
        #//
        page_rewrite = apply_filters("page_rewrite_rules", page_rewrite)
        #// Extra permastructs.
        for permastructname,struct in self.extra_permastructs:
            if php_is_array(struct):
                if php_count(struct) == 2:
                    rules = self.generate_rewrite_rules(struct[0], struct[1])
                else:
                    rules = self.generate_rewrite_rules(struct["struct"], struct["ep_mask"], struct["paged"], struct["feed"], struct["forcomments"], struct["walk_dirs"], struct["endpoints"])
                # end if
            else:
                rules = self.generate_rewrite_rules(struct)
            # end if
            #// 
            #// Filters rewrite rules used for individual permastructs.
            #// 
            #// The dynamic portion of the hook name, `$permastructname`, refers
            #// to the name of the registered permastruct, e.g. 'post_tag' (tags),
            #// 'category' (categories), etc.
            #// 
            #// @since 3.1.0
            #// 
            #// @param string[] $rules Array of rewrite rules generated for the current permastruct, keyed by their regex pattern.
            #//
            rules = apply_filters(str(permastructname) + str("_rewrite_rules"), rules)
            if "post_tag" == permastructname:
                #// 
                #// Filters rewrite rules used specifically for Tags.
                #// 
                #// @since 2.3.0
                #// @deprecated 3.1.0 Use {@see 'post_tag_rewrite_rules'} instead.
                #// 
                #// @param string[] $rules Array of rewrite rules generated for tags, keyed by their regex pattern.
                #//
                rules = apply_filters_deprecated("tag_rewrite_rules", Array(rules), "3.1.0", "post_tag_rewrite_rules")
            # end if
            self.extra_rules_top = php_array_merge(self.extra_rules_top, rules)
        # end for
        #// Put them together.
        if self.use_verbose_page_rules:
            self.rules = php_array_merge(self.extra_rules_top, robots_rewrite, favicon_rewrite, deprecated_files, registration_pages, root_rewrite, comments_rewrite, search_rewrite, author_rewrite, date_rewrite, page_rewrite, post_rewrite, self.extra_rules)
        else:
            self.rules = php_array_merge(self.extra_rules_top, robots_rewrite, favicon_rewrite, deprecated_files, registration_pages, root_rewrite, comments_rewrite, search_rewrite, author_rewrite, date_rewrite, post_rewrite, page_rewrite, self.extra_rules)
        # end if
        #// 
        #// Fires after the rewrite rules are generated.
        #// 
        #// @since 1.5.0
        #// 
        #// @param WP_Rewrite $this Current WP_Rewrite instance (passed by reference).
        #//
        do_action_ref_array("generate_rewrite_rules", Array(self))
        #// 
        #// Filters the full set of generated rewrite rules.
        #// 
        #// @since 1.5.0
        #// 
        #// @param string[] $this->rules The compiled array of rewrite rules, keyed by their regex pattern.
        #//
        self.rules = apply_filters("rewrite_rules_array", self.rules)
        return self.rules
    # end def rewrite_rules
    #// 
    #// Retrieves the rewrite rules.
    #// 
    #// The difference between this method and WP_Rewrite::rewrite_rules() is that
    #// this method stores the rewrite rules in the 'rewrite_rules' option and retrieves
    #// it. This prevents having to process all of the permalinks to get the rewrite rules
    #// in the form of caching.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string[] Array of rewrite rules keyed by their regex pattern.
    #//
    def wp_rewrite_rules(self):
        
        self.rules = get_option("rewrite_rules")
        if php_empty(lambda : self.rules):
            self.matches = "matches"
            self.rewrite_rules()
            if (not did_action("wp_loaded")):
                add_action("wp_loaded", Array(self, "flush_rules"))
                return self.rules
            # end if
            update_option("rewrite_rules", self.rules)
        # end if
        return self.rules
    # end def wp_rewrite_rules
    #// 
    #// Retrieves mod_rewrite-formatted rewrite rules to write to .htaccess.
    #// 
    #// Does not actually write to the .htaccess file, but creates the rules for
    #// the process that will.
    #// 
    #// Will add the non_wp_rules property rules to the .htaccess file before
    #// the WordPress rewrite rules one.
    #// 
    #// @since 1.5.0
    #// 
    #// @return string
    #//
    def mod_rewrite_rules(self):
        
        if (not self.using_permalinks()):
            return ""
        # end if
        site_root = php_parse_url(site_url())
        if (php_isset(lambda : site_root["path"])):
            site_root = trailingslashit(site_root["path"])
        # end if
        home_root = php_parse_url(home_url())
        if (php_isset(lambda : home_root["path"])):
            home_root = trailingslashit(home_root["path"])
        else:
            home_root = "/"
        # end if
        rules = "<IfModule mod_rewrite.c>\n"
        rules += "RewriteEngine On\n"
        rules += str("RewriteBase ") + str(home_root) + str("\n")
        #// Prevent -f checks on index.php.
        rules += "RewriteRule ^index\\.php$ - [L]\n"
        #// Add in the rules that don't redirect to WP's index.php (and thus shouldn't be handled by WP at all).
        for match,query in self.non_wp_rules:
            #// Apache 1.3 does not support the reluctant (non-greedy) modifier.
            match = php_str_replace(".+?", ".+", match)
            rules += "RewriteRule ^" + match + " " + home_root + query + " [QSA,L]\n"
        # end for
        if self.use_verbose_rules:
            self.matches = ""
            rewrite = self.rewrite_rules()
            num_rules = php_count(rewrite)
            rules += "RewriteCond %{REQUEST_FILENAME} -f [OR]\n" + "RewriteCond %{REQUEST_FILENAME} -d\n" + str("RewriteRule ^.*$ - [S=") + str(num_rules) + str("]\n")
            for match,query in rewrite:
                #// Apache 1.3 does not support the reluctant (non-greedy) modifier.
                match = php_str_replace(".+?", ".+", match)
                if php_strpos(query, self.index) != False:
                    rules += "RewriteRule ^" + match + " " + home_root + query + " [QSA,L]\n"
                else:
                    rules += "RewriteRule ^" + match + " " + site_root + query + " [QSA,L]\n"
                # end if
            # end for
        else:
            rules += "RewriteCond %{REQUEST_FILENAME} !-f\n" + "RewriteCond %{REQUEST_FILENAME} !-d\n" + str("RewriteRule . ") + str(home_root) + str(self.index) + str(" [L]\n")
        # end if
        rules += "</IfModule>\n"
        #// 
        #// Filters the list of rewrite rules formatted for output to an .htaccess file.
        #// 
        #// @since 1.5.0
        #// 
        #// @param string $rules mod_rewrite Rewrite rules formatted for .htaccess.
        #//
        rules = apply_filters("mod_rewrite_rules", rules)
        #// 
        #// Filters the list of rewrite rules formatted for output to an .htaccess file.
        #// 
        #// @since 1.5.0
        #// @deprecated 1.5.0 Use the {@see 'mod_rewrite_rules'} filter instead.
        #// 
        #// @param string $rules mod_rewrite Rewrite rules formatted for .htaccess.
        #//
        return apply_filters_deprecated("rewrite_rules", Array(rules), "1.5.0", "mod_rewrite_rules")
    # end def mod_rewrite_rules
    #// 
    #// Retrieves IIS7 URL Rewrite formatted rewrite rules to write to web.config file.
    #// 
    #// Does not actually write to the web.config file, but creates the rules for
    #// the process that will.
    #// 
    #// @since 2.8.0
    #// 
    #// @param bool $add_parent_tags Optional. Whether to add parent tags to the rewrite rule sets.
    #// Default false.
    #// @return string IIS7 URL rewrite rule sets.
    #//
    def iis7_url_rewrite_rules(self, add_parent_tags=False):
        
        if (not self.using_permalinks()):
            return ""
        # end if
        rules = ""
        if add_parent_tags:
            rules += """<configuration>
            <system.webServer>
            <rewrite>
            <rules>"""
        # end if
        rules += "\n            <rule name=\"WordPress: " + esc_attr(home_url()) + """\" patternSyntax=\"Wildcard\">
        <match url=\"*\" />
        <conditions>
        <add input=\"{REQUEST_FILENAME}\" matchType=\"IsFile\" negate=\"true\" />
        <add input=\"{REQUEST_FILENAME}\" matchType=\"IsDirectory\" negate=\"true\" />
        </conditions>
        <action type=\"Rewrite\" url=\"index.php\" />
        </rule>"""
        if add_parent_tags:
            rules += """
            </rules>
            </rewrite>
            </system.webServer>
            </configuration>"""
        # end if
        #// 
        #// Filters the list of rewrite rules formatted for output to a web.config.
        #// 
        #// @since 2.8.0
        #// 
        #// @param string $rules Rewrite rules formatted for IIS web.config.
        #//
        return apply_filters("iis7_url_rewrite_rules", rules)
    # end def iis7_url_rewrite_rules
    #// 
    #// Adds a rewrite rule that transforms a URL structure to a set of query vars.
    #// 
    #// Any value in the $after parameter that isn't 'bottom' will result in the rule
    #// being placed at the top of the rewrite rules.
    #// 
    #// @since 2.1.0
    #// @since 4.4.0 Array support was added to the `$query` parameter.
    #// 
    #// @param string       $regex Regular expression to match request against.
    #// @param string|array $query The corresponding query vars for this rewrite rule.
    #// @param string       $after Optional. Priority of the new rule. Accepts 'top'
    #// or 'bottom'. Default 'bottom'.
    #//
    def add_rule(self, regex=None, query=None, after="bottom"):
        
        if php_is_array(query):
            external = False
            query = add_query_arg(query, "index.php")
        else:
            index = php_strlen(query) if False == php_strpos(query, "?") else php_strpos(query, "?")
            front = php_substr(query, 0, index)
            external = front != self.index
        # end if
        #// "external" = it doesn't correspond to index.php.
        if external:
            self.add_external_rule(regex, query)
        else:
            if "bottom" == after:
                self.extra_rules = php_array_merge(self.extra_rules, Array({regex: query}))
            else:
                self.extra_rules_top = php_array_merge(self.extra_rules_top, Array({regex: query}))
            # end if
        # end if
    # end def add_rule
    #// 
    #// Adds a rewrite rule that doesn't correspond to index.php.
    #// 
    #// @since 2.1.0
    #// 
    #// @param string $regex Regular expression to match request against.
    #// @param string $query The corresponding query vars for this rewrite rule.
    #//
    def add_external_rule(self, regex=None, query=None):
        
        self.non_wp_rules[regex] = query
    # end def add_external_rule
    #// 
    #// Adds an endpoint, like /trackback/.
    #// 
    #// @since 2.1.0
    #// @since 3.9.0 $query_var parameter added.
    #// @since 4.3.0 Added support for skipping query var registration by passing `false` to `$query_var`.
    #// 
    #// @see add_rewrite_endpoint() for full documentation.
    #// @global WP $wp Current WordPress environment instance.
    #// 
    #// @param string      $name      Name of the endpoint.
    #// @param int         $places    Endpoint mask describing the places the endpoint should be added.
    #// @param string|bool $query_var Optional. Name of the corresponding query variable. Pass `false` to
    #// skip registering a query_var for this endpoint. Defaults to the
    #// value of `$name`.
    #//
    def add_endpoint(self, name=None, places=None, query_var=True):
        
        global wp
        php_check_if_defined("wp")
        #// For backward compatibility, if null has explicitly been passed as `$query_var`, assume `true`.
        if True == query_var or None == query_var:
            query_var = name
        # end if
        self.endpoints[-1] = Array(places, name, query_var)
        if query_var:
            wp.add_query_var(query_var)
        # end if
    # end def add_endpoint
    #// 
    #// Adds a new permalink structure.
    #// 
    #// A permalink structure (permastruct) is an abstract definition of a set of rewrite rules;
    #// it is an easy way of expressing a set of regular expressions that rewrite to a set of
    #// query strings. The new permastruct is added to the WP_Rewrite::$extra_permastructs array.
    #// 
    #// When the rewrite rules are built by WP_Rewrite::rewrite_rules(), all of these extra
    #// permastructs are passed to WP_Rewrite::generate_rewrite_rules() which transforms them
    #// into the regular expressions that many love to hate.
    #// 
    #// The `$args` parameter gives you control over how WP_Rewrite::generate_rewrite_rules()
    #// works on the new permastruct.
    #// 
    #// @since 2.5.0
    #// 
    #// @param string $name   Name for permalink structure.
    #// @param string $struct Permalink structure (e.g. category/%category%)
    #// @param array  $args   {
    #// Optional. Arguments for building rewrite rules based on the permalink structure.
    #// Default empty array.
    #// 
    #// @type bool $with_front  Whether the structure should be prepended with `WP_Rewrite::$front`.
    #// Default true.
    #// @type int  $ep_mask     The endpoint mask defining which endpoints are added to the structure.
    #// Accepts `EP_NONE`, `EP_PERMALINK`, `EP_ATTACHMENT`, `EP_DATE`, `EP_YEAR`,
    #// `EP_MONTH`, `EP_DAY`, `EP_ROOT`, `EP_COMMENTS`, `EP_SEARCH`, `EP_CATEGORIES`,
    #// `EP_TAGS`, `EP_AUTHORS`, `EP_PAGES`, `EP_ALL_ARCHIVES`, and `EP_ALL`.
    #// Default `EP_NONE`.
    #// @type bool $paged       Whether archive pagination rules should be added for the structure.
    #// Default true.
    #// @type bool $feed        Whether feed rewrite rules should be added for the structure. Default true.
    #// @type bool $forcomments Whether the feed rules should be a query for a comments feed. Default false.
    #// @type bool $walk_dirs   Whether the 'directories' making up the structure should be walked over
    #// and rewrite rules built for each in-turn. Default true.
    #// @type bool $endpoints   Whether endpoints should be applied to the generated rules. Default true.
    #// }
    #//
    def add_permastruct(self, name=None, struct=None, args=Array()):
        
        #// Back-compat for the old parameters: $with_front and $ep_mask.
        if (not php_is_array(args)):
            args = Array({"with_front": args})
        # end if
        if php_func_num_args() == 4:
            args["ep_mask"] = php_func_get_arg(3)
        # end if
        defaults = Array({"with_front": True, "ep_mask": EP_NONE, "paged": True, "feed": True, "forcomments": False, "walk_dirs": True, "endpoints": True})
        args = php_array_intersect_key(args, defaults)
        args = wp_parse_args(args, defaults)
        if args["with_front"]:
            struct = self.front + struct
        else:
            struct = self.root + struct
        # end if
        args["struct"] = struct
        self.extra_permastructs[name] = args
    # end def add_permastruct
    #// 
    #// Removes a permalink structure.
    #// 
    #// @since 4.5.0
    #// 
    #// @param string $name Name for permalink structure.
    #//
    def remove_permastruct(self, name=None):
        
        self.extra_permastructs[name] = None
    # end def remove_permastruct
    #// 
    #// Removes rewrite rules and then recreate rewrite rules.
    #// 
    #// Calls WP_Rewrite::wp_rewrite_rules() after removing the 'rewrite_rules' option.
    #// If the function named 'save_mod_rewrite_rules' exists, it will be called.
    #// 
    #// @since 2.0.1
    #// 
    #// @staticvar bool $do_hard_later
    #// 
    #// @param bool $hard Whether to update .htaccess (hard flush) or just update rewrite_rules option (soft flush). Default is true (hard).
    #//
    def flush_rules(self, hard=True):
        
        flush_rules.do_hard_later = None
        #// Prevent this action from running before everyone has registered their rewrites.
        if (not did_action("wp_loaded")):
            add_action("wp_loaded", Array(self, "flush_rules"))
            flush_rules.do_hard_later = flush_rules.do_hard_later or hard if (php_isset(lambda : flush_rules.do_hard_later)) else hard
            return
        # end if
        if (php_isset(lambda : flush_rules.do_hard_later)):
            hard = flush_rules.do_hard_later
            flush_rules.do_hard_later = None
        # end if
        update_option("rewrite_rules", "")
        self.wp_rewrite_rules()
        #// 
        #// Filters whether a "hard" rewrite rule flush should be performed when requested.
        #// 
        #// A "hard" flush updates .htaccess (Apache) or web.config (IIS).
        #// 
        #// @since 3.7.0
        #// 
        #// @param bool $hard Whether to flush rewrite rules "hard". Default true.
        #//
        if (not hard) or (not apply_filters("flush_rewrite_rules_hard", True)):
            return
        # end if
        if php_function_exists("save_mod_rewrite_rules"):
            save_mod_rewrite_rules()
        # end if
        if php_function_exists("iis7_save_url_rewrite_rules"):
            iis7_save_url_rewrite_rules()
        # end if
    # end def flush_rules
    #// 
    #// Sets up the object's properties.
    #// 
    #// The 'use_verbose_page_rules' object property will be set to true if the
    #// permalink structure begins with one of the following: '%postname%', '%category%',
    #// '%tag%', or '%author%'.
    #// 
    #// @since 1.5.0
    #//
    def init(self):
        
        self.extra_rules = Array()
        self.non_wp_rules = Array()
        self.endpoints = Array()
        self.permalink_structure = get_option("permalink_structure")
        self.front = php_substr(self.permalink_structure, 0, php_strpos(self.permalink_structure, "%"))
        self.root = ""
        if self.using_index_permalinks():
            self.root = self.index + "/"
        # end if
        self.author_structure = None
        self.date_structure = None
        self.page_structure = None
        self.search_structure = None
        self.feed_structure = None
        self.comment_feed_structure = None
        self.use_trailing_slashes = "/" == php_substr(self.permalink_structure, -1, 1)
        #// Enable generic rules for pages if permalink structure doesn't begin with a wildcard.
        if php_preg_match("/^[^%]*%(?:postname|category|tag|author)%/", self.permalink_structure):
            self.use_verbose_page_rules = True
        else:
            self.use_verbose_page_rules = False
        # end if
    # end def init
    #// 
    #// Sets the main permalink structure for the site.
    #// 
    #// Will update the 'permalink_structure' option, if there is a difference
    #// between the current permalink structure and the parameter value. Calls
    #// WP_Rewrite::init() after the option is updated.
    #// 
    #// Fires the {@see 'permalink_structure_changed'} action once the init call has
    #// processed passing the old and new values
    #// 
    #// @since 1.5.0
    #// 
    #// @param string $permalink_structure Permalink structure.
    #//
    def set_permalink_structure(self, permalink_structure=None):
        
        if permalink_structure != self.permalink_structure:
            old_permalink_structure = self.permalink_structure
            update_option("permalink_structure", permalink_structure)
            self.init()
            #// 
            #// Fires after the permalink structure is updated.
            #// 
            #// @since 2.8.0
            #// 
            #// @param string $old_permalink_structure The previous permalink structure.
            #// @param string $permalink_structure     The new permalink structure.
            #//
            do_action("permalink_structure_changed", old_permalink_structure, permalink_structure)
        # end if
    # end def set_permalink_structure
    #// 
    #// Sets the category base for the category permalink.
    #// 
    #// Will update the 'category_base' option, if there is a difference between
    #// the current category base and the parameter value. Calls WP_Rewrite::init()
    #// after the option is updated.
    #// 
    #// @since 1.5.0
    #// 
    #// @param string $category_base Category permalink structure base.
    #//
    def set_category_base(self, category_base=None):
        
        if get_option("category_base") != category_base:
            update_option("category_base", category_base)
            self.init()
        # end if
    # end def set_category_base
    #// 
    #// Sets the tag base for the tag permalink.
    #// 
    #// Will update the 'tag_base' option, if there is a difference between the
    #// current tag base and the parameter value. Calls WP_Rewrite::init() after
    #// the option is updated.
    #// 
    #// @since 2.3.0
    #// 
    #// @param string $tag_base Tag permalink structure base.
    #//
    def set_tag_base(self, tag_base=None):
        
        if get_option("tag_base") != tag_base:
            update_option("tag_base", tag_base)
            self.init()
        # end if
    # end def set_tag_base
    #// 
    #// Constructor - Calls init(), which runs setup.
    #// 
    #// @since 1.5.0
    #//
    def __init__(self):
        
        self.init()
    # end def __init__
# end class WP_Rewrite
