service.create("Kuerba2", "kuerba2", "video", true);
var page = require("showtime/page");
page.contents = "video";
page.appendItem("https://raw.githubusercontent.com/kuerba2/kuerba2/main/lista.m3u", "video", { title: "Kuerba2 Lista Principal" });