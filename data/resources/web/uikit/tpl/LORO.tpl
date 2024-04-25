<!DOCTYPE Html>
<html lang="en">
<head>
    <title></title>
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
    <div class="uk-flex uk-flex-center uk-flex-middle" style="height: 100vh;">
        <section id="home" class="home-area" style="min-height: max(0px, 100vh);">
            <div class="uk-container">
                <div class="uk-margin-large-top">
                    <h1 class="uk-text-center uk-padding-large">Ooops!</h1>
                </div>
                <div uk-grid>
                    <div class="uk-width-1-2@m">
                        <img src="${var['html']['logo']}" width="128" height="128" alt="Logo for Loro app">
                    </div>
                    <div class="uk-width-1-2@m">
                        <div class="uk-overflow-hidden">
                            <div uk-scrollspy="cls: uk-animation-slide-left; delay: 100; repeat: true; offset-top: 0; ; media: @m">
                                <h4>Please, go back to the editor and compile this workbook. Or choose another one.</h4>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </div>
</body>
</html>
