using Toybox.WatchUi as Ui;
using Toybox.System;

class SettingsDelegate extends Ui.Menu2InputDelegate {
    var reader;
    var category;
    function initialize(view, kind) {
        Menu2InputDelegate.initialize(); reader = view; category = kind;
    }

    function onSelect(item) {
        var id = item.getId();
        if (id.equals("instructions") || id.equals("shema") || id.equals("scrolling")) {
            var anchor = reader.currentAnchor();
            if (id.equals("instructions")) { reader.preferences.showInstructions = !reader.preferences.showInstructions; }
            if (id.equals("shema")) { reader.preferences.fullShema = !reader.preferences.fullShema; }
            if (id.equals("scrolling")) { reader.preferences.screenScroll = !reader.preferences.screenScroll; }
            reader.preferences.save();
            reader.reload(anchor);
            reader.savePosition();
            Ui.popView(Ui.SLIDE_IMMEDIATE);
        } else if (category.equals("sizes")) {
            var anchor = reader.currentAnchor();
            reader.preferences.size = id;
            reader.preferences.save();
            reader.reload(anchor);
            reader.savePosition();
            Ui.popView(Ui.SLIDE_IMMEDIATE);
        } else if (category.equals("nusach")) {
            if (!DocumentData.available(id)) { return; }
            reader.savePosition();
            reader.preferences.nusach = id;
            reader.preferences.save();
            reader.reload(null);
            reader.savePosition();
            Ui.popView(Ui.SLIDE_IMMEDIATE);
        } else if (id.equals("sources")) {
            var sources = new SourcesView();
            Ui.pushView(sources, new SourcesDelegate(sources), Ui.SLIDE_IMMEDIATE);
        } else if (id.equals("exit")) {
            reader.savePosition();
            System.exit();
        } else if (id.equals("begin")) {
            reader.beginning();
            Ui.popView(Ui.SLIDE_IMMEDIATE);
        } else {
            var menu = new Ui.Menu2({:title=>id.equals("sizes") ? "Text size" : "Nusach"});
            if (id.equals("sizes")) {
                menu.addItem(new Ui.MenuItem("Small", null, 0, null));
                menu.addItem(new Ui.MenuItem("Medium", null, 1, null));
                menu.addItem(new Ui.MenuItem("Large", null, 2, null));
            } else {
                addNusach(menu, "Ashkenaz", "ashkenaz");
                addNusach(menu, "Sefard (Chassidic)", "sefard");
                addNusach(menu, "Edot HaMizrach", "edot_hamizrach");
            }
            Ui.pushView(menu, new SettingsDelegate(reader, id), Ui.SLIDE_IMMEDIATE);
        }
        Ui.requestUpdate();
    }

    function addNusach(menu, label, id) {
        menu.addItem(new Ui.MenuItem(label, DocumentData.available(id) ? null : "Text not yet verified", id, null));
    }
}
