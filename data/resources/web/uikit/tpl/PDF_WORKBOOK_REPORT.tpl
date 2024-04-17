<% import pprint %>
= ${var['workbook']['title']}

:description: ${var['workbook']['description']}
:organization: ${var['workbook']['title']}
:doctype: book
:preface-title: Preface
// Settings:
:date:  ${var['timestamp']}
:experimental:
:reproducible:
:icons: font
:listing-caption: Listing
:toc:
:toclevels: 3
:xrefstyle: short
ifdef::backend-pdf[]
:pdf-theme: chronicles
:pdf-themesdir: {docdir}
:title-logo-image: image:com.github.t00m.Loro-logo.svg[pdfwidth=1.25in,align=center]
:source-highlighter: rouge
//:rouge-style: github
endif::[]
// URIs:
:url-devoxx: https://devoxx.be
:url-devoxx-top-talks: https://www.youtube.com/watch?v=1OpAgZvYXLQ&list=PLRsbF2sD7JVq7fv1GZGORShSUIae1ZAPy&index=1
:url-stbernardusabt12: http://www.sintbernardus.be/stbernardusabt12.php?l=en
:url-wolpertinger: http://en.wikipedia.org/wiki/Wolpertinger

[%notitle]
--
[abstract]
{description}
--

== In this workbook

[cols="30%,70%"]
|===
| *Files*
| ${var['workbook']['stats']['summary']['filenames']}

| *Topics*
| ${var['workbook']['stats']['summary']['topics']}

| *Subtopics*
| ${var['workbook']['stats']['summary']['subtopics']}

| *Parts of the speech*
| ${var['workbook']['stats']['summary']['postags']}
|===


== Parts of the speech

=== Nouns

% if len(var['workbook']['stats']['summary']['nouns_common']) > 0:

==== Most common
${var['workbook']['stats']['summary']['nouns_common']}

==== All nouns
${var['workbook']['stats']['summary']['nouns_all']}

% else:

No nouns in this workbook

% endif


=== Verbs

% if len(var['workbook']['stats']['summary']['verbs_common']) > 0:
==== Most common
${var['workbook']['stats']['summary']['verbs_common']}

==== All verbs
${var['workbook']['stats']['summary']['verbs_all']}

% else:

No verbs in this workbook

% endif



=== Adjetives

% if len(var['workbook']['stats']['summary']['adjs_common']) > 0:
==== Most common
${var['workbook']['stats']['summary']['adjs_common']}

==== All adjetivess
${var['workbook']['stats']['summary']['adjs_all']}

% else:

No adjetives in this workbook

% endif


=== Adverbs

% if len(var['workbook']['stats']['summary']['advs_common']) > 0:

==== Most common
${var['workbook']['stats']['summary']['advs_common']}

==== All adverbs
${var['workbook']['stats']['summary']['advs_all']}

% else:

No adverbs in this workbook

% endif

== Files in this workbook

% for filename in var['workbook']['cache']['filenames']['data'].keys():

=== ${filename}

    % for sid in var['workbook']['cache']['filenames']['data'][filename]:
        <% sentence = var['workbook']['cache']['sentences']['data'][sid]['DE'] %>
* ${sentence}
    % endfor

<<<<

% endfor


== Dictionary

<% tlcache = var['app'].translate.get_cache_tokens() %>

[cols="25%,25%,50%"]
|===
| Word | Part of Speech | Translation

% for tid in var['workbook']['cache']['tokens']['data'].keys():

<%
token = var['workbook']['cache']['tokens']['data'][tid]
postag = var['app'].nlp.explain_term(token['postag']).title()
target = var['workbook']['target']
try:
    translation = tlcache[tid][target]
except KeyError:
    translation = ''
%>
| ${token['title']}
| ${postag}
| ${translation}

% endfor
|===
