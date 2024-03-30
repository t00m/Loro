<!DOCTYPE Html>
<html lang="en">
<head>
    <title>${var['html']['title']}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="Loro">
    <meta name="description" content="Loro report">
    <meta name="author" content="github.com/t00m/Loro">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="${var['html']['uikit']['css']}" />
    <link rel="stylesheet" href="${var['html']['uikit']['css_print']}" />
    <script src="${var['html']['uikit']['js']}"></script>
    <script src="${var['html']['uikit']['icon']}"></script>
</head>
<body>
<div class="uk-container">
    <div uk-grid>
        <div class="uk-width-2-3@m">
            <div class="uk-padding-large">
                <article class="uk-article">
                    <h1 class="uk-article-title" id="WORKBOOK">
                        <a class="uk-link-text" href="index.html">Workbook ${var['workbook']['id']}</h1></a>
% if var['html']['index']:
                    <p class="uk-article-meta">Workbook description</p>
                    <p class="uk-article-meta"><span class="uk-text-bolder">Topics: </span>${var['workbook']['topics']}</p>
% endif


