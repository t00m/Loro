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


<%
app = var['app']
topics = ', '.join(var['workbook']['topics'])
subtopics = ', '.join(var['workbook']['subtopics'])
filenames = ', '.join(var['workbook']['cache']['filenames']['data'].keys())
counter_postags = var['workbook']['stats']['counters']['postags']
postags = ', '.join(["%d %s" % (v, app.nlp.explain_term(k)) for k, v in sorted(counter_postags.items(), key=lambda x: x[0], reverse=False)])


try:
    counter_nouns = var['workbook']['stats']['counters']['LemmaByPOS']['NOUN']
    nouns_all = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_nouns.items(), key=lambda x: x[0], reverse=False)])
    nouns_common = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_nouns.most_common(10), key=lambda x: x[1], reverse=True)])
except KeyError:
    nouns_all = 'No nouns in this workbook'
    nouns_common = ''

try:
    counter_verbs = var['workbook']['stats']['counters']['LemmaByPOS']['VERB']
    verbs_all = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_verbs.items(), key=lambda x: x[0], reverse=False)])
    verbs_common = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_verbs.most_common(10), key=lambda x: x[1], reverse=True)])
except KeyError:
    verbs_all = 'No verbs in this workbook'
    verbs_common = ''

try:
    counter_adjs = var['workbook']['stats']['counters']['LemmaByPOS']['ADJ']
    adjs_all = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_adjs.items(), key=lambda x: x[0], reverse=False)])
    adjs_common = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_adjs.most_common(10), key=lambda x: x[1], reverse=True)])
except KeyError:
    adjs_all = 'No adjetives in this workbook'
    adjs_common = ''

try:
    counter_advs = var['workbook']['stats']['counters']['LemmaByPOS']['ADV']
    advs_all = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_advs.items(), key=lambda x: x[0], reverse=False)])
    advs_common = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_advs.most_common(10), key=lambda x: x[1], reverse=True)])
except KeyError:
    advs_all = 'No adverbs in this workbook'
    advs_common = ''
%>

== In this workbook

[cols="30%,70%"]
|===
| *Files*
| ${filenames}

| *Topics*
| ${topics}

| *Subtopics*
| ${subtopics}

| *Parts of the speech*
| ${postags}
|===


== Parts of the speech

=== Nouns

% if len(nouns_common) > 0:
==== Most common
${nouns_common}

==== All nouns
${nouns_all}

% else:

No nouns in this workbook

% endif


=== Verbs

% if len(verbs_common) > 0:
==== Most common
${verbs_common}

==== All verbs
${verbs_all}

% else:

No verbs in this workbook

% endif


=== Adjetives

% if len(adjs_common) > 0:
==== Most common
${adjs_common}

==== All adjetivess
${adjs_all}

% else:

No adjetives in this workbook

% endif


=== Adverbs

% if len(advs_common) > 0:
==== Most common
${advs_common}

==== All adverbs
${advs_all}

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
