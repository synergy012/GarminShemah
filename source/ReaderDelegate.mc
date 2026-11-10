using Toybox.WatchUi as Ui;
using Toybox.System;

class ReaderDelegate extends Ui.BehaviorDelegate {
    var reader;
    var lastY;
    var lastDragAt = 0;

    function initialize(view) { BehaviorDelegate.initialize(); reader = view; }
    function onNextPage() { reader.advance(1); return true; }
    function onPreviousPage() { reader.advance(-1); return true; }
    // START selects items in menus; it has no scrolling action in the reader.
    function onSelect() { return true; }
    function onBack() {
        reader.savePosition();
        System.exit();
        return true;
    }

    function onSwipe(event) {
        // Some device input paths deliver a swipe after drag. Do not scroll twice.
        if (lastDragAt != 0 && System.getTimer() - lastDragAt < 400) { lastY = null; return true; }
        if (event.getDirection() == Ui.SWIPE_UP) { reader.advance(1); return true; }
        if (event.getDirection() == Ui.SWIPE_DOWN) { reader.advance(-1); return true; }
        return false;
    }

    function onTap(event) {
        lastY = null;
        return true;
    }

    function onDrag(event) {
        var y = event.getCoordinates()[1];
        var now = System.getTimer();
        if (event.getType() == Ui.DRAG_TYPE_START) { lastY = y; }
        if (lastY != null) { reader.move(lastY - y); }
        lastY = event.getType() == Ui.DRAG_TYPE_STOP ? null : y;
        lastDragAt = now;
        return true;
    }

    function onMenu() {
        var menu = new Ui.Menu2({:title=>"Reader settings"});
        menu.addItem(new Ui.MenuItem("Return to beginning", null, "begin", null));
        var sizes = ["Small", "Medium", "Large"];
        var nusach = reader.preferences.nusach;
        var nusachLabel = nusach.equals("ashkenaz") ? "Ashkenaz" : nusach.equals("sefard") ? "Sefard (Chassidic)" : "Edot HaMizrach";
        menu.addItem(new Ui.MenuItem("Text size", sizes[reader.preferences.size], "sizes", null));
        menu.addItem(new Ui.MenuItem("Nusach", nusachLabel, "nusach", null));
        menu.addItem(new Ui.MenuItem("Scrolling", reader.preferences.screenScroll ? "By screen" : "By line", "scrolling", null));
        menu.addItem(new Ui.MenuItem("Instructions", reader.preferences.showInstructions ? "Shown" : "Hidden", "instructions", null));
        menu.addItem(new Ui.MenuItem("Shema 2 + 3", reader.preferences.fullShema ? "Shown" : "Hidden", "shema", null));
        menu.addItem(new Ui.MenuItem("Close reader", null, "exit", null));
        menu.addItem(new Ui.MenuItem("Text sources", "Editions, licenses and review notes", "sources", null));
        Ui.pushView(menu, new SettingsDelegate(reader, "main"), Ui.SLIDE_IMMEDIATE);
        return true;
    }
}
