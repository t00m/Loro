<!DOCTYPE html>
<html lang="en">
<head>
    <title>${var['html']['title']}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="Loro">
    <meta name="description" content="Loro report">
    <meta name="author" content="github.com/t00m/Loro">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="keywords" content="${var['workbook']['stats']['summary']['topics']}, ${var['workbook']['stats']['summary']['subtopics']}" />
    <link rel="icon" type="image/svg+xml" href="${var['html']['favicon']}">
    <link rel="stylesheet" href="${var['html']['uikit']['css']}" />
    <link rel="stylesheet" href="${var['html']['uikit']['css_print']}" />
    <script src="${var['html']['uikit']['js']}"></script>
    <script src="${var['html']['uikit']['icon']}"></script>
</head>
<body>
    <section id="home" class="home-area" style="min-height: max(0px, 100vh);">
        <div class="uk-container">
            <div class="uk-margin-large-top">
                <h1 class="uk-text-center uk-padding-large">${var['html']['title']}</h1>
            </div>
            <div class="uk-grid-divider" uk-grid>
                <div class="uk-width-1-2@m">
                    <h3 class="uk-text-lead uk-text-center">About this workbook</h3>
                    <div>
                        <ul class="uk-list uk-list-disc">
                            <li><span class="uk-text-bold">Topics</span>: <span class="uk-text-meta">${var['workbook']['stats']['summary']['topics']}</span></li>
                            <li><span class="uk-text-bold">Subtopics</span>: <span class="uk-text-meta">${var['workbook']['stats']['summary']['subtopics']}</span></li>
                            <li><span class="uk-text-bold">Parts Of Speech</span>: <span class="uk-text-meta">${var['workbook']['stats']['summary']['postags']}</span></li>
                        </ul>
                    </div>
                </div>
                <div class="uk-width-1-2@m">
                    <h3 class="uk-text-lead uk-text-center">Translations status</h3>
                    <div class="uk-overflow-hidden">
                        <div uk-scrollspy="cls: uk-animation-slide-left; delay: 100; repeat: true; offset-top: 0; ; media: @m">
                            <h6 class="skill-title">Words translated <span class="uk-float-right">${var['workbook']['stats']['summary']['translations']['tokens']['progress_text']}</span></h6>
                            <progress id="" class="uk-progress " value="${var['workbook']['stats']['summary']['translations']['tokens']['progress_value']}" max="100"></progress>
                        </div>
                        <div uk-scrollspy="cls: uk-animation-slide-left; delay: 100; repeat: true; offset-top: 0; ; media: @m">
                            <h6 class="skill-title">Sentences translated <span class="uk-float-right">60%</span></h6>
                            <progress id="" class="uk-progress " value="60" max="100"></progress>
                        </div>
                    </div>
                </div>
                <div class="uk-width-1-1@m">
                    <div uk-grid>
                        <!-- Buttons -->
                        <div class="uk-width-1-3@m uk-text-center">
                            <a href="report.pdf"><button class="uk-button uk-button-default">Report</button></a>
                        </div>
                        <div class="uk-width-1-3@m uk-text-center">
                            <a href="workbook.html"><button class="uk-button uk-button-default">Browse</button></a>
                        </div>
                        <div class="uk-width-1-3@m uk-text-center">
                            <a href="dictionary.html"><button class="uk-button uk-button-default">Dictionary</button></a>
                        </div>
                        <!-- Buttons -->
                    </div>
                </div>
            </div>
        </div>
    </section>
</body>
</html>
