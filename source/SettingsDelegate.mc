using Toybox.WatchUi as Ui;
using Toybox.System;

class SettingsDelegate extends Ui.Menu2InputDelegate {
    var reader;
    var category;
    var menu;
    var rootMenu;
    function initialize(view, kind, settingsMenu, mainMenu) {
        Menu2InputDelegate.initialize(); reader = view; category = kind;
        menu = settingsMenu; rootMenu = mainMenu;
    }

    function refreshLabels() {
        var sizes = ["Small", "Medium", "Large"];
        var n = reader.preferences.nusach;
        rootMenu.getItem(1).setSubLabel(sizes[reader.preferences.size]);
        rootMenu.getItem(2).setSubLabel(DisplayBrightness.label(reader.preferences.brightness));
        rootMenu.getItem(3).setSubLabel(n.equals("ashkenaz") ? "Ashkenaz" : n.equals("sefard") ? "Sefard (Chassidic)" : "Edot HaMizrach");
        rootMenu.getItem(4).setSubLabel(reader.preferences.screenScroll ? "By screen" : "By line");
        rootMenu.getItem(5).setSubLabel(reader.preferences.showInstructions ? "Shown" : "Hidden");
        rootMenu.getItem(6).setSubLabel(reader.preferences.fullShema ? "Shown" : "Hidden");
        if (!category.equals("main")) {
            var count = category.equals("brightness") ? 5 : 3;
            for (var i = 0; i < count; i++) {
                var entry = menu.getItem(i);
                var selected = category.equals("brightness") ? entry.getId() == reader.preferences.brightness : category.equals("sizes") ? entry.getId() == reader.preferences.size : entry.getId().equals(n);
                entry.setSubLabel(selected ? "Selected" : null);
            }
        }
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
        } else if (category.equals("brightness")) {
            reader.preferences.brightness = id;
            reader.preferences.save();
            DisplayBrightness.apply(id);
        } else if (category.equals("sizes")) {
            var anchor = reader.currentAnchor();
            reader.preferences.size = id;
            reader.preferences.save();
            reader.reload(anchor);
            reader.savePosition();
        } else if (category.equals("nusach")) {
            if (!DocumentData.available(id)) { return; }
            reader.savePosition();
            reader.preferences.nusach = id;
            reader.preferences.save();
            reader.reload(null);
            reader.savePosition();
        } else if (id.equals("sources")) {
            var sources = new SourcesView();
            Ui.pushView(sources, new SourcesDelegate(sources), Ui.SLIDE_IMMEDIATE);
        } else if (id.equals("exit")) {
            reader.savePosition();
            System.exit();
        } else if (id.equals("begin")) {
            reader.beginning();
            Ui.popView(Ui.SLIDE_IMMEDIATE);
            return;
        } else {
            var child = new Ui.Menu2({:title=>id.equals("brightness") ? "Brightness" : id.equals("sizes") ? "Text size" : "Nusach"});
            if (id.equals("brightness")) {
                for (var b = 0; b < 5; b++) {
                    child.addItem(new Ui.MenuItem(DisplayBrightness.label(b), null, b, null));
                }
                child.setFocus(reader.preferences.brightness);
            } else if (id.equals("sizes")) {
                child.addItem(new Ui.MenuItem("Small", null, 0, null));
                child.addItem(new Ui.MenuItem("Medium", null, 1, null));
                child.addItem(new Ui.MenuItem("Large", null, 2, null));
                child.setFocus(reader.preferences.size);
            } else {
                addNusach(child, "Ashkenaz", "ashkenaz");
                addNusach(child, "Sefard (Chassidic)", "sefard");
                addNusach(child, "Edot HaMizrach", "edot_hamizrach");
                child.setFocus(reader.preferences.nusach.equals("ashkenaz") ? 0 : reader.preferences.nusach.equals("sefard") ? 1 : 2);
            }
            var delegate = new SettingsDelegate(reader, id, child, rootMenu);
            delegate.refreshLabels();
            Ui.pushView(child, delegate, Ui.SLIDE_IMMEDIATE);
        }
        refreshLabels();
        Ui.requestUpdate();
    }

    function addNusach(menu, label, id) {
        menu.addItem(new Ui.MenuItem(label, DocumentData.available(id) ? null : "Text not yet verified", id, null));
    }
}
