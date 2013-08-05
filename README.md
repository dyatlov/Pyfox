Pyfox
===

Attempt to build www-page renderer fully on Python.

At this moment only CSS Parser is done.

CSS Parser output:

```
    stylesheet:
        charset
        importBlock
            import  # @import
                STRING | URI
                medialist
                    medium  # screen, handheld, monitor, print..
                    ...
        body
            page    # @page
                pseudopage  # :left, :right, :first..
                pagedeclarations
                    declaration
                        property
                        expression
                            term
                            ...
                    ...
            media   # @media
                medialist
                    medium  # print, screen, aural, braille..
                    ...
                rulesets
                    ruleset
                    ...
            ruleset # single ruleset
                selectors   # list of pathes which match ruleset
                    vector  # path to destination element
                        template    # element template: .class, #id, a:nth-child(1)..
                declarations    # list of css properties
                    declaration # property string
                        property    # property name
                        expression  # set of property values
                            term    # property value: 1px, 'content', 0, #abcdef..
                            ...
                    ...
            ...
```

Example
==

CSS:

```
#review_interview { margin-top: 0px; }

.main_simple {
    width: auto !important;
}

.main_simple .content_box_container_full {
    width: 665px !important;
}

#review_interview #review_interview_heading {
    color: #AA9984;
}

.shared_interview_container .video_list_container > .video_list_item.active_video a, .shared_interview_container .video_list_container > .video_list_item.active_video span {
    color: #0079A5;
}

.shared_interview_container .video_list_container > .video_list_item:first-child.active_video {
    border-top: 1px solid #DEDEDE;
}

.shared_interview_container .video_list_container > .video_list_item.active_video {
    border-bottom: 1px solid #DEDEDE;
}

.shared_interview_container .video_list_container > .video_list_item.highlight_top {
    border-top: 1px solid #DEDEDE;
}

.shared_interview_container .video_list_container > .video_list_item.highlight_bottom {
    border-bottom: 1px solid #DEDEDE;
}
```

Output:

```
stylesheet:
	charset:

	importblock:

	body:
		ruleset:
			selectors:
				vector:
					template:
						id:
							#review_interview
			declarations:
				declaration:
					property:
						margin-top
					expression:
						term:
							numeral:
								0px
		ruleset:
			selectors:
				vector:
					template:
						class:
							main_simple
			declarations:
				declaration:
					property:
						width
					expression:
						term:
							identifier:
								auto
					prio:
						!important
		ruleset:
			selectors:
				vector:
					template:
						class:
							main_simple
					template:
						class:
							content_box_container_full
			declarations:
				declaration:
					property:
						width
					expression:
						term:
							numeral:
								665px
					prio:
						!important
		ruleset:
			selectors:
				vector:
					template:
						id:
							#review_interview
					template:
						id:
							#review_interview_heading
			declarations:
				declaration:
					property:
						color
					expression:
						term:
							hexcolor:
								#AA9984
		ruleset:
			selectors:
				vector:
					template:
						class:
							shared_interview_container
					template:
						class:
							video_list_container
					combinator:
						>
					template:
						class:
							video_list_item
						class:
							active_video
					template:
						type:
							a
				vector:
					template:
						class:
							shared_interview_container
					template:
						class:
							video_list_container
					combinator:
						>
					template:
						class:
							video_list_item
						class:
							active_video
					template:
						type:
							span
			declarations:
				declaration:
					property:
						color
					expression:
						term:
							hexcolor:
								#0079A5
		ruleset:
			selectors:
				vector:
					template:
						class:
							shared_interview_container
					template:
						class:
							video_list_container
					combinator:
						>
					template:
						class:
							video_list_item
						:
						class:
							active_video
			declarations:
				declaration:
					property:
						border-top
					expression:
						term:
							numeral:
								1px
						term:
							identifier:
								solid
						term:
							hexcolor:
								#DEDEDE
		ruleset:
			selectors:
				vector:
					template:
						class:
							shared_interview_container
					template:
						class:
							video_list_container
					combinator:
						>
					template:
						class:
							video_list_item
						class:
							active_video
			declarations:
				declaration:
					property:
						border-bottom
					expression:
						term:
							numeral:
								1px
						term:
							identifier:
								solid
						term:
							hexcolor:
								#DEDEDE
		ruleset:
			selectors:
				vector:
					template:
						class:
							shared_interview_container
					template:
						class:
							video_list_container
					combinator:
						>
					template:
						class:
							video_list_item
						class:
							highlight_top
			declarations:
				declaration:
					property:
						border-top
					expression:
						term:
							numeral:
								1px
						term:
							identifier:
								solid
						term:
							hexcolor:
								#DEDEDE
		ruleset:
			selectors:
				vector:
					template:
						class:
							shared_interview_container
					template:
						class:
							video_list_container
					combinator:
						>
					template:
						class:
							video_list_item
						class:
							highlight_bottom
			declarations:
				declaration:
					property:
						border-bottom
					expression:
						term:
							numeral:
								1px
						term:
							identifier:
								solid
						term:
							hexcolor:
								#DEDEDE
```