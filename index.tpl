<html>
    <head>
        <script src = "https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
        <script src = "https://socket.io/socket.io.js"></script>
    </head>
    <body>
        <form method="post" action="/">
            <label for="input">Enter URL</label><br>
            <input type="text" id="input" name="input"><br>
            <input type="submit" value="submit">
        </form>
        <p>Current Tournament: {{tournament}}</p>
        <a href="/downloadFile" target="blank"><button id = "btn_download">Download</button></a>
        <!-- <script type="text/javascript">
        $("#btn_download").click(function(){
            window.open('/download');
        }) -->
        </script>
    </body>
</html>
