using Toybox.Application;
using Toybox.Lang;
using Toybox.Time;

class Preferences {
    var nusach = "ashkenaz";
    var size = 1;
    var showInstructions = false;
    var fullShema = true;
    var screenScroll = true;

    function initialize() {
        var saved = Application.Storage.getValue("preferences-v1");
        if (saved instanceof Lang.Dictionary) {
            if (saved.hasKey("showInstructions") && saved["showInstructions"] instanceof Lang.Boolean) { showInstructions = saved["showInstructions"]; }
            if (saved.hasKey("fullShema") && saved["fullShema"] instanceof Lang.Boolean) { fullShema = saved["fullShema"]; }
            if (saved.hasKey("screenScroll") && saved["screenScroll"] instanceof Lang.Boolean) { screenScroll = saved["screenScroll"]; }
            if (saved.hasKey("nusach") && saved["nusach"] instanceof Lang.String) {
                var n = saved["nusach"];
                if (n.equals("ashkenaz") || n.equals("sefard") || n.equals("edot_hamizrach")) { nusach = n; }
            }
            if (saved.hasKey("size") && saved["size"] instanceof Lang.Number && saved["size"] >= 0 && saved["size"] <= 2) {
                size = saved["size"];
            }
        }
    }

    function save() {
        Application.Storage.setValue("preferences-v1", {"nusach"=>nusach, "size"=>size,
            "showInstructions"=>showInstructions, "fullShema"=>fullShema, "screenScroll"=>screenScroll});
    }

    function positionKey(documentId) { return "position-v1-" + documentId; }

    function savePosition(documentId, offset, anchor) {
        Application.Storage.setValue(positionKey(documentId), {
            "offset"=>offset, "size"=>size, "time"=>Time.now().value(), "anchor"=>anchor,
            "showInstructions"=>showInstructions, "fullShema"=>fullShema
        });
    }

    function sameLayout(position) {
        var instructions = position.hasKey("showInstructions") ? position["showInstructions"] : true;
        var shema = position.hasKey("fullShema") ? position["fullShema"] : true;
        return position.hasKey("size") && position["size"] == size && instructions == showInstructions && shema == fullShema;
    }

    function readPosition(documentId) {
        var p = Application.Storage.getValue(positionKey(documentId));
        if (!(p instanceof Lang.Dictionary)) { return null; }
        if (!p.hasKey("time") || !(p["time"] instanceof Lang.Number)) { return null; }
        var age = Time.now().value() - p["time"];
        // Only restart boundaries evaluate the timeout. Reading/menu navigation never resets it.
        if (age < 0 || age > 2700) { return null; }
        if (!p.hasKey("offset") || !(p["offset"] instanceof Lang.Number)) { return null; }
        return p;
    }
}
