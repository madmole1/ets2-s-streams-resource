# ets2-s-streams-resource

抓取icecast的流媒体公告板页面的MP3流资源到live_streams.sii文件中。
运行代码后上述文件将会被覆盖，并备份旧文件到后缀为运行时间的新文件中。

默认将抓取前六页内容并去重后导入。(取更多可能导致游戏的电台报错)

可直接运行打包后的ets2_catch.exe文件

Capture the MP3 stream resource from the icecast streaming media bulletin board page and save it to the `live_stream.sii` file.
After running the code, the above file will be overwritten, and the old file will be backed up to a new file with the suffix of the running time.
By default, the first six pages will be crawled, deduplicated, and imported. (Fetching more may cause errors in the game's radio station.)
