<h2>Token: ${var['token']['name']}</h2>
<p>
<ul class="uk-list">
    <%
        postag = var['token']['properties']['postags'][0]
        lemma = var['token']['properties']['lemmas'][0]
    %>
    <li>Lemma: <a class="uk-link-text" href="${postag}_${lemma}.html">${lemma}</a></li>
    <li>Found ${var['token']['properties']['count']} ocurrences</li>
</ul>
</p>

<p>
<ul class="uk-list">
% for key in var['token']['properties']:
    <% value = var['token']['properties'][key] %>
    <li><a class="uk-link-text" href="#">${key}: ${value}</a></li>
% endfor
</ul>
</p>

