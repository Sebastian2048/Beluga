service.create("Kueba2", "kueba2", "video", true);
var page = require("showtime/page");
page.contents = "video";
page.appendItem("https://raw.githubusercontent.com/kueba2/kueba2/main/lista.m3u", "video", { title: "Kueba2 Lista Principal" });