<h2>${var['lemma']['postag']}: ${var['lemma']['name']}</h2>
<p><span class="uk-text-bold">${var['lemma']['name']}</span> is the lemma for the follwing tokens:
% for token in var['lemma']['tokens']:
    <a class="uk-link-text" href="Token_${token}.html">${token}</a>
% endfor
</p>

