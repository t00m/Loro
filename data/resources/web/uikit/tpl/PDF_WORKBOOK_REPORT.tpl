= ${var['workbook']['title']}: ${var['workbook']['description']}

:date:  ${var['timestamp']}

== In this workbook

<%
app = var['app']
topics = ', '.join(var['workbook']['topics'])
subtopics = ', '.join(var['workbook']['subtopics'])
filenames = ', '.join(var['workbook']['cache']['filenames']['data'].keys())

counter = var['workbook']['stats']['counters']['postags']

postags = ', '.join(["%d %s" % (v, app.nlp.explain_term(k)) for k, v in counter.items()])
%>

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


